import streamlit as st

from data_utils import (
    aplicar_filtros,
    filtro_edicion,
    grafico_barras,
    grafico_multiseleccion,
    iniciar_filtros,
    load_data,
)

INCONVENIENTES_EDUCACION_HIJOS = [
    ("hijos_educacion_problema_cupo", "Problemas de cupo en la escuela"),
    ("hijos_educacion_problema_inscripcion", "Problemas con la inscripción"),
    ("hijos_educacion_problema_documentacion", "Problemas con la documentación del hijo/a"),
    ("hijos_educacion_problema_otros", "Otros problemas"),
]


def render():
    df = load_data()
    contador = iniciar_filtros()

    mask = filtro_edicion(df, "hijos_edicion")

    df = aplicar_filtros(df, mask, contador)

    st.title("Hijos/as y educación")
    st.caption("Asistencia educativa de hijos/as e inconvenientes en su inscripción escolar.")

    col1, col2 = st.columns(2)
    with col1:
        grafico_barras(df, "hijos", "Tenencia de hijos/as")
    with col2:
        grafico_barras(df, "asistencia_educacion", "Hijos/as que asisten actualmente a la escuela en Argentina")

    sin_problemas = df["hijos_educacion_problema_ninguno"] != True  # noqa: E712
    grafico_multiseleccion(
        df[sin_problemas], INCONVENIENTES_EDUCACION_HIJOS,
        "Inconvenientes para la inscripción escolar de hijos/as",
        "Qué % de quienes tuvieron algún inconveniente declaró cada tipo (pregunta de selección múltiple: una persona puede haber tenido más de uno).",
    )
