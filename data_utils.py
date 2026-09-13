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
def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


def iniciar_filtros() -> "st.delta_generator.DeltaGenerator":
    """Encabezado del panel de filtros de la página + placeholder para el contador
    de encuestados (se completa recién en aplicar_filtros, una vez armada la máscara)."""
    st.sidebar.header("Filtros")
    return st.sidebar.empty()


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
        if horizontal:
            data = data.iloc[::-1]
            fig = px.bar(
                data, x="Porcentaje", y=columna, orientation="h",
                color_discrete_sequence=CHART_SEQUENCE, text="Porcentaje",
                custom_data=["Cantidad"],
            )
            fig.update_layout(yaxis_title=None, xaxis_title="Porcentaje (%)")
            fig.update_xaxes(range=[0, data["Porcentaje"].max() * 1.18])
            hovertemplate = (
                "%{y}<br>Porcentaje: %{x:.1f}%<br>"
                f"<span style='color:{COLOR_DETALLE}'>Personas (ponderado): %{{customdata[0]:,.0f}}</span>"
                "<extra></extra>"
            )
        else:
            fig = px.bar(
                data, x=columna, y="Porcentaje",
                color_discrete_sequence=CHART_SEQUENCE, text="Porcentaje",
                custom_data=["Cantidad"],
            )
            fig.update_layout(xaxis_title=None, yaxis_title="Porcentaje (%)")
            fig.update_yaxes(range=[0, data["Porcentaje"].max() * 1.3])
            hovertemplate = (
                "%{x}<br>Porcentaje: %{y:.1f}%<br>"
                f"<span style='color:{COLOR_DETALLE}'>Personas (ponderado): %{{customdata[0]:,.0f}}</span>"
                "<extra></extra>"
            )
        fig.update_traces(texttemplate="%{text}%", textposition="outside", hovertemplate=hovertemplate)
        fig.update_layout(margin=dict(t=25, b=25, l=15, r=15))
        aplicar_tipografia(fig)
        st.plotly_chart(fig, width="stretch")
