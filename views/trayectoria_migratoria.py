import streamlit as st

from data_utils import aplicar_filtros, filtro_edicion, iniciar_filtros, load_data


def render():
    df = load_data()
    contador = iniciar_filtros()

    mask = filtro_edicion(df, "trayectoria_edicion")

    df = aplicar_filtros(df, mask, contador)

    st.title("Trayectoria migratoria")
    st.caption("Motivos de la migración, tiempo de residencia y movilidad dentro y fuera del país.")
    st.info("Próximamente")
