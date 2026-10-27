import plotly.express as px
import streamlit as st

from data_utils import (
    PESO_NACIONALIDAD,
    PESO_TOTAL,
    aplicar_filtros,
    aplicar_tipografia,
    formatear_n,
    filtro_edicion,
    grafico_barras,
    iniciar_filtros,
    load_data,
    nota_ponderacion,
)
from enma_palette import CHART_SEQUENCE, COLORS

PERIODO_RESIDENCIA_ORDEN = ["Hasta 5 años", "Entre 5 y 9 años", "Más de 10 años"]

POBLACION_TOTAL_LABEL = "Población migrante total"

DESCENDENCIA_SIN_GRAFICAR = ["Ninguna de las anteriores"]

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


def _pais_por_genero(df):
    with st.container(border=True, key="grafico_pais_genero"):
        st.subheader("Composición por género según país de origen")
        tabla, conteo, orden = _tabla_ponderada(
            df, "pais_nacimiento_var", "genero_agrup", POBLACION_TOTAL_LABEL,
        )
        data = tabla.reset_index().melt(id_vars="pais_nacimiento_var", var_name="Género", value_name="Porcentaje")
        data_cantidad = conteo.reset_index().melt(id_vars="pais_nacimiento_var", var_name="Género", value_name="Cantidad")
        data = data.merge(data_cantidad, on=["pais_nacimiento_var", "Género"])
        data["Género"] = data["Género"].map(GENERO_ETIQUETAS)
        fig = px.bar(
            data, x="Porcentaje", y="pais_nacimiento_var", color="Género",
            orientation="h", barmode="stack",
            category_orders={"pais_nacimiento_var": orden, "Género": GENERO_ORDEN},
            color_discrete_map=GENERO_COLORES,
            text="Porcentaje", custom_data=["Cantidad"],
        )
        fig.update_traces(
            # Barra con el valor sin redondear (cada fila suma 100%); etiqueta con 1 decimal.
            texttemplate=TEXTO_PORCENTAJE, textposition="inside",
            # Detalle de personas (ponderado) deshabilitado a pedido; customdata queda
            # disponible para reactivarlo agregando de nuevo el <span> con %{customdata[0]}.
            hovertemplate=HOVER_POR_PAIS,
        )
        # Leyenda horizontal arriba y sin título de eje X (los valores ya llevan %): así las barras
        # usan todo el ancho. Todas las barras llevan su % adentro; en segmentos muy finos Plotly
        # achica la etiqueta para que entre.
        fig.update_layout(
            yaxis_title=None, xaxis_title=None,
            legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0, title_text=None),
            # Margen derecho para que entre la etiqueta "100%" del eje.
            margin=dict(t=10, b=10, l=10, r=30),
        )
        fig.update_xaxes(range=[0, 101], tickvals=[0, 25, 50, 75, 100], ticktext=["0%", "25%", "50%", "75%", "100%"])
        aplicar_tipografia(fig)
        # En barras horizontales Plotly dibuja la primera categoría abajo: se invierte `orden` para
        # que Población migrante total quede siempre en la primera fila, arriba de todo.
        fig.update_yaxes(
            categoryorder="array", categoryarray=orden[::-1],
            tickmode="array", tickvals=orden, ticktext=_ticktext_con_referencia(orden),
            tickfont=dict(size=TAMANIO_EJE_PAISES),
        )
        st.plotly_chart(fig, width="stretch")
        _nota_ponderacion_por_pais(df, "genero_agrup")


def _descendencia_por_pais(df):
    with st.container(border=True, key="grafico_descendencia"):
        st.subheader("Pertenencia afrodescendiente y otras según país de origen")
        tabla, conteo, orden = _tabla_ponderada(
            df, "pais_nacimiento_var", "descendencia", POBLACION_TOTAL_LABEL,
        )
        # "Ninguna de las anteriores" se calcula (cuenta en el total de cada fila, así los % siguen
        # siendo sobre todas las personas del país) pero no se grafica: es la categoría mayoritaria
        # y aplastaba la escala del resto.
        tabla = tabla.drop(columns=DESCENDENCIA_SIN_GRAFICAR, errors="ignore")
        conteo = conteo.drop(columns=DESCENDENCIA_SIN_GRAFICAR, errors="ignore")
        data = tabla.reset_index().melt(id_vars="pais_nacimiento_var", var_name="Descendencia", value_name="Porcentaje")
        data_cantidad = conteo.reset_index().melt(id_vars="pais_nacimiento_var", var_name="Descendencia", value_name="Cantidad")
        data = data.merge(data_cantidad, on=["pais_nacimiento_var", "Descendencia"])
        colores = dict(zip(tabla.columns, COLORES_CATEGORIAS))
        fig = px.bar(
            data, x="Porcentaje", y="pais_nacimiento_var", color="Descendencia",
            orientation="h", barmode="group",
            category_orders={"pais_nacimiento_var": orden, "Descendencia": list(colores)},
            color_discrete_map=colores,
            text="Porcentaje", custom_data=["Cantidad"],
        )
        fig.update_traces(
            texttemplate=TEXTO_PORCENTAJE, textposition="outside",
            # Detalle de personas (ponderado) deshabilitado a pedido; customdata queda
            # disponible para reactivarlo agregando de nuevo el <span> con %{customdata[0]}.
            hovertemplate=HOVER_POR_PAIS,
        )
        # Mismo criterio que el gráfico de género: leyenda horizontal arriba y sin título de eje X,
        # para que las barras usen todo el ancho y no quede espacio en blanco antes de la nota.
        fig.update_layout(
            yaxis_title=None, xaxis_title=None,
            legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0, title_text=None),
            margin=dict(t=10, b=10, l=10, r=30),
        )
        aplicar_tipografia(fig)
        fig.update_xaxes(range=[0, data["Porcentaje"].max() * 1.2], ticksuffix="%")
        # En barras horizontales Plotly dibuja la primera categoría abajo: se invierte `orden` para
        # que Población migrante total quede siempre en la primera fila, arriba de todo.
        fig.update_yaxes(
            categoryorder="array", categoryarray=orden[::-1],
            tickmode="array", tickvals=orden, ticktext=_ticktext_con_referencia(orden),
            tickfont=dict(size=TAMANIO_EJE_PAISES),
        )
        st.plotly_chart(fig, width="stretch")
        _nota_ponderacion_por_pais(df, "descendencia")


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
            texttemplate="%{text:.0f}%", textposition="outside",
            # Detalle de personas (ponderado) deshabilitado a pedido; customdata queda
            # disponible para reactivarlo agregando de nuevo el <span> con %{customdata[0]}.
            hovertemplate="%{x}<br>Porcentaje: %{y:.0f}%",
        )
        fig.update_layout(
            xaxis_title=None, yaxis_title="Porcentaje (%)",
            legend_title="Rango etario", margin=dict(t=25, b=25, l=15, r=15),
        )
        aplicar_tipografia(fig)
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
        _region_por_edad(df)
    with col4:
        grafico_barras(df, "idioma_var", "Distribución por lenguas habladas", horizontal=True, columna_peso=PESO_TOTAL)

    col5, _ = st.columns(2)
    with col5:
        grafico_barras(df, "periodo_residencia", "Distribución por años de residencia", orden=PERIODO_RESIDENCIA_ORDEN, columna_peso=PESO_TOTAL)
