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
from enma_palette import CHART_SEQUENCE

PERIODO_RESIDENCIA_ORDEN = ["Hasta 5 años", "Entre 5 y 9 años", "Más de 10 años"]

ALTURA_GRANDE = 300
ALTURA_CHICA = 180

# Columnas de ponderador disponibles en el dataset (una por fila, ya armonizadas
# entre ediciones). Usar PESO_NACIONALIDAD para todo gráfico que desagregue por
# país/nacionalidad, y PESO_TOTAL para el resto.
PESO_TOTAL = "peso_muestral_total"
PESO_NACIONALIDAD = "peso_muestral_nacionalidad"


def _tabla_ponderada(df, filas, columnas, peso):
    """Arma el equivalente ponderado de:
        df.groupby([filas, columnas]).size().unstack(fill_value=0)
    sumando `peso` en vez de contar filas.
    """
    conteo = (
        df.groupby([filas, columnas])[peso]
        .sum()
        .unstack(fill_value=0)
    )
    return conteo


def _pais_por_genero(df):
    st.subheader("País de origen")
    # Desagrega por país -> usar peso ponderado por nacionalidad
    conteo = _tabla_ponderada(df, "pais_nacimiento_var", "genero_agrup", PESO_NACIONALIDAD)
    tabla = conteo.div(conteo.sum(axis=1), axis=0).mul(100).round(1)
    orden_paises = tabla.sum(axis=1).sort_values().index
    tabla = tabla.loc[orden_paises]
    conteo = conteo.loc[orden_paises]
    data = tabla.reset_index().melt(id_vars="pais_nacimiento_var", var_name="Género", value_name="Porcentaje")
    data_cantidad = conteo.reset_index().melt(id_vars="pais_nacimiento_var", var_name="Género", value_name="Cantidad")
    data = data.merge(data_cantidad, on=["pais_nacimiento_var", "Género"])
    fig = px.bar(
        data, x="Porcentaje", y="pais_nacimiento_var", color="Género",
        orientation="h", barmode="stack",
        color_discrete_sequence=CHART_SEQUENCE,
        text="Porcentaje", custom_data=["Cantidad"],
    )
    fig.update_traces(
        texttemplate="%{text}%", textposition="inside",
        hovertemplate="%{y}<br>Porcentaje: %{x:.1f}%<br>Personas (ponderado): %{customdata[0]:,.0f}",
    )
    fig.update_layout(
        yaxis_title=None, xaxis_title="Porcentaje (%)",
        margin=dict(t=10, b=10), height=ALTURA_GRANDE,
    )
    aplicar_tipografia(fig)
    fig.update_yaxes(tickmode="linear", dtick=1, tickfont=dict(size=9))
    st.plotly_chart(fig, use_container_width=True)


def _descendencia_por_pais(df):
    st.subheader("Descendencia")
    # Desagrega por país -> usar peso ponderado por nacionalidad
    conteo = _tabla_ponderada(df, "pais_nacimiento_var", "descendencia", PESO_NACIONALIDAD)
    tabla = conteo.div(conteo.sum(axis=1), axis=0).mul(100).round(1)
    orden_paises = tabla.sum(axis=1).sort_values().index
    tabla = tabla.loc[orden_paises]
    conteo = conteo.loc[orden_paises]
    data = tabla.reset_index().melt(id_vars="pais_nacimiento_var", var_name="Descendencia", value_name="Porcentaje")
    data_cantidad = conteo.reset_index().melt(id_vars="pais_nacimiento_var", var_name="Descendencia", value_name="Cantidad")
    data = data.merge(data_cantidad, on=["pais_nacimiento_var", "Descendencia"])
    fig = px.bar(
        data, x="Porcentaje", y="pais_nacimiento_var", color="Descendencia",
        orientation="h", barmode="group",
        color_discrete_sequence=CHART_SEQUENCE,
        text="Porcentaje", custom_data=["Cantidad"],
    )
    fig.update_traces(
        texttemplate="%{text}%", textposition="outside",
        hovertemplate="%{y}<br>Porcentaje: %{x:.1f}%<br>Personas (ponderado): %{customdata[0]:,.0f}",
    )
    fig.update_layout(
        yaxis_title=None, xaxis_title="Porcentaje (%)",
        margin=dict(t=10, b=10), height=ALTURA_GRANDE,
    )
    aplicar_tipografia(fig)
    fig.update_xaxes(range=[0, data["Porcentaje"].max() * 1.2])
    fig.update_yaxes(tickmode="linear", dtick=1, tickfont=dict(size=9))
    st.plotly_chart(fig, use_container_width=True)


def _region_por_edad(df):
    st.subheader("Región de residencia")
    # No desagrega por país -> usar peso total
    conteo = _tabla_ponderada(df, "edad_agrupada", "region", PESO_TOTAL)
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
        hovertemplate="%{x}<br>Porcentaje: %{y:.1f}%<br>Personas (ponderado): %{customdata[0]:,.0f}",
    )
    fig.update_layout(
        xaxis_title=None, yaxis_title="Porcentaje (%)",
        legend_title="Rango etario", margin=dict(t=10, b=10), height=ALTURA_CHICA,
    )
    aplicar_tipografia(fig)
    st.plotly_chart(fig, use_container_width=True)


def render():
    df = load_data()
    contador = iniciar_filtros()

    mask_edicion = filtro_edicion(df, "socio_edicion")
    mask = mask_edicion & filtro_nacionalidad(df, "socio_nacionalidad", mask_edicion)
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
        grafico_barras(df, "idioma_var", "Lenguas habladas", horizontal=True, height=ALTURA_CHICA, columna_peso=PESO_TOTAL)
    with col5:
        grafico_barras(df, "periodo_residencia", "Años de residencia", orden=PERIODO_RESIDENCIA_ORDEN, height=ALTURA_CHICA, columna_peso=PESO_TOTAL)