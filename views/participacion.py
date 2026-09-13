import streamlit as st

from data_utils import aplicar_filtros, filtro_edicion, iniciar_filtros, load_data


def render():
    df = load_data()
    contador = iniciar_filtros()

    mask = filtro_edicion(df, "participacion_edicion")

    df = aplicar_filtros(df, mask, contador)

    st.title("Participación social y política")
    st.caption("Participación en organizaciones, voto en Argentina y en el país de origen, y percepción sobre la vida en Argentina.")
    st.info("Próximamente")
