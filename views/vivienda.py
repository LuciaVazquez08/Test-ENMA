import streamlit as st

from data_utils import aplicar_filtros, filtro_edicion, iniciar_filtros, load_data


def render():
    df = load_data()
    contador = iniciar_filtros()

    mask = filtro_edicion(df, "vivienda_edicion")

    df = aplicar_filtros(df, mask, contador)

    st.title("Vivienda")
    st.caption("Tenencia de la vivienda y dificultades de acceso.")
    st.info("Próximamente")
