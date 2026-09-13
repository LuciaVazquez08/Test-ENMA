import streamlit as st

from data_utils import aplicar_filtros, filtro_edicion, iniciar_filtros, load_data


def render():
    df = load_data()
    contador = iniciar_filtros()

    mask = filtro_edicion(df, "documentacion_edicion")

    df = aplicar_filtros(df, mask, contador)

    st.title("Documentación y asilo")
    st.caption("Situación documentaria, dificultades para tramitar el DNI y solicitudes de asilo o refugio.")
    st.info("Próximamente")
