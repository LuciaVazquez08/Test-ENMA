import streamlit as st

from data_utils import aplicar_filtros, filtro_edicion, iniciar_filtros, load_data


def render():
    df = load_data()
    contador = iniciar_filtros()

    mask = filtro_edicion(df, "discriminacion_edicion")

    df = aplicar_filtros(df, mask, contador)

    st.title("Discriminación y violencia")
    st.caption("Experiencias de discriminación y violencia sufridas por la población migrante encuestada.")
    st.info("Próximamente")
