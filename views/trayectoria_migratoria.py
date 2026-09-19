import streamlit as st

from data_utils import (
    aplicar_filtros,
    filtro_edicion,
    grafico_barras,
    grafico_multiseleccion,
    iniciar_filtros,
    load_data,
)

MOTIVOS_MIGRACION = [
    ("motivo_mejor_trabajo", "Mejor trabajo"),
    ("motivo_necesidades_basicas", "Necesidades básicas"),
    ("motivo_estudios_nuevas_experiencias", "Estudios o nuevas experiencias"),
    ("motivo_violencias_persecuciones", "Violencias o persecuciones"),
    ("motivo_familiar", "Motivos familiares"),
    ("motivo_otro", "Otro"),
]


def render():
    df = load_data()
    contador = iniciar_filtros()

    mask = filtro_edicion(df, "trayectoria_edicion")

    df = aplicar_filtros(df, mask, contador)

    st.title("Trayectoria migratoria")
    st.caption("Motivos de la migración, tiempo de residencia y movilidad dentro y fuera del país.")

    grafico_multiseleccion(
        df, MOTIVOS_MIGRACION,
        "Principales motivos para migrar a Argentina",
        "Qué % de la población declaró cada motivo entre sus razones para migrar (pregunta de selección múltiple: una persona puede tener más de un motivo).",
    )

    col1, col2 = st.columns(2)
    with col1:
        grafico_barras(df, "vivio_otra_provincia", "Vivió antes en otra provincia argentina")
    with col2:
        grafico_barras(df, "mudanza_futura", "Proyecto migratorio para los próximos años")

    col3, col4 = st.columns(2)
    with col3:
        grafico_barras(df, "migracion_reciente", "Migración reciente (llegada en los últimos años)")
    with col4:
        grafico_barras(df, "situacion_vida_argentina", "Situación de vida en Argentina en los últimos dos años")
