import streamlit as st

from data_utils import (
    aplicar_filtros,
    filtro_cruce,
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
    filtro_cruce(df, "trabajo_cruce")

    st.title("Situación socioeconómica")
    st.caption("Situación ocupacional, circuitos laborales y acceso a ayudas económicas.")

    col1, col2 = st.columns(2)
    with col1:
        grafico_barras(df, "situacion_ocupacional_agrup", "Distribución por situación ocupacional")
    with col2:
        grafico_barras(df, "trabajo_en_area_experiencia", "Distribución por trabajo en su área de experiencia o formación")

    grafico_barras(df, "dificultad_trabajo_experiencia", "Distribución por dificultad para conseguir un trabajo acorde a su experiencia")

    grafico_barras(df, "circuitos_laborales", "Distribución por circuito laboral de inserción", horizontal=True)

    grafico_multiseleccion(
        df, DIFICULTADES_TRABAJO_EXPERIENCIA,
        "Distribución por dificultades para acceder a un trabajo acorde a su experiencia",
        "Qué % de quienes tuvieron dificultades declaró cada tipo (pregunta de selección múltiple: una persona puede haber tenido más de una).",
    )

    col3, col4 = st.columns(2)
    with col3:
        grafico_barras(df, "envia_dinero_exterior", "Distribución por envío de dinero al exterior")
    with col4:
        grafico_barras(df, "recibe_ayuda_economica", "Distribución por recepción de ayuda económica o alimentaria")

    col5, _ = st.columns(2)
    with col5:
        grafico_barras(df, "dificultad_gestion_subsidios", "Distribución por dificultad para gestionar subsidios o prestaciones")
