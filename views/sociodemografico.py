import plotly.express as px
import streamlit as st

from data_utils import (
    aplicar_filtros,
    aplicar_tipografia,
    filtro_edicion,
    filtro_nacionalidad,
    filtro_region,
    grafico_barras,
    iniciar_filtros,
    load_data,
)
from enma_palette import CHART_SEQUENCE, COLORS

PERIODO_RESIDENCIA_ORDEN = ["Hasta 5 años", "Entre 5 y 9 años", "Más de 10 años"]

# Ponderadores muestrales: por nacionalidad (corrige la composición dentro de
# cada país de origen) y total (corrige la composición de la población
# migrante completa, entre países). No son intercambiables: los gráficos que
# desagregan por país usan el primero fila por fila, y la fila de referencia
# poblacional usa el segundo.
PESO_NACIONALIDAD = "peso_muestral_nacionalidad"
PESO_TOTAL = "peso_muestral_total"

POBLACION_TOTAL_LABEL = "Población total"
COLOR_DETALLE = COLORS["text_3"]


def _tabla_ponderada(df, index_col, columns_col, peso_pais, peso_poblacion, etiqueta_poblacion):
    """Arma una tabla índice x columnas con los pesos muestrales sumados (no
    conteo de filas), ordenada de menor a mayor magnitud, y agrega al final
    una fila `etiqueta_poblacion` con la distribución de toda la población
    filtrada (ponderada con `peso_poblacion`) como referencia. Devuelve el
    porcentaje resultante por fila, el peso sumado (para el detalle de
    "personas") y el orden final de categorías."""
    pivot = df.groupby([index_col, columns_col])[peso_pais].sum().unstack(fill_value=0)
    orden = pivot.sum(axis=1).sort_values().index.tolist()
    pivot = pivot.loc[orden]

    poblacion = df.groupby(columns_col)[peso_poblacion].sum().reindex(pivot.columns, fill_value=0)
    pivot.loc[etiqueta_poblacion] = poblacion

    orden_final = orden + [etiqueta_poblacion]
    pivot = pivot.loc[orden_final]

    tabla = pivot.div(pivot.sum(axis=1), axis=0).mul(100).round(1)
    return tabla, pivot, orden_final


def _ticktext_con_referencia(orden):
    return [f"<b>{c}</b>" if c == POBLACION_TOTAL_LABEL else c for c in orden]


def _pais_por_genero(df):
    st.subheader("País de origen")
    tabla, conteo, orden = _tabla_ponderada(
        df, "pais_nacimiento_var", "genero_agrup", PESO_NACIONALIDAD, PESO_TOTAL, POBLACION_TOTAL_LABEL,
    )
    data = tabla.reset_index().melt(id_vars="pais_nacimiento_var", var_name="Género", value_name="Porcentaje")
    data_cantidad = conteo.reset_index().melt(id_vars="pais_nacimiento_var", var_name="Género", value_name="Cantidad")
    data = data.merge(data_cantidad, on=["pais_nacimiento_var", "Género"])
    fig = px.bar(
        data, x="Porcentaje", y="pais_nacimiento_var", color="Género",
        orientation="h", barmode="stack",
        category_orders={"pais_nacimiento_var": orden},
        color_discrete_sequence=CHART_SEQUENCE,
        text="Porcentaje", custom_data=["Cantidad"],
    )
    fig.update_traces(
        texttemplate="%{text}%", textposition="inside",
        hovertemplate=(
            "%{y}<br>Porcentaje: %{x:.1f}%<br>"
            f"<span style='color:{COLOR_DETALLE}'>Personas (ponderado): %{{customdata[0]:,.0f}}</span>"
        ),
    )
    fig.update_layout(
        yaxis_title=None, xaxis_title="Porcentaje (%)",
        margin=dict(t=10, b=10),
    )
    aplicar_tipografia(fig)
    fig.update_yaxes(tickmode="array", tickvals=orden, ticktext=_ticktext_con_referencia(orden), tickfont=dict(size=9))
    st.plotly_chart(fig, width="stretch")
    st.caption(
        "«Población total» pondera todo el conjunto filtrado con el peso muestral total, "
        "como referencia frente a la distribución de género de cada nacionalidad "
        "(ponderada con el peso muestral por nacionalidad)."
    )


def _descendencia_por_pais(df):
    st.subheader("Descendencia")
    tabla, conteo, orden = _tabla_ponderada(
        df, "pais_nacimiento_var", "descendencia", PESO_NACIONALIDAD, PESO_TOTAL, POBLACION_TOTAL_LABEL,
    )
    data = tabla.reset_index().melt(id_vars="pais_nacimiento_var", var_name="Descendencia", value_name="Porcentaje")
    data_cantidad = conteo.reset_index().melt(id_vars="pais_nacimiento_var", var_name="Descendencia", value_name="Cantidad")
    data = data.merge(data_cantidad, on=["pais_nacimiento_var", "Descendencia"])
    fig = px.bar(
        data, x="Porcentaje", y="pais_nacimiento_var", color="Descendencia",
        orientation="h", barmode="group",
        category_orders={"pais_nacimiento_var": orden},
        color_discrete_sequence=CHART_SEQUENCE,
        text="Porcentaje", custom_data=["Cantidad"],
    )
    fig.update_traces(
        texttemplate="%{text}%", textposition="outside",
        hovertemplate=(
            "%{y}<br>Porcentaje: %{x:.1f}%<br>"
            f"<span style='color:{COLOR_DETALLE}'>Personas (ponderado): %{{customdata[0]:,.0f}}</span>"
        ),
    )
    fig.update_layout(
        yaxis_title=None, xaxis_title="Porcentaje (%)",
        margin=dict(t=10, b=10),
    )
    aplicar_tipografia(fig)
    fig.update_xaxes(range=[0, data["Porcentaje"].max() * 1.2])
    fig.update_yaxes(tickmode="array", tickvals=orden, ticktext=_ticktext_con_referencia(orden), tickfont=dict(size=9))
    st.plotly_chart(fig, width="stretch")
    st.caption(
        "«Población total» pondera todo el conjunto filtrado con el peso muestral total, "
        "como referencia frente a la distribución de descendencia de cada nacionalidad "
        "(ponderada con el peso muestral por nacionalidad)."
    )


def _region_por_edad(df):
    st.subheader("Región de residencia")
    # No desagrega por país -> usar peso total
    conteo = df.groupby(["edad_agrupada", "region"])[PESO_TOTAL].sum().unstack(fill_value=0)
    tabla = conteo.div(conteo.sum(axis=1), axis=0).mul(100).round(1)
    data = tabla.reset_index().melt(id_vars="edad_agrupada", var_name="region", value_name="Porcentaje")
    data_cantidad = conteo.reset_index().melt(id_vars="edad_agrupada", var_name="region", value_name="Cantidad")
    data = data.merge(data_cantidad, on=["edad_agrupada", "region"])
    fig = px.bar(
        data, x="region", y="Porcentaje", color="edad_agrupada",
        barmode="group", color_discrete_sequence=CHART_SEQUENCE,
        text="Porcentaje", custom_data=["Cantidad"],
    )
    fig.update_traces(
        texttemplate="%{text}%", textposition="outside",
        hovertemplate=(
            "%{x}<br>Porcentaje: %{y:.1f}%<br>"
            f"<span style='color:{COLOR_DETALLE}'>Personas (ponderado): %{{customdata[0]:,.0f}}</span>"
        ),
    )
    fig.update_layout(
        xaxis_title=None, yaxis_title="Porcentaje (%)",
        legend_title="Rango etario", margin=dict(t=10, b=10),
    )
    aplicar_tipografia(fig)
    st.plotly_chart(fig, width="stretch")


def render():
    df = load_data()
    contador = iniciar_filtros()

    mask = filtro_edicion(df, "socio_edicion", reset_keys=["socio_nacionalidad"])
    mask &= filtro_nacionalidad(df, "socio_nacionalidad", df_opciones=df[mask])
    mask &= filtro_region(df, "socio_region")

    df = aplicar_filtros(df, mask, contador)

    st.title("Datos sociodemográficos")
    st.caption("Composición de la población migrante encuestada según origen, género, descendencia, idioma, edad, región y tiempo de residencia.")

    col1, col2 = st.columns(2)
    with col1:
        _pais_por_genero(df)
    with col2:
        _descendencia_por_pais(df)

    col3, col4, col5 = st.columns(3)
    with col3:
        _region_por_edad(df)
    with col4:
        grafico_barras(df, "idioma_var", "Lenguas habladas", horizontal=True, columna_peso=PESO_TOTAL)
    with col5:
        grafico_barras(df, "periodo_residencia", "Años de residencia", orden=PERIODO_RESIDENCIA_ORDEN, columna_peso=PESO_TOTAL)
