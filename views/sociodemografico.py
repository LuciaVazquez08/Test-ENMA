import plotly.express as px
import streamlit as st

from data_utils import (
    PESO_NACIONALIDAD,
    PESO_TOTAL,
    TAMANIO_EJE_CATEGORIAS,
    TEXTO_PORCENTAJE_ENTERO,
    aplicar_filtros,
    aplicar_tipografia,
    formatear_n,
    filtro_edicion,
    iniciar_filtros,
    load_data,
    nota_ponderacion,
)
from enma_palette import CHART_SEQUENCE, COLORS

PERIODO_RESIDENCIA_ORDEN = ["Hasta 5 años", "Entre 5 y 9 años", "Más de 10 años"]

POBLACION_TOTAL_LABEL = "Población migrante total"

DESCENDENCIA_ORDEN = ["Afrodescendiente", "Descendencia Asiática", "Descendencia Indígena", "Ninguna de las anteriores"]
DESCENDENCIA_SIN_GRAFICAR = ["Ninguna de las anteriores"]

# Orden fijo de las lenguas (igual en ambas ediciones), con "Otro" al final, y un color de la paleta
# para cada una (gris para "Otro").
IDIOMA_ORDEN = [
    "Español / Castellano", "Guaraní", "Portugués", "Quechua",
    "Creole haitiano", "Wolof", "Francés", "Otro",
]
IDIOMA_COLORES = dict(zip(IDIOMA_ORDEN, CHART_SEQUENCE))

# Orden fijo de las categorías de género (leyenda y apilado) y su etiqueta en los gráficos.
GENERO_ETIQUETAS = {
    "Mujer": "Mujer",
    "Varón": "Varón",
    "Otro género": "Otro",
    "Prefiero no responder": "Prefiero no contestar",
}
GENERO_ORDEN = list(GENERO_ETIQUETAS.values())
# En los gráficos según país de origen, la fila Población migrante total usa los mismos colores que
# los países; se distingue por ir primera y en negrita en el eje Y.
COLORES_CATEGORIAS = [COLORS["orange_1"], COLORS["blue"], COLORS["yellow_1"], COLORS["blue_pale"]]
GENERO_COLORES = dict(zip(GENERO_ORDEN, COLORES_CATEGORIAS))

# Etiquetas del eje Y (países) y de los % en negrita, un punto más grandes que el resto del gráfico.
TAMANIO_EJE_PAISES = 10
TEXTO_PORCENTAJE = "<b>%{text:.1f}%</b>"
# Detalle flotante sin el nombre de la categoría (ya está en la leyenda): `<extra></extra>` quita
# el recuadro con el nombre de la traza que Plotly agrega por defecto.
HOVER_POR_PAIS = "%{y}<br>Porcentaje: %{x:.1f}%<extra></extra>"


def _nota_ponderacion_por_pais(df, columns_col):
    """Nota al pie de los cruces por país, con el N de casos con dato en el cruce."""
    n = int(df[["pais_nacimiento_var", columns_col]].notna().all(axis=1).sum())
    nota_ponderacion(
        n,
        "Países ponderados por nacionalidad; "
        "Población migrante total ponderada con el ponderador general",
    )


def _tabla_ponderada(df, index_col, columns_col, etiqueta_poblacion):
    """Arma una tabla índice (país) x columnas con los pesos muestrales sumados (no conteo de
    filas), ordenada de menor a mayor magnitud, y agrega al final una fila `etiqueta_poblacion`
    con la distribución de toda la población filtrada como referencia. Todas las filas por país usan
    el ponderador intra nacionalidad (aunque en los países sin ajuste propio valga 1) y solo la fila
    de población usa el general. Devuelve el porcentaje resultante por fila, el peso sumado y el
    orden final de categorías."""
    pivot = df.groupby([index_col, columns_col])[PESO_NACIONALIDAD].sum().unstack(fill_value=0)
    orden = pivot.sum(axis=1).sort_values().index.tolist()
    pivot = pivot.loc[orden]

    poblacion = df.groupby(columns_col)[PESO_TOTAL].sum().reindex(pivot.columns, fill_value=0)
    pivot.loc[etiqueta_poblacion] = poblacion

    # Plotly invierte el orden de category_orders en gráficos horizontales (la primera categoría
    # de la lista termina abajo del todo), por eso la referencia poblacional va primera acá para
    # terminar arriba del todo en el gráfico.
    orden_final = [etiqueta_poblacion] + orden
    pivot = pivot.loc[orden_final]

    # Sin redondear: así las barras apiladas de cada fila suman exactamente 100% y quedan en la
    # misma escala; el redondeo a enteros se aplica solo en las etiquetas (texttemplate).
    tabla = pivot.div(pivot.sum(axis=1), axis=0).mul(100)
    return tabla, pivot, orden_final


def _ticktext_con_referencia(orden):
    return [f"<b>{c}</b>" if c == POBLACION_TOTAL_LABEL else c for c in orden]


def _datos_por_pais(df, columna, sin_graficar=()):
    """Tabla larga (país, categoría, %) lista para graficar, con la fila de Población migrante
    total y el orden de filas de `_tabla_ponderada`. Las categorías de `sin_graficar` cuentan en el
    total de cada fila (los % siguen siendo sobre todas las personas del país) pero no se grafican."""
    tabla, conteo, orden = _tabla_ponderada(df, "pais_nacimiento_var", columna, POBLACION_TOTAL_LABEL)
    tabla = tabla.drop(columns=list(sin_graficar), errors="ignore")
    conteo = conteo.drop(columns=list(sin_graficar), errors="ignore")
    data = tabla.reset_index().melt(id_vars="pais_nacimiento_var", var_name="Categoría", value_name="Porcentaje")
    data_cantidad = conteo.reset_index().melt(id_vars="pais_nacimiento_var", var_name="Categoría", value_name="Cantidad")
    return data.merge(data_cantidad, on=["pais_nacimiento_var", "Categoría"]), orden


def _formato_por_pais(fig, orden, rango_max):
    """Formato común de los gráficos según país de origen: leyenda horizontal arriba, sin títulos de
    eje (los valores ya llevan %), escala fija de 0 a `rango_max` con marcas cada 25%, % en negrita
    con 1 decimal, detalle flotante sin la categoría, y Población migrante total en la primera fila
    y en negrita."""
    fig.update_traces(
        texttemplate=TEXTO_PORCENTAJE,
        # Detalle de personas (ponderado) deshabilitado a pedido; customdata queda
        # disponible para reactivarlo agregando de nuevo el <span> con %{customdata[0]}.
        hovertemplate=HOVER_POR_PAIS,
        # Deja ver las etiquetas que quedan pasando el máximo de la escala.
        cliponaxis=False,
    )
    fig.update_layout(
        yaxis_title=None, xaxis_title=None,
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0, title_text=None),
        # Margen derecho para que entre la última etiqueta del eje.
        margin=dict(t=10, b=10, l=10, r=30),
    )
    marcas = list(range(0, rango_max + 1, 25))
    fig.update_xaxes(range=[0, rango_max + 1], tickvals=marcas, ticktext=[f"{m}%" for m in marcas])
    aplicar_tipografia(fig)
    # En barras horizontales Plotly dibuja la primera categoría abajo: se invierte `orden` para
    # que Población migrante total quede siempre en la primera fila, arriba de todo.
    fig.update_yaxes(
        categoryorder="array", categoryarray=orden[::-1],
        tickmode="array", tickvals=orden, ticktext=_ticktext_con_referencia(orden),
        tickfont=dict(size=TAMANIO_EJE_PAISES),
    )


def _apilado_por_pais(df, columna, titulo, key, categorias, colores, etiquetas=None):
    """Barras apiladas al 100% por país (una fila por país y la de Población migrante total arriba),
    con las categorías en el orden fijo de `categorias`. Las barras usan el valor sin redondear (cada
    fila suma 100%) y la etiqueta va adentro con 1 decimal; en segmentos muy finos Plotly la achica."""
    with st.container(border=True, key=key):
        st.subheader(titulo)
        data, orden = _datos_por_pais(df, columna)
        if etiquetas:
            data["Categoría"] = data["Categoría"].map(etiquetas)
        fig = px.bar(
            data, x="Porcentaje", y="pais_nacimiento_var", color="Categoría",
            orientation="h", barmode="stack",
            category_orders={"pais_nacimiento_var": orden, "Categoría": categorias},
            color_discrete_map=colores,
            text="Porcentaje", custom_data=["Cantidad"],
        )
        fig.update_traces(textposition="inside")
        _formato_por_pais(fig, orden, rango_max=100)
        st.plotly_chart(fig, width="stretch")
        _nota_ponderacion_por_pais(df, columna)


def _agrupado_por_pais(df, columna, titulo, key, categorias, rango_max, sin_graficar=()):
    """Barras agrupadas por país (una barra por categoría, en el orden fijo de `categorias`), con la
    fila de Población migrante total arriba y la etiqueta afuera de cada barra."""
    with st.container(border=True, key=key):
        st.subheader(titulo)
        data, orden = _datos_por_pais(df, columna, sin_graficar)
        categorias = [c for c in categorias if c not in sin_graficar]
        fig = px.bar(
            data, x="Porcentaje", y="pais_nacimiento_var", color="Categoría",
            orientation="h", barmode="group",
            category_orders={"pais_nacimiento_var": orden, "Categoría": categorias},
            color_discrete_map=dict(zip(categorias, COLORES_CATEGORIAS)),
            text="Porcentaje", custom_data=["Cantidad"],
        )
        fig.update_traces(textposition="outside")
        _formato_por_pais(fig, orden, rango_max)
        st.plotly_chart(fig, width="stretch")
        _nota_ponderacion_por_pais(df, columna)


def _pais_por_genero(df):
    _apilado_por_pais(
        df, "genero_agrup", "Composición por género según país de origen", "grafico_pais_genero",
        GENERO_ORDEN, GENERO_COLORES, etiquetas=GENERO_ETIQUETAS,
    )


def _descendencia_por_pais(df):
    # "Ninguna de las anteriores" es la categoría mayoritaria y aplastaba la escala del resto. El
    # valor más alto que queda es 73,3% (Haití, 2020), así que la escala va de 0 a 75%.
    _agrupado_por_pais(
        df, "descendencia", "Pertenencia afrodescendiente y otras según país de origen", "grafico_descendencia",
        DESCENDENCIA_ORDEN, rango_max=75, sin_graficar=DESCENDENCIA_SIN_GRAFICAR,
    )


def _idioma_por_pais(df):
    _apilado_por_pais(
        df, "idioma_var", "Lenguas habladas según país de origen", "grafico_pais_idioma",
        IDIOMA_ORDEN, IDIOMA_COLORES,
    )


def _residencia_por_pais(df):
    _agrupado_por_pais(
        df, "periodo_residencia", "Años de residencia según país de origen", "grafico_pais_residencia",
        PERIODO_RESIDENCIA_ORDEN, rango_max=100,
    )


def _region_por_edad(df):
    with st.container(border=True, key="grafico_region_edad"):
        st.subheader("Región de residencia según rango etario")
        # No desagrega por país -> ponderador general
        conteo = df.groupby(["edad_agrupada", "region"])[PESO_TOTAL].sum().unstack(fill_value=0)
        tabla = conteo.div(conteo.sum(axis=1), axis=0).mul(100).round(0)
        data = tabla.reset_index().melt(id_vars="edad_agrupada", var_name="region", value_name="Porcentaje")
        data_cantidad = conteo.reset_index().melt(id_vars="edad_agrupada", var_name="region", value_name="Cantidad")
        data = data.merge(data_cantidad, on=["edad_agrupada", "region"])
        fig = px.bar(
            data, x="region", y="Porcentaje", color="edad_agrupada",
            barmode="group", color_discrete_sequence=CHART_SEQUENCE,
            text="Porcentaje", custom_data=["Cantidad"],
        )
        fig.update_traces(
            texttemplate=TEXTO_PORCENTAJE_ENTERO, textposition="outside",
            # Detalle de personas (ponderado) deshabilitado a pedido; customdata queda
            # disponible para reactivarlo agregando de nuevo el <span> con %{customdata[0]}.
            hovertemplate="%{x}<br>Porcentaje: %{y:.0f}%",
        )
        fig.update_layout(
            xaxis_title=None, yaxis_title="Porcentaje (%)",
            legend_title="Rango etario", margin=dict(t=25, b=25, l=15, r=15),
        )
        aplicar_tipografia(fig)
        fig.update_xaxes(tickfont=dict(size=TAMANIO_EJE_CATEGORIAS))
        st.plotly_chart(fig, width="stretch")
        nota_ponderacion(int(df[["edad_agrupada", "region"]].notna().all(axis=1).sum()))


# Categorías residuales que van al final de las tablas de composición, sin importar su peso.
CATEGORIAS_AL_FINAL = ["Otro", "Sin clasificar"]


def _formatear_porcentaje(valor):
    """Porcentaje entero; "<1%" para categorías presentes que redondean a 0 y "—" si no figuran."""
    if valor <= 0:
        return "—"
    return "<1%" if valor < 0.5 else f"{valor:.0f}%"


def _tabla_por_edicion(df, columna, etiqueta):
    """% ponderado (ponderador general de cada edición) de cada categoría de `columna`, con una
    columna por edición. Una categoría que no se muestra por separado en una edición (p. ej. un
    país que ese año queda dentro de "Otro") figura con "—"."""
    tabla = (
        df.dropna(subset=[columna])
        .groupby(["Año", columna])[PESO_TOTAL].sum()
        .unstack("Año", fill_value=0)
    )
    tabla = tabla.div(tabla.sum()).mul(100)
    principales = [c for c in tabla.mean(axis=1).sort_values(ascending=False).index if c not in CATEGORIAS_AL_FINAL]
    tabla = tabla.loc[principales + [c for c in CATEGORIAS_AL_FINAL if c in tabla.index]]
    tabla = tabla.apply(lambda col: col.map(_formatear_porcentaje))
    tabla.columns = [f"ENMA {anio}" for anio in tabla.columns]
    tabla.index.name = etiqueta
    return tabla.reset_index()


def _mostrar_tabla(tabla):
    """st.dataframe con la altura justa para mostrar todas las filas sin scroll interno."""
    st.dataframe(tabla, hide_index=True, width="stretch", height=(len(tabla) + 1) * 35 + 3)


def _composicion_ediciones(df):
    """Composición de cada muestra por país de origen y por región, una columna por edición. Usa
    la base completa: no la afectan los filtros de la página (año, nacionalidad ni región)."""
    with st.container(border=True, key="grafico_composicion_ediciones"):
        st.subheader("Composición de cada edición")
        col_pais, col_region = st.columns(2)
        with col_pais:
            st.markdown("**País de origen según edición**")
            _mostrar_tabla(_tabla_por_edicion(df, "pais_nacimiento_var", "País de origen"))
        with col_region:
            st.markdown("**Región de residencia según edición**")
            _mostrar_tabla(_tabla_por_edicion(df, "region", "Región de residencia"))
        n_por_anio = df["Año"].value_counts().sort_index()
        n_texto = " y ".join(f"{formatear_n(int(n))} ({anio})" for anio, n in n_por_anio.items())
        st.caption(
            "Describe la composición de cada muestra; las ediciones no son comparables pregunta por "
            "pregunta. \"—\": el país no se muestra por separado en esa edición y queda dentro de \"Otro\". "
            f"Datos ponderados con el ponderador general de cada edición. N = {n_texto}"
        )


def render():
    df = load_data()
    df_completo = df
    contador = iniciar_filtros()

    # Solo el filtro de año, que no afecta la sección "Composición de cada edición" (usa la base
    # completa, df_completo).
    mask = filtro_edicion(df, "socio_edicion")

    df = aplicar_filtros(df, mask, contador)

    st.title("Datos sociodemográficos")
    st.caption("Composición de la población migrante encuestada según origen, género, descendencia, idioma, edad, región y tiempo de residencia.")

    _composicion_ediciones(df_completo)

    col1, col2 = st.columns(2)
    with col1:
        _pais_por_genero(df)
    with col2:
        _descendencia_por_pais(df)

    col3, col4 = st.columns(2)
    with col3:
        _idioma_por_pais(df)
    with col4:
        _residencia_por_pais(df)

    col5, _ = st.columns(2)
    with col5:
        _region_por_edad(df)
