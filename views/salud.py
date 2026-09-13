import streamlit as st

from data_utils import aplicar_filtros, filtro_edicion, iniciar_filtros, load_data


def render():
    df = load_data()
    contador = iniciar_filtros()

    mask = filtro_edicion(df, "salud_edicion")

    df = aplicar_filtros(df, mask, contador)

    st.title("Derecho a la salud")
    st.caption("Cobertura, acceso y dificultades relacionadas con la atención de la salud.")
    st.info("Próximamente")
