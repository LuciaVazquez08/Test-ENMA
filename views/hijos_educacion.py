import streamlit as st

from data_utils import aplicar_filtros, filtro_edicion, iniciar_filtros, load_data


def render():
    df = load_data()
    contador = iniciar_filtros()

    mask = filtro_edicion(df, "hijos_edicion")

    df = aplicar_filtros(df, mask, contador)

    st.title("Hijos/as y educación")
    st.caption("Asistencia educativa de hijos/as e inconvenientes en su inscripción escolar.")
    st.info("Próximamente")
