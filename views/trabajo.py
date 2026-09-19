import streamlit as st

from data_utils import (
    aplicar_filtros,
    filtro_edicion,
    grafico_barras,
    grafico_multiseleccion,
    iniciar_filtros,
    load_data,
)

DIFICULTADES_TRABAJO_EXPERIENCIA = [
    ("trabajo_dificultad_titulos", "Convalidación de títulos"),
    ("trabajo_dificultad_discriminacion", "Discriminación (extranjero/a, género u orientación, edad)"),
    ("trabajo_dificultad_hogar", "Responsabilidades de cuidado o condición de salud"),
    ("trabajo_dificultad_documentacion", "Documentación faltante"),
    ("trabajo_dificultad_experiencia", "Falta de experiencia, idioma o información"),
]


def render():
    df = load_data()
    contador = iniciar_filtros()

    mask = filtro_edicion(df, "trabajo_edicion")

    df = aplicar_filtros(df, mask, contador)

    st.title("Situación socioeconómica")
    st.caption("Situación ocupacional, circuitos laborales y acceso a ayudas económicas.")

    col1, col2 = st.columns(2)
    with col1:
        grafico_barras(df, "situacion_ocupacional_agrup", "Situación ocupacional")
    with col2:
        grafico_barras(df, "trabajo_en_area_experiencia", "Trabaja en su área de experiencia o formación")

    grafico_barras(df, "dificultad_trabajo_experiencia", "Tuvo dificultad para conseguir un trabajo acorde a su experiencia")

    grafico_barras(df, "circuitos_laborales", "Circuito laboral de inserción", horizontal=True)

    grafico_multiseleccion(
        df, DIFICULTADES_TRABAJO_EXPERIENCIA,
        "Principales dificultades para acceder a un trabajo acorde a su experiencia",
        "Qué % de quienes tuvieron dificultades declaró cada tipo (pregunta de selección múltiple: una persona puede haber tenido más de una).",
    )

    col3, col4, col5 = st.columns(3)
    with col3:
        grafico_barras(df, "envia_dinero_exterior", "Envía dinero al exterior")
    with col4:
        grafico_barras(df, "recibe_ayuda_economica", "Recibe ayuda económica o alimentaria")
    with col5:
        grafico_barras(df, "dificultad_gestion_subsidios", "Dificultad para gestionar subsidios o prestaciones")
