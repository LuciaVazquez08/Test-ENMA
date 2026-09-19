import streamlit as st

from data_utils import (
    aplicar_filtros,
    filtro_edicion,
    grafico_barras,
    grafico_multiseleccion,
    iniciar_filtros,
    load_data,
)

TIPO_ORGANIZACION = [
    ("participacion_tipo_migrantes", "Organización de migrantes"),
    ("participacion_tipo_social_barrial", "Organización social, barrial o comunitaria"),
    ("participacion_tipo_movimiento_social", "Movimiento social"),
    ("participacion_tipo_partido", "Partido político"),
    ("participacion_tipo_religiosa", "Iglesia o comunidad religiosa"),
    ("participacion_tipo_cooperativa", "Cooperativa de trabajo o sindicato"),
    ("participacion_tipo_otra", "Otra"),
]

MOTIVOS_NO_VOTO_LOCAL = [
    ("motivo_no_voto_requisitos", "No cumple los requisitos (DNI, antigüedad, padrón)"),
    ("motivo_no_voto_desinformacion", "Desinformación"),
    ("motivo_no_voto_desinteres", "Desinterés"),
    ("motivo_no_voto_obstaculos", "Obstáculos materiales (lejanía, no habilitado)"),
]


def render():
    df = load_data()
    contador = iniciar_filtros()

    mask = filtro_edicion(df, "participacion_edicion")

    df = aplicar_filtros(df, mask, contador)

    st.title("Participación social y política")
    st.caption("Participación en organizaciones, voto en Argentina y en el país de origen, y percepción sobre la vida en Argentina.")

    grafico_barras(df, "participacion_organizacion", "Participación en organizaciones sociales, comunitarias o políticas")

    no_participa = df["participacion_organizacion"] != "No"
    grafico_multiseleccion(
        df[no_participa], TIPO_ORGANIZACION,
        "Tipo de organización en la que participa",
        "Qué % de quienes participan en alguna organización declaró cada tipo (pregunta de selección múltiple: una persona puede participar en más de un tipo).",
    )

    col1, col2 = st.columns(2)
    with col1:
        grafico_barras(df, "voto_elecciones_locales", "Votó en elecciones locales en Argentina")
    with col2:
        grafico_barras(df, "voto_elecciones_pais_origen", "Votó en elecciones de su país de origen")

    no_voto_local = df["voto_elecciones_locales"] != "Sí"
    grafico_multiseleccion(
        df[no_voto_local], MOTIVOS_NO_VOTO_LOCAL,
        "Motivos de no participación en elecciones locales",
        "Qué % de quienes no votaron declaró cada motivo (pregunta de selección múltiple: una persona puede tener más de un motivo).",
    )

    grafico_barras(df, "motivo_no_voto_extranjero", "Motivo de no participación en elecciones del país de origen", horizontal=True)
