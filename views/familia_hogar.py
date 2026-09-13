import streamlit as st

from data_utils import aplicar_filtros, filtro_edicion, iniciar_filtros, load_data


def render():
    df = load_data()
    contador = iniciar_filtros()

    mask = filtro_edicion(df, "familia_edicion")

    df = aplicar_filtros(df, mask, contador)

    st.title("Situación familiar y hogar")
    st.caption("Composición del hogar, convivencia, discapacidad y presencia de hijos/as.")
    st.info("Próximamente")
