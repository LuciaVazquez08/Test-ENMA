import streamlit as st

from data_utils import (
    aplicar_filtros,
    filtro_edicion,
    grafico_barras,
    grafico_multiseleccion,
    iniciar_filtros,
    load_data,
)

TIPO_ESTUDIO = [
    ("estudio_primario", "Primario"),
    ("estudio_secundario", "Secundario"),
    ("estudio_superior", "Terciario, universitario o postgrado"),
    ("estudio_capacitaciones", "Capacitaciones o cursos"),
]

INCONVENIENTES_INSCRIPCION = [
    ("inscripcion_estudio_dni", "Problemas con el DNI"),
    ("inscripcion_estudio_discriminacion", "Discriminación o xenofobia"),
    ("inscripcion_estudio_inscripcion", "Problemas con la inscripción"),
    ("inscripcion_estudio_otros", "Otros"),
]


def render():
    df = load_data()
    contador = iniciar_filtros()

    mask = filtro_edicion(df, "educacion_edicion")

    df = aplicar_filtros(df, mask, contador)

    st.title("Trayectoria educativa (adultos/as)")
    st.caption("Nivel educativo alcanzado y situación educativa actual de la población encuestada.")

    col1, col2 = st.columns(2)
    with col1:
        grafico_barras(df, "nivel_educativo_agrup", "Máximo nivel educativo alcanzado")
    with col2:
        grafico_barras(df, "estudiando_actualmente", "Está estudiando actualmente")

    grafico_multiseleccion(
        df, TIPO_ESTUDIO,
        "Tipo de estudios que cursa actualmente",
        "Qué % de quienes estudian actualmente cursa cada tipo de estudio (pregunta de selección múltiple: una persona puede cursar más de uno).",
    )

    sin_inconvenientes = df["inscripcion_estudio_ninguno"] != True  # noqa: E712
    grafico_multiseleccion(
        df[sin_inconvenientes], INCONVENIENTES_INSCRIPCION,
        "Inconvenientes para la inscripción en el nivel educativo en curso",
        "Qué % de quienes tuvieron inconvenientes declaró cada tipo (pregunta de selección múltiple: una persona puede haber tenido más de uno).",
    )
