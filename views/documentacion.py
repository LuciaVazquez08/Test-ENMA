import streamlit as st

from data_utils import (
    aplicar_filtros,
    filtro_edicion,
    grafico_barras,
    grafico_multiseleccion,
    iniciar_filtros,
    load_data,
)

DIFICULTADES_DNI = [
    ("dni_dificultad_tipo_turnos", "Turnos o demoras en el trámite"),
    ("dni_dificultad_tipo_economica", "Dificultades económicas"),
    ("dni_dificultad_tipo_doc_origen", "Documentación del país de origen"),
    ("dni_dificultad_tipo_informacion", "Falta de información sobre el trámite"),
    ("dni_dificultad_tipo_internet", "Falta de internet o herramientas"),
    ("dni_dificultad_tipo_otro", "Otro"),
]


def render():
    df = load_data()
    contador = iniciar_filtros()

    mask = filtro_edicion(df, "documentacion_edicion")

    df = aplicar_filtros(df, mask, contador)

    st.title("Documentación y asilo")
    st.caption("Situación documentaria, dificultades para tramitar el DNI y solicitudes de asilo o refugio.")

    col1, col2 = st.columns(2)
    with col1:
        grafico_barras(df, "dni_tenencia", "Tenencia de DNI argentino")
    with col2:
        grafico_barras(df, "solicitud_asilo_refugio", "Solicitud de asilo, refugio o visado humanitario")

    grafico_multiseleccion(
        df, DIFICULTADES_DNI,
        "Tipos de dificultades para tramitar o renovar el DNI",
        "Qué % de quienes tuvieron que tramitar el DNI declaró cada dificultad (pregunta de selección múltiple: una persona puede haber tenido más de una).",
    )
