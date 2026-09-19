import pandas as pd
import streamlit as st

from data_utils import aplicar_filtros, filtro_edicion, grafico_barras, iniciar_filtros, load_data

HOGAR_PERSONAS_ORDEN = ["1", "2", "3", "4", "5 o más"]


def _agrupar_hogar_personas(df: pd.DataFrame) -> pd.DataFrame:
    """Agrupa la cantidad de personas en el hogar (numérica) en tramos, para poder graficarla
    como una distribución de categorías en vez de un promedio."""
    df = df.copy()
    df["hogar_personas_agrup"] = pd.cut(
        df["hogar_personas"], bins=[0, 1, 2, 3, 4, 10000], labels=HOGAR_PERSONAS_ORDEN,
    )
    return df


def render():
    df = load_data()
    contador = iniciar_filtros()

    mask = filtro_edicion(df, "familia_edicion")

    df = aplicar_filtros(df, mask, contador)

    st.title("Situación familiar y hogar")
    st.caption("Composición del hogar, convivencia, discapacidad y presencia de hijos/as.")

    df = _agrupar_hogar_personas(df)

    col1, col2 = st.columns(2)
    with col1:
        grafico_barras(df, "hogar_convivencia", "Convivencia con cónyuge o pareja")
    with col2:
        grafico_barras(df, "hogar_discapacidad", "Hogar con alguna persona con discapacidad")

    grafico_barras(df, "hogar_personas_agrup", "Cantidad de personas en el hogar", orden=HOGAR_PERSONAS_ORDEN)
