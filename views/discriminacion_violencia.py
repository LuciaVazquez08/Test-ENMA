import streamlit as st

from data_utils import (
    aplicar_filtros,
    filtro_edicion,
    grafico_barras,
    grafico_multiseleccion,
    iniciar_filtros,
    load_data,
)

AMBITOS_DISCRIMINACION = [
    ("discriminacion_lugar_calle", "Calle"),
    ("discriminacion_lugar_trabajo", "Trabajo"),
    ("discriminacion_lugar_estado", "Trámites del Estado"),
    ("discriminacion_lugar_medios", "Medios de comunicación"),
    ("discriminacion_lugar_educacion", "Escuela y/o universidad"),
    ("discriminacion_lugar_transporte", "Transporte público"),
    ("discriminacion_lugar_grupos_sociales", "Grupos sociales"),
    ("discriminacion_lugar_atencion_medica", "Atención médica"),
    ("discriminacion_lugar_fuerzas_seguridad", "Fuerzas de seguridad"),
    ("discriminacion_lugar_otros", "Otros"),
]


def render():
    df = load_data()
    contador = iniciar_filtros()

    mask = filtro_edicion(df, "discriminacion_edicion")

    df = aplicar_filtros(df, mask, contador)

    st.title("Discriminación y violencia")
    st.caption("Experiencias de discriminación y violencia sufridas por la población migrante encuestada.")

    col1, col2 = st.columns(2)
    with col1:
        grafico_barras(df, "violencia_fuerza_seguridad", "Situaciones de violencia por parte de fuerzas de seguridad")
    with col2:
        grafico_barras(df, "violencia_genero", "Situaciones de violencia por razones de género")

    grafico_barras(df, "discriminacion_experimentada", "Experimentó discriminación")

    grafico_multiseleccion(
        df, AMBITOS_DISCRIMINACION,
        "Ámbitos donde experimentó discriminación con mayor frecuencia",
        "Qué % de quienes fueron discriminados declaró cada ámbito (pregunta de selección múltiple: una persona puede haber sido discriminada en más de un ámbito).",
    )
