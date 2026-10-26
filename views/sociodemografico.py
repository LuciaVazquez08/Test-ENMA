import plotly.express as px
import streamlit as st

from data_utils import (
    PESO_NACIONALIDAD,
    PESO_TOTAL,
    aplicar_filtros,
    aplicar_tipografia,
    filtro_edicion,
    filtro_nacionalidad,
    filtro_region,
    grafico_barras,
    iniciar_filtros,
    load_data,
    nota_ponderacion,
)
from enma_palette import CHART_SEQUENCE

PERIODO_RESIDENCIA_ORDEN = ["Hasta 5 años", "Entre 5 y 9 años", "Más de 10 años"]

POBLACION_TOTAL_LABEL = "Población total"


def _nota_ponderacion_por_pais(df, columns_col):
    """Nota al pie de los cruces por país, con el N de casos con dato en el cruce."""
    n = int(df[["pais_nacimiento_var", columns_col]].notna().all(axis=1).sum())
    nota_ponderacion(
        n,
        "Países ponderados por nacionalidad; "
        "Población total ponderada con el ponderador general",
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

    tabla = pivot.div(pivot.sum(axis=1), axis=0).mul(100).round(0)
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
        fig = px.bar(
            data, x="Porcentaje", y="pais_nacimiento_var", color="Género",
            orientation="h", barmode="stack",
            category_orders={"pais_nacimiento_var": orden},
            color_discrete_sequence=CHART_SEQUENCE,
            text="Porcentaje", custom_data=["Cantidad"],
        )
        fig.update_traces(
            texttemplate="%{text:.0f}%", textposition="inside",
            # Detalle de personas (ponderado) deshabilitado a pedido; customdata queda
            # disponible para reactivarlo agregando de nuevo el <span> con %{customdata[0]}.
            hovertemplate="%{y}<br>Porcentaje: %{x:.0f}%",
        )
        fig.update_layout(
            yaxis_title=None, xaxis_title="Porcentaje (%)",
            margin=dict(t=25, b=25, l=15, r=15),
        )
        aplicar_tipografia(fig)
        fig.update_yaxes(tickmode="array", tickvals=orden, ticktext=_ticktext_con_referencia(orden), tickfont=dict(size=9))
        st.plotly_chart(fig, width="stretch")
        _nota_ponderacion_por_pais(df, "genero_agrup")


def _descendencia_por_pais(df):
    with st.container(border=True, key="grafico_descendencia"):
        st.subheader("Descendencia según país de origen")
        tabla, conteo, orden = _tabla_ponderada(
            df, "pais_nacimiento_var", "descendencia", POBLACION_TOTAL_LABEL,
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
            texttemplate="%{text:.0f}%", textposition="outside",
            # Detalle de personas (ponderado) deshabilitado a pedido; customdata queda
            # disponible para reactivarlo agregando de nuevo el <span> con %{customdata[0]}.
            hovertemplate="%{y}<br>Porcentaje: %{x:.0f}%",
        )
        fig.update_layout(
            yaxis_title=None, xaxis_title="Porcentaje (%)",
            margin=dict(t=25, b=25, l=15, r=15),
        )
        aplicar_tipografia(fig)
        fig.update_xaxes(range=[0, data["Porcentaje"].max() * 1.2])
        fig.update_yaxes(tickmode="array", tickvals=orden, ticktext=_ticktext_con_referencia(orden), tickfont=dict(size=9))
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
        grafico_barras(df, "idioma_var", "Distribución por lenguas habladas", horizontal=True, columna_peso=PESO_TOTAL)
    with col5:
        grafico_barras(df, "periodo_residencia", "Distribución por años de residencia", orden=PERIODO_RESIDENCIA_ORDEN, columna_peso=PESO_TOTAL)
