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
    filtro_cruce(df, "trayectoria_cruce")

    st.title("Trayectoria migratoria")
    st.caption("Motivos de la migración, tiempo de residencia y movilidad dentro y fuera del país.")

    grafico_multiseleccion(
        df, MOTIVOS_MIGRACION,
        "Distribución por motivos para migrar a Argentina",
        "Qué % de la población declaró cada motivo entre sus razones para migrar (pregunta de selección múltiple: una persona puede tener más de un motivo).",
    )

    col1, col2 = st.columns(2)
    with col1:
        grafico_barras(df, "vivio_otra_provincia", "Distribución por residencia previa en otra provincia argentina")
    with col2:
        grafico_barras(df, "mudanza_futura", "Distribución por proyecto migratorio para los próximos años")

    col3, col4 = st.columns(2)
    with col3:
        grafico_barras(df, "migracion_reciente", "Distribución por migración reciente (llegada en los últimos años)")
    with col4:
        grafico_barras(df, "situacion_vida_argentina", "Distribución por situación de vida en Argentina en los últimos dos años")
