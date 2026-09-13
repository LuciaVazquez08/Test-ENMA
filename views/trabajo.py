import streamlit as st

from data_utils import aplicar_filtros, filtro_edicion, iniciar_filtros, load_data


def render():
    df = load_data()
    contador = iniciar_filtros()

    mask = filtro_edicion(df, "trabajo_edicion")

    df = aplicar_filtros(df, mask, contador)

    st.title("Situación socioeconómica")
    st.caption("Situación ocupacional, circuitos laborales y acceso a ayudas económicas.")
    st.info("Próximamente")
