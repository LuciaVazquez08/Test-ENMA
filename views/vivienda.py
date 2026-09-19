import streamlit as st

from data_utils import (
    aplicar_filtros,
    filtro_edicion,
    grafico_barras,
    grafico_multiseleccion,
    iniciar_filtros,
    load_data,
)

PROBLEMAS_VIVIENDA = [
    ("vivienda_dificultad_alquilar", "Barreras para alquilar"),
    ("vivienda_dificultad_economicas", "Barreras económicas"),
    ("vivienda_dificultad_programas", "Falta de acceso a programas de vivienda"),
    ("vivienda_dificultad_conflictos", "Conflictos habitacionales (desalojo, estafa)"),
    ("vivienda_dificultad_otras", "Otras"),
]


def render():
    df = load_data()
    contador = iniciar_filtros()

    mask = filtro_edicion(df, "vivienda_edicion")

    df = aplicar_filtros(df, mask, contador)

    st.title("Vivienda")
    st.caption("Tenencia de la vivienda y dificultades de acceso.")

    grafico_barras(df, "vivienda_tenencia", "Condición de tenencia de la vivienda")

    sin_dificultades = df["vivienda_dificultad_ninguna"] != True  # noqa: E712
    grafico_multiseleccion(
        df[sin_dificultades], PROBLEMAS_VIVIENDA,
        "Principales problemas de acceso a la vivienda en los últimos dos años",
        "Qué % de quienes tuvieron dificultades declaró cada tipo de problema (pregunta de selección múltiple: una persona puede haber tenido más de uno).",
    )
