import os

import pandas as pd
import plotly.express as px
import streamlit as st

from enma_palette import CHART_SEQUENCE, COLORS, FONT_BODY

DATA_PATH = "data/processed/ENMA.csv"

COLOR_DETALLE = COLORS["text_3"]

# Ponderadores muestrales (no son intercambiables, ver la documentación de cada base):
# - General (weightvec en 2023 / pesos_para_estimaciones_totales en 2020): para todo lo que no es
#   la distribución de una variable dentro de una nacionalidad (fila de población total, cruces que
#   no son por nacionalidad, composición por país de origen).
# - Intra nacionalidad (weightvec_0 en 2023 / pesos_para_estimaciones_por_nacionalidad en 2020):
#   para ver una variable dentro de cada nacionalidad. Se aplica a todas las filas por país, aunque
#   solo diez nacionalidades tienen un ajuste propio (ver la nota metodológica del README).
PESO_TOTAL = "peso_muestral_total"
PESO_NACIONALIDAD = "peso_muestral_nacionalidad"


# Etiquetas de las categorías del eje un punto más grandes que el tamaño por defecto de Plotly (12),
# y % de las barras en negrita, en todos los gráficos de barras.
TAMANIO_EJE_CATEGORIAS = 13
TEXTO_PORCENTAJE_ENTERO = "<b>%{text:.0f}%</b>"


# Dimensiones de cruce que se eligen en el panel lateral de las secciones (ver `filtro_cruce`).
SIN_CRUCE = "Sin cruce"
POBLACION_TOTAL_LABEL = "Población migrante total"
PERIODO_RESIDENCIA_ORDEN = ["Hasta 5 años", "Entre 5 y 9 años", "Más de 10 años"]
# "Sin clasificar" (57 casos de 2020 de Provincia de Buenos Aires sin localidad asignable) no es una
# región: no se muestra como fila del cruce, pero cuenta en la fila de Población migrante total.
REGIONES_ORDEN = ["AMBA", "Región Pampeana", "Cuyo", "NEA", "NOA", "Patagonia"]
CRUCES = {
    # País de origen: cada país con el ponderador intra nacionalidad y la fila de población total
    # con el general, como en la página sociodemográfica.
    "País de origen": dict(
        columna="pais_nacimiento_var", nombre="país de origen", total=POBLACION_TOTAL_LABEL,
        peso_filas=PESO_NACIONALIDAD,
        nota="Países ponderados por nacionalidad; Población migrante total ponderada con el ponderador general",
    ),
    "Tiempo de residencia": dict(
        columna="periodo_residencia", nombre="tiempo de residencia", total=POBLACION_TOTAL_LABEL,
        peso_filas=PESO_TOTAL, orden=PERIODO_RESIDENCIA_ORDEN,
        nota="Datos ponderados con el ponderador general",
        fuera="sin dato de tiempo de residencia",
    ),
    "Región": dict(
        columna="region", nombre="región de residencia", total=POBLACION_TOTAL_LABEL,
        peso_filas=PESO_TOTAL, orden=REGIONES_ORDEN,
        nota="Datos ponderados con el ponderador general",
        fuera="de Provincia de Buenos Aires sin región asignable (\"Sin clasificar\")",
    ),
}

# Gráficos cruzados: etiquetas de las filas (categorías del cruce) en 10, % en negrita con 1
# decimal, y detalle flotante sin el nombre de la categoría (ya está en la leyenda).
TAMANIO_EJE_CRUCE = 10
TEXTO_PORCENTAJE_DECIMAL = "<b>%{text:.1f}%</b>"
NOTA_RESPUESTA_MULTIPLE = "**Respuesta múltiple: los % no suman 100.**"


def formatear_n(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def nota_ponderacion(n: int, texto_ponderador: str = "Datos ponderados con el ponderador general"):
    """Nota al pie de cada gráfico: ponderador usado y N (casos sin ponderar que entran en el
    gráfico, es decir, quienes tienen dato en la variable graficada)."""
    st.caption(f"{texto_ponderador}. N = {formatear_n(n)}")


def aplicar_tipografia(fig):
    """DM Sans en negro puro para todos los textos del gráfico. El título va aparte, vía
    st.subheader (que ya hereda Syncopate del CSS global de la app), no como título nativo de Plotly."""
    fig.update_layout(
        font=dict(family=FONT_BODY, color="#000000"),
        legend=dict(font=dict(family=FONT_BODY, color="#000000")),
        hoverlabel=dict(font=dict(family=FONT_BODY, color="#000000")),
    )
    fig.update_xaxes(title_font=dict(family=FONT_BODY, color="#000000"), tickfont=dict(family=FONT_BODY, color="#000000"))
    fig.update_yaxes(title_font=dict(family=FONT_BODY, color="#000000"), tickfont=dict(family=FONT_BODY, color="#000000"))
    return fig


@st.cache_data
def _leer_datos(_mtime: float) -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


def load_data() -> pd.DataFrame:
    """`st.cache_data` cachea por código + argumentos, no por el contenido del archivo: si
    ENMA.csv cambia (nuevo commit) pero el proceso de Streamlit sigue "caliente" (no se reinició),
    sin este truco seguiría sirviendo el CSV viejo cacheado. Pasar la fecha de modificación del
    archivo como argumento oculto hace que la key de cache cambie sola cada vez que el CSV se
    actualiza, sin depender de un reinicio manual."""
    return _leer_datos(os.path.getmtime(DATA_PATH))


def iniciar_filtros() -> "st.delta_generator.DeltaGenerator":
    """Encabezado del panel de filtros de la página + placeholder para el contador
    de encuestados (se completa recién en aplicar_filtros, una vez armada la máscara).
    También reinicia la rotación de colores de los gráficos (ver `_siguiente_color`), para que
    cada página vuelva a empezar por el primer color de la paleta en su primer gráfico."""
    st.session_state["_color_index"] = 0
    st.session_state["_cruce"] = None
    st.sidebar.header("Filtros")
    return st.sidebar.empty()


def _siguiente_color() -> str:
    """Devuelve el próximo color de CHART_SEQUENCE y avanza la rotación un lugar. Todas las
    barras de un mismo gráfico comparten ese único color (Plotly, sin una columna `color`, ya
    pinta toda la serie de un solo color); lo que rota es el color ENTRE gráficos, para que los
    distintos gráficos de barra de una misma página no salgan todos naranja. La rotación se
    reinicia en `iniciar_filtros`, al principio de cada página."""
    indice = st.session_state.get("_color_index", 0)
    st.session_state["_color_index"] = indice + 1
    return CHART_SEQUENCE[indice % len(CHART_SEQUENCE)]


def filtro_edicion(df: pd.DataFrame, key: str, reset_keys: list[str] | None = None) -> pd.Series:
    """Selector de Año. Si se pasan `reset_keys`, al cambiar de año se incrementa
    la "versión" de esos otros widgets (p. ej. el filtro de nacionalidad). Un
    widget de Streamlit conserva su selección en el navegador mientras
    conserve su `key`, aunque el script borre esa entrada de session_state
    (el propio frontend reenvía el último valor elegido en cada rerun); la
    única forma confiable de que vuelva a mostrar todas sus opciones es
    darle una key nueva, forzando una instancia nueva del widget. Ver
    `version_key()`."""
    anios = sorted(df["Año"].dropna().unique())
    seleccion = st.sidebar.selectbox("Edición / Año", anios, key=key)
    anio_previo_key = f"_{key}_anio_previo"
    anio_previo = st.session_state.get(anio_previo_key)
    if reset_keys and anio_previo is not None and anio_previo != seleccion:
        for reset_key in reset_keys:
            version_key = f"_{reset_key}_version"
            st.session_state[version_key] = st.session_state.get(version_key, 0) + 1
    st.session_state[anio_previo_key] = seleccion
    return df["Año"] == seleccion


def version_key(key: str) -> str:
    """Key efectiva de un widget versionado por `filtro_edicion` (ver ahí):
    cambia cuando se le pide resetear, lo que fuerza a Streamlit a tratarlo
    como un widget nuevo en el navegador en vez de arrastrar la selección
    previa."""
    return f"{key}_{st.session_state.get(f'_{key}_version', 0)}"


def filtro_nacionalidad(df: pd.DataFrame, key: str, df_opciones: pd.DataFrame | None = None) -> pd.Series:
    """`df_opciones` permite calcular las opciones del multiselect sobre un
    subconjunto (p. ej. ya filtrado por año) sin restringir el propio `df`
    usado para armar la máscara. `key` es la key lógica del filtro; la key
    real del widget se versiona (ver `version_key`) para poder resetearlo
    desde `filtro_edicion`."""
    fuente = df_opciones if df_opciones is not None else df
    nacionalidades = sorted(fuente["pais_nacimiento_var"].dropna().unique())
    seleccion = st.sidebar.multiselect("Nacionalidad", nacionalidades, default=nacionalidades, key=version_key(key))
    return df["pais_nacimiento_var"].isin(seleccion)


def filtro_genero(df: pd.DataFrame, key: str) -> pd.Series:
    generos = sorted(df["genero_agrup"].dropna().unique())
    seleccion = st.sidebar.multiselect("Género", generos, default=generos, key=key)
    return df["genero_agrup"].isin(seleccion)


def filtro_edad(df: pd.DataFrame, key: str) -> pd.Series:
    edades = sorted(df["edad_agrupada"].dropna().unique())
    seleccion = st.sidebar.multiselect("Edades", edades, default=edades, key=key)
    return df["edad_agrupada"].isin(seleccion)


def filtro_region(df: pd.DataFrame, key: str) -> pd.Series:
    regiones = sorted(df["region"].dropna().unique())
    seleccion = st.sidebar.multiselect("Región", regiones, default=regiones, key=key)
    return df["region"].isin(seleccion)


def filtro_cruce(df: pd.DataFrame, key: str) -> dict | None:
    """Selector de la dimensión de cruce de la sección. Recibe `df` ya filtrado por año, para fijar
    el orden de las filas una sola vez (igual en todos los gráficos de la página). Guarda el cruce
    elegido en session_state, de donde lo leen `grafico_barras` y `grafico_multiseleccion` (se
    reinicia en `iniciar_filtros`, así las páginas sin este selector no cruzan)."""
    eleccion = st.sidebar.selectbox("Cruzar por", [SIN_CRUCE, *CRUCES], key=key)
    if eleccion == SIN_CRUCE:
        st.session_state["_cruce"] = None
        return None
    cruce = dict(CRUCES[eleccion])
    if "orden" in cruce:
        filas = [c for c in cruce["orden"] if c in set(df[cruce["columna"]].dropna())]
    else:
        # Países de menor a mayor cantidad de casos, como en la página sociodemográfica.
        filas = df.groupby(cruce["columna"])[PESO_NACIONALIDAD].sum().sort_values().index.tolist()
    cruce["filas"] = [cruce["total"]] + filas
    st.session_state["_cruce"] = cruce
    return cruce


def _titulo_cruzado(titulo: str, cruce: dict) -> str:
    """"Distribución por X" -> "X según <dimensión>" (el resto de los títulos solo suma "según ...")."""
    prefijo = "Distribución por "
    if titulo.startswith(prefijo):
        titulo = titulo[len(prefijo):]
        titulo = titulo[0].upper() + titulo[1:]
    return f"{titulo} según {cruce['nombre']}"


def _ponderados_por_fila(df: pd.DataFrame, cruce: dict, valores) -> dict:
    """Aplica `valores(sub_df, columna_peso)` a cada fila del cruce: la de total sobre todo `df`
    con el ponderador general y cada categoría sobre su subconjunto con el ponderador de la
    dimensión. Devuelve {fila: resultado}, sin las filas que quedan vacías."""
    resultado = {}
    for fila in cruce["filas"]:
        if fila == cruce["total"]:
            sub, peso = df, PESO_TOTAL
        else:
            sub, peso = df[df[cruce["columna"]] == fila], cruce["peso_filas"]
        if not sub.empty and sub[peso].sum():
            resultado[fila] = valores(sub, peso)
    return resultado


def _nota_cruce(datos: pd.DataFrame, cruce: dict):
    """Nota al pie de los gráficos cruzados: ponderador, casos que cuentan en la fila de total pero
    no en ninguna categoría del cruce (si los hay) y N."""
    categorias = [f for f in cruce["filas"] if f != cruce["total"]]
    fuera = int((~datos[cruce["columna"]].isin(categorias)).sum())
    texto = cruce["nota"]
    if fuera and cruce.get("fuera"):
        texto += (
            f". {formatear_n(fuera)} casos {cruce['fuera']} cuentan en {cruce['total']} "
            "pero no se muestran por separado"
        )
    nota_ponderacion(len(datos), texto)


def _ejes_cruce(fig, filas: list, total: str | None):
    """Filas del cruce en el eje Y, en el orden de `filas` de arriba hacia abajo (Plotly dibuja la
    primera categoría abajo, por eso se invierte) y con la fila de total en negrita."""
    fig.update_yaxes(
        categoryorder="array", categoryarray=filas[::-1],
        tickmode="array", tickvals=filas, ticktext=[f"<b>{f}</b>" if f == total else f for f in filas],
        tickfont=dict(size=TAMANIO_EJE_CRUCE), title=None,
    )


def _grafico_cruce_simple(df, columna, titulo, orden, cruce):
    """Pregunta de respuesta única cruzada: barras apiladas al 100% (una fila por categoría del
    cruce), con el valor sin redondear en la barra (cada fila suma 100%) y la etiqueta con 1
    decimal, como "Composición por género según país de origen"."""
    with st.container(border=True, key=f"grafico_{columna}"):
        st.subheader(_titulo_cruzado(titulo, cruce))
        datos = df.dropna(subset=[columna])
        distribuciones = _ponderados_por_fila(
            datos, cruce,
            lambda sub, peso: sub.groupby(columna)[peso].sum().pipe(lambda c: c / c.sum() * 100),
        )
        if not distribuciones:
            st.info("Sin datos para este filtro.")
            return
        tabla = pd.DataFrame(distribuciones).T.fillna(0)
        if orden:
            categorias = [c for c in orden if c in tabla.columns]
        else:
            categorias = datos.groupby(columna)[PESO_TOTAL].sum().sort_values(ascending=False).index.tolist()
        filas = list(tabla.index)
        data = tabla.reset_index(names="Fila").melt(id_vars="Fila", var_name="Categoría", value_name="Porcentaje")
        colores = {c: CHART_SEQUENCE[i % len(CHART_SEQUENCE)] for i, c in enumerate(categorias)}
        fig = px.bar(
            data, x="Porcentaje", y="Fila", color="Categoría", orientation="h", barmode="stack",
            category_orders={"Categoría": categorias}, color_discrete_map=colores, text="Porcentaje",
        )
        fig.update_traces(
            texttemplate=TEXTO_PORCENTAJE_DECIMAL, textposition="inside", cliponaxis=False,
            hovertemplate="%{y}<br>Porcentaje: %{x:.1f}%<extra></extra>",
        )
        fig.update_layout(
            xaxis_title=None,
            legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0, title_text=None),
            margin=dict(t=10, b=10, l=10, r=30),
        )
        fig.update_xaxes(range=[0, 101], tickvals=[0, 25, 50, 75, 100], ticktext=["0%", "25%", "50%", "75%", "100%"])
        aplicar_tipografia(fig)
        _ejes_cruce(fig, filas, cruce["total"])
        st.plotly_chart(fig, width="stretch")
        _nota_cruce(datos, cruce)


def _grafico_cruce_multiple(df, opciones, titulo, subtitulo, cruce):
    """Pregunta de respuesta múltiple cruzada: tabla de calor con una fila por opción y una columna
    por categoría del cruce (la de total primera y en negrita). Cada celda es el % ponderado de
    quienes respondieron la pregunta en esa categoría que marcó la opción; las opciones no son
    excluyentes, así que los % de una columna no suman 100."""
    columnas = [c for c, _ in opciones]
    with st.container(border=True, key=f"grafico_{columnas[0]}"):
        st.subheader(_titulo_cruzado(titulo, cruce))
        st.caption(f"{NOTA_RESPUESTA_MULTIPLE} {subtitulo}")
        respondieron = df[df[columnas].notna().any(axis=1)]

        def porcentajes(sub, peso):
            return {
                etiqueta: (_a_binario(sub[columna]) * sub[peso]).sum() / sub.loc[sub[columna].notna(), peso].sum() * 100
                for columna, etiqueta in opciones if sub[columna].notna().any()
            }

        tabla = pd.DataFrame(_ponderados_por_fila(respondieron, cruce, porcentajes))
        if tabla.empty:
            st.info("Sin datos para este filtro.")
            return
        tabla = tabla.loc[[e for _, e in opciones if e in tabla.index]]
        # La escala de color va de 0 al % más alto de la tabla (no hasta 100%), para que las
        # diferencias se vean aunque todos los valores sean bajos. El tope es el naranja de la
        # paleta con un poco de transparencia, así ni la celda máxima queda en el color pleno.
        naranja = COLORS["orange_1"].lstrip("#")
        r, g, b = (int(naranja[i:i + 2], 16) for i in (0, 2, 4))
        fig = px.imshow(
            tabla, aspect="auto", zmin=0, zmax=max(tabla.max().max(), 1),
            color_continuous_scale=[f"rgba({r},{g},{b},0)", f"rgba({r},{g},{b},0.8)"],
        )
        fig.update_traces(
            texttemplate="<b>%{z:.1f}%</b>", textfont=dict(size=TAMANIO_EJE_CRUCE),
            hovertemplate="%{x}<br>%{y}: %{z:.1f}%<extra></extra>",
        )
        fig.update_layout(coloraxis_showscale=False, margin=dict(t=10, b=10, l=10, r=10))
        aplicar_tipografia(fig)
        fig.update_xaxes(
            side="top", title=None, tickangle=-30, tickfont=dict(size=TAMANIO_EJE_CRUCE),
            tickmode="array", tickvals=list(tabla.columns),
            ticktext=[f"<b>{c}</b>" if c == cruce["total"] else c for c in tabla.columns],
        )
        fig.update_yaxes(title=None, tickfont=dict(size=TAMANIO_EJE_CRUCE))
        st.plotly_chart(fig, width="stretch")
        _nota_cruce(respondieron, cruce)


def aplicar_filtros(df: pd.DataFrame, mask: pd.Series, contador) -> pd.DataFrame:
    """Filtra df con la máscara combinada de la página, actualiza el contador de
    encuestados (en el placeholder reservado por iniciar_filtros) y frena la
    ejecución si el cruce de filtros no deja ningún registro."""
    df_filtrado = df[mask]
    contador.caption(f"{len(df_filtrado):,}".replace(",", ".") + " personas encuestadas")
    if df_filtrado.empty:
        st.warning("No hay datos para los filtros seleccionados.")
        st.stop()
    return df_filtrado


def distribucion(
    df: pd.DataFrame,
    columna: str,
    orden: list | None = None,
    columna_peso: str = PESO_TOTAL,
) -> pd.DataFrame:
    """La magnitud de cada categoría se calcula como la suma del ponderador
    `columna_peso` en lugar del conteo crudo de filas, para que el porcentaje
    refleje la población estimada y no la composición de la muestra."""
    datos = df.dropna(subset=[columna])
    cantidad = datos.groupby(columna)[columna_peso].sum()
    porcentaje = cantidad.div(cantidad.sum()).mul(100).round(0)
    if orden:
        indice = [c for c in orden if c in cantidad.index]
    else:
        indice = porcentaje.sort_values(ascending=False).index
    data = pd.DataFrame({
        columna: indice,
        "Porcentaje": porcentaje.reindex(indice).values,
        "Cantidad": cantidad.reindex(indice).values,
    })
    return data


def grafico_barras(
    df: pd.DataFrame,
    columna: str,
    titulo: str,
    orden: list | None = None,
    horizontal: bool = False,
    columna_peso: str = PESO_TOTAL,
):
    """Sin cruce: distribución de frecuencias en barras de un solo color, con % enteros. Con un
    cruce elegido en el panel lateral (`filtro_cruce`): barras apiladas al 100% por categoría del
    cruce (ver `_grafico_cruce_simple`)."""
    cruce = st.session_state.get("_cruce")
    if cruce:
        _grafico_cruce_simple(df, columna, titulo, orden, cruce)
        return
    with st.container(border=True, key=f"grafico_{columna}"):
        st.subheader(titulo)
        data = distribucion(df, columna, orden, columna_peso=columna_peso)
        if data.empty:
            st.info("Sin datos para este filtro.")
            return
        color = _siguiente_color()
        if horizontal:
            data = data.iloc[::-1]
            fig = px.bar(
                data, x="Porcentaje", y=columna, orientation="h",
                color_discrete_sequence=[color], text="Porcentaje",
                custom_data=["Cantidad"],
            )
            fig.update_layout(yaxis_title=None, xaxis_title="Porcentaje (%)")
            fig.update_xaxes(range=[0, data["Porcentaje"].max() * 1.18])
            fig.update_yaxes(tickfont=dict(size=TAMANIO_EJE_CATEGORIAS))
            hovertemplate = (
                "%{y}<br>Porcentaje: %{x:.0f}%"
                # Detalle de personas (ponderado) deshabilitado a pedido; customdata queda
                # disponible para reactivarlo agregando de nuevo el <span> con %{customdata[0]}.
                "<extra></extra>"
            )
        else:
            fig = px.bar(
                data, x=columna, y="Porcentaje",
                color_discrete_sequence=[color], text="Porcentaje",
                custom_data=["Cantidad"],
            )
            fig.update_layout(xaxis_title=None, yaxis_title="Porcentaje (%)")
            fig.update_yaxes(range=[0, data["Porcentaje"].max() * 1.3])
            fig.update_xaxes(tickfont=dict(size=TAMANIO_EJE_CATEGORIAS))
            hovertemplate = (
                "%{x}<br>Porcentaje: %{y:.0f}%"
                # Detalle de personas (ponderado) deshabilitado a pedido; customdata queda
                # disponible para reactivarlo agregando de nuevo el <span> con %{customdata[0]}.
                "<extra></extra>"
            )
        fig.update_traces(texttemplate=TEXTO_PORCENTAJE_ENTERO, textposition="outside", hovertemplate=hovertemplate)
        fig.update_layout(margin=dict(t=25, b=25, l=15, r=15))
        aplicar_tipografia(fig)
        st.plotly_chart(fig, width="stretch")
        nota_ponderacion(int(df[columna].notna().sum()))


def _a_binario(serie: pd.Series) -> pd.Series:
    """Normaliza a 0.0/1.0/NaN una columna booleana ponderable armada por `construir_multiseleccion`
    en el ETL. Al guardarse y releerse desde CSV, True/False pueden volver como bool de Python,
    como texto ("True"/"False") o, si pandas ya los infirió como booleanos puros, como su propio
    dtype; `.astype(float)` a secas rompe con cualquiera de las variantes de texto."""
    return pd.to_numeric(
        serie.replace({True: 1, False: 0, "True": 1, "False": 0}),
        errors="coerce",
    )


def grafico_multiseleccion(
    df: pd.DataFrame,
    opciones: list[tuple[str, str]],
    titulo: str,
    subtitulo: str,
    columna_peso: str = PESO_TOTAL,
):
    """Gráfico para preguntas de selección múltiple armonizadas en el ETL como un set de columnas
    booleanas (una por opción final, ver `construir_multiseleccion` en scripts/ETL.py): una barra
    por opción con el % ponderado de personas que la seleccionó, sobre el total de quienes
    respondieron la pregunta (no sobre la muestra completa). A diferencia de `grafico_barras`, las
    opciones no son mutuamente excluyentes: una misma persona puede sumar en más de una barra si
    marcó varias, por eso el subtítulo aclara qué representa cada porcentaje."""
    cruce = st.session_state.get("_cruce")
    if cruce:
        _grafico_cruce_multiple(df, opciones, titulo, subtitulo, cruce)
        return
    columna_base = opciones[0][0]
    with st.container(border=True, key=f"grafico_{columna_base}"):
        st.subheader(titulo)
        st.caption(f"{NOTA_RESPUESTA_MULTIPLE} {subtitulo}")
        filas = []
        for columna, etiqueta in opciones:
            datos = df.dropna(subset=[columna])
            if datos.empty:
                continue
            seleccionado = _a_binario(datos[columna])
            peso = datos[columna_peso]
            total_peso = peso.sum()
            if not total_peso:
                continue
            cantidad = (seleccionado * peso).sum()
            filas.append({
                "Opción": etiqueta,
                "Porcentaje": round(cantidad / total_peso * 100),
                "Cantidad": round(cantidad),
            })
        if not filas:
            st.info("Sin datos para este filtro.")
            return
        data = pd.DataFrame(filas).sort_values("Porcentaje", ascending=True)
        fig = px.bar(
            data, x="Porcentaje", y="Opción", orientation="h",
            color_discrete_sequence=[_siguiente_color()], text="Porcentaje",
            custom_data=["Cantidad"],
        )
        fig.update_layout(yaxis_title=None, xaxis_title="Porcentaje (%)")
        fig.update_xaxes(range=[0, data["Porcentaje"].max() * 1.18])
        fig.update_yaxes(tickfont=dict(size=TAMANIO_EJE_CATEGORIAS))
        hovertemplate = (
            "%{y}<br>Porcentaje: %{x:.0f}%"
            # Detalle de personas (ponderado) deshabilitado a pedido; customdata queda
            # disponible para reactivarlo agregando de nuevo el <span> con %{customdata[0]}.
            "<extra></extra>"
        )
        fig.update_traces(texttemplate=TEXTO_PORCENTAJE_ENTERO, textposition="outside", hovertemplate=hovertemplate)
        fig.update_layout(margin=dict(t=25, b=25, l=15, r=15))
        aplicar_tipografia(fig)
        st.plotly_chart(fig, width="stretch")
        nota_ponderacion(int(df[[c for c, _ in opciones]].notna().any(axis=1).sum()))
