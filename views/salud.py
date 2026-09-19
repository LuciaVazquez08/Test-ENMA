import streamlit as st

from data_utils import (
    aplicar_filtros,
    filtro_edicion,
    grafico_barras,
    grafico_multiseleccion,
    iniciar_filtros,
    load_data,
)

FORMAS_ACCESO_SALUD = [
    ("salud_acceso_publica", "Salud pública"),
    ("salud_acceso_obrasocial", "Obra social, prepaga o privada"),
    ("salud_acceso_tradicional", "Medicina tradicional, familiar o comunitaria"),
    ("salud_acceso_nunca_necesito", "Nunca necesitó atenderse"),
    ("salud_acceso_no_pudo", "No pudo atenderse"),
    ("salud_acceso_otro", "Otro"),
]

TIPOS_DIFICULTAD_SALUD = [
    ("salud_dificultad_maltrato", "Maltrato o discriminación"),
    ("salud_dificultad_economicas", "Barreras económicas"),
    ("salud_dificultad_administrativas", "Barreras administrativas"),
    ("salud_dificultad_comunicacion", "Barreras de comunicación (idioma)"),
    ("salud_dificultad_acceso_servicio", "Barreras de acceso al servicio (turnos, distancia)"),
    ("salud_dificultad_otras", "Otras"),
]


def render():
    df = load_data()
    contador = iniciar_filtros()

    mask = filtro_edicion(df, "salud_edicion")

    df = aplicar_filtros(df, mask, contador)

    st.title("Derecho a la salud")
    st.caption("Cobertura, acceso y dificultades relacionadas con la atención de la salud.")

    col1, col2, col3 = st.columns(3)
    with col1:
        grafico_barras(df, "salud_cobertura", "Cobertura de salud")
    with col2:
        grafico_barras(df, "salud_problemas", "Tuvo algún problema de salud")
    with col3:
        grafico_barras(df, "salud_dificultad_acceso", "Frecuencia de dificultades para acceder a la salud")

    grafico_multiseleccion(
        df, FORMAS_ACCESO_SALUD,
        "Formas de acceso a la atención de la salud",
        "Qué % de la población accedió (o intentó acceder) a la salud por cada vía en los últimos dos años (pregunta de selección múltiple).",
    )

    sin_dificultades = df["salud_dificultad_ninguna"] != True  # noqa: E712
    grafico_multiseleccion(
        df[sin_dificultades], TIPOS_DIFICULTAD_SALUD,
        "Tipos de dificultades de acceso a la salud",
        "Qué % de quienes tuvieron dificultades declaró cada tipo (pregunta de selección múltiple: una persona puede haber tenido más de una).",
    )
