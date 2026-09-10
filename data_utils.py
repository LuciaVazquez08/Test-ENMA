import pandas as pd
import plotly.express as px
import streamlit as st

from enma_palette import CHART_SEQUENCE, FONT_BODY

DATA_PATH = "data/processed/ENMA.csv"


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
def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


def iniciar_filtros() -> "st.delta_generator.DeltaGenerator":
    """Encabezado del panel de filtros de la página + placeholder para el contador
    de encuestados (se completa recién en aplicar_filtros, una vez armada la máscara)."""
    st.sidebar.header("Filtros")
    return st.sidebar.empty()


def filtro_edicion(df: pd.DataFrame, key: str) -> pd.Series:
    anios = sorted(df["Año"].dropna().unique())
    seleccion = st.sidebar.selectbox("Edición / Año", anios, key=key)
    return df["Año"] == seleccion


def filtro_nacionalidad(df: pd.DataFrame, key: str, mask_edicion: pd.Series) -> pd.Series:
    opciones_df = df[mask_edicion]
    nacionalidades = sorted(opciones_df["pais_nacimiento_var"].dropna().unique())
    seleccion = st.sidebar.multiselect("Nacionalidad", nacionalidades, default=nacionalidades, key=key)
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
    height: int | None = None,
    columna_peso: str = "peso_muestral_total",
):
    st.subheader(titulo)
    data = distribucion(df, columna, orden, columna_peso=columna_peso)
    if data.empty:
        st.info("Sin datos para este filtro.")
        return
    if horizontal:
        data = data.iloc[::-1]
        fig = px.bar(
            data, x="Porcentaje", y=columna, orientation="h",
            color_discrete_sequence=CHART_SEQUENCE, text="Porcentaje",
            custom_data=["Cantidad"],
        )
        fig.update_layout(yaxis_title=None, xaxis_title="Porcentaje (%)")
        fig.update_xaxes(range=[0, data["Porcentaje"].max() * 1.18])
        hovertemplate = "%{y}<br>Porcentaje: %{x:.1f}%<br>Personas (ponderado): %{customdata[0]:,.0f}<extra></extra>"
    else:
        fig = px.bar(
            data, x=columna, y="Porcentaje",
            color_discrete_sequence=CHART_SEQUENCE, text="Porcentaje",
            custom_data=["Cantidad"],
        )
        fig.update_layout(xaxis_title=None, yaxis_title="Porcentaje (%)")
        fig.update_yaxes(range=[0, data["Porcentaje"].max() * 1.3])
        hovertemplate = "%{x}<br>Porcentaje: %{y:.1f}%<br>Personas (ponderado): %{customdata[0]:,.0f}<extra></extra>"
    fig.update_traces(texttemplate="%{text}%", textposition="outside", hovertemplate=hovertemplate)
    fig.update_layout(margin=dict(t=10, b=10))
    aplicar_tipografia(fig)
    if height:
        fig.update_layout(height=height)
    st.plotly_chart(fig, use_container_width=True)
