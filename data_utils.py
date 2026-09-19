import os

import pandas as pd
import plotly.express as px
import streamlit as st

from enma_palette import CHART_SEQUENCE, COLORS, FONT_BODY

DATA_PATH = "data/processed/ENMA.csv"

COLOR_DETALLE = COLORS["text_3"]


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
    st.sidebar.header("Filtros")
    return st.sidebar.empty()


def _siguiente_color() -> str:
    """Devuelve el próximo color de CHART_SEQUENCE y avanza la rotación, para que los distintos
    gráficos de barra de una misma página no salgan todos del mismo color (Plotly Express, sin una
    columna `color`, siempre usa el primer color de la secuencia para toda la serie). La rotación
    se reinicia en `iniciar_filtros`, al principio de cada página."""
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
    columna_peso: str = "peso_muestral_total",
) -> pd.DataFrame:
    """La magnitud de cada categoría se calcula como la suma del ponderador
    `columna_peso` en lugar del conteo crudo de filas, para que el porcentaje
    refleje la población estimada y no la composición de la muestra."""
    datos = df.dropna(subset=[columna])
    cantidad = datos.groupby(columna)[columna_peso].sum()
    porcentaje = cantidad.div(cantidad.sum()).mul(100).round(1)
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
    columna_peso: str = "peso_muestral_total",
):
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
            hovertemplate = (
                "%{y}<br>Porcentaje: %{x:.1f}%"
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
            hovertemplate = (
                "%{x}<br>Porcentaje: %{y:.1f}%"
                # Detalle de personas (ponderado) deshabilitado a pedido; customdata queda
                # disponible para reactivarlo agregando de nuevo el <span> con %{customdata[0]}.
                "<extra></extra>"
            )
        fig.update_traces(texttemplate="%{text}%", textposition="outside", hovertemplate=hovertemplate)
        fig.update_layout(margin=dict(t=25, b=25, l=15, r=15))
        aplicar_tipografia(fig)
        st.plotly_chart(fig, width="stretch")


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
    columna_peso: str = "peso_muestral_total",
):
    """Gráfico para preguntas de selección múltiple armonizadas en el ETL como un set de columnas
    booleanas (una por opción final, ver `construir_multiseleccion` en scripts/ETL.py): una barra
    por opción con el % ponderado de personas que la seleccionó, sobre el total de quienes
    respondieron la pregunta (no sobre la muestra completa). A diferencia de `grafico_barras`, las
    opciones no son mutuamente excluyentes: una misma persona puede sumar en más de una barra si
    marcó varias, por eso el subtítulo aclara qué representa cada porcentaje."""
    columna_base = opciones[0][0]
    with st.container(border=True, key=f"grafico_{columna_base}"):
        st.subheader(titulo)
        st.caption(subtitulo)
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
                "Porcentaje": round(cantidad / total_peso * 100, 1),
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
        hovertemplate = (
            "%{y}<br>Porcentaje: %{x:.1f}%"
            # Detalle de personas (ponderado) deshabilitado a pedido; customdata queda
            # disponible para reactivarlo agregando de nuevo el <span> con %{customdata[0]}.
            "<extra></extra>"
        )
        fig.update_traces(texttemplate="%{text}%", textposition="outside", hovertemplate=hovertemplate)
        fig.update_layout(margin=dict(t=25, b=25, l=15, r=15))
        aplicar_tipografia(fig)
        st.plotly_chart(fig, width="stretch")
