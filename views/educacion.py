import streamlit as st

from data_utils import aplicar_filtros, filtro_edicion, iniciar_filtros, load_data


def render():
    df = load_data()
    contador = iniciar_filtros()

    mask = filtro_edicion(df, "educacion_edicion")

    df = aplicar_filtros(df, mask, contador)

    st.title("Trayectoria educativa (adultos/as)")
    st.caption("Nivel educativo alcanzado y situación educativa actual de la población encuestada.")
    st.info("Próximamente")
