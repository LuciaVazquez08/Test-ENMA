import base64
from pathlib import Path

import streamlit as st

RAIZ = Path(__file__).resolve().parent.parent
LOGO_ENMA = RAIZ / "assets" / "logo_enma.png"
LOGO_CIAI = RAIZ / "assets" / "logo_ciai.jpg"

EDICIONES = """
| | ENMA 2020 | ENMA 2023 |
|---|---:|---:|
| Casos | 3.114 | 4.679 |
| Variables | 202 | 228 |
| Preguntas del cuestionario | 62 | 73 |
| Regiones de residencia | 6 más una categoría residual | 6 |
| Ponderador de estimaciones totales | `pesos_para_estimaciones_totales` | `weightvec` |
| Ponderador por nacionalidad | `pesos_para_estimaciones_por_nacionalidad` | `weightvec_0` |
"""


def _data_uri(ruta: Path, tipo: str) -> str:
    return f"data:{tipo};base64,{base64.b64encode(ruta.read_bytes()).decode()}"


def render():
    """Pantalla de presentación de la encuesta. El texto retoma casi textual el README de
    https://github.com/natdebandi/ENMA."""
    # Logos en una fila flexible (HTML) para que mantengan su proporción también en pantallas
    # angostas, donde las columnas de Streamlit se apilan y agrandan el logo cuadrado.
    st.markdown(
        f"""
        <div style="display:flex; justify-content:space-between; align-items:center;
                    gap:1.5rem; flex-wrap:wrap; margin:1.5rem 0 1rem 0;">
            <img src="{_data_uri(LOGO_ENMA, 'image/png')}" alt="ENMA - Encuesta Nacional Migrante de Argentina"
                 style="height:80px; max-width:100%; object-fit:contain;">
            <img src="{_data_uri(LOGO_CIAI, 'image/jpeg')}" alt="Centro de Inteligencia Artificial Interdisciplinario - ECyT UNSAM"
                 style="height:120px; object-fit:contain;">
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True, key="seccion_que_es"):
        st.subheader("¿Qué es la ENMA?")
        st.markdown(
            "La ENMA es una iniciativa de producción de datos primarios que releva las condiciones de "
            "vida en las que se encuentran las personas migrantes, solicitantes de asilo y refugiadas "
            "que viven en la República Argentina, sus trayectorias y su nivel de acceso efectivo a "
            "derechos en todos los órdenes sociales. Se desarrolla desde la Red de Investigaciones en "
            "Derechos Humanos del CONICET en conjunto con organizaciones de migrantes, con un enfoque "
            "práctico de derechos humanos, y se realiza cada tres años desde 2020."
        )

    with st.container(border=True, key="seccion_ediciones"):
        st.subheader("Las ediciones")
        # En pantallas angostas la tabla se desplaza horizontalmente en vez de desbordar el recuadro.
        st.markdown(
            "<style>.st-key-seccion_ediciones table { display: block; overflow-x: auto; }</style>",
            unsafe_allow_html=True,
        )
        st.markdown(EDICIONES)

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True, key="seccion_tablero"):
            st.subheader("Sobre este tablero")
            st.markdown(
                "- Usa el ponderador por nacionalidad: permite ver diferencias entre nacionalidades "
                "y dentro de cada una (solo para las nacionalidades con más casos).\n"
                "- La fila **Población total** y los cruces que no son por nacionalidad usan el "
                "ponderador de estimaciones totales.\n"
                "- Las bases de 2020 y 2023 no son integrables de manera automática (los "
                "cuestionarios difieren en secciones, preguntas y opciones): cada edición se "
                "muestra por separado."
            )
    with col2:
        with st.container(border=True, key="seccion_marco"):
            st.subheader("Marco de uso")
            st.markdown(
                "La encuesta se diseñó desde una perspectiva de derechos humanos. Las versiones "
                "públicas no incluyen identificadores directos, geografía por debajo de la región ni "
                "campos de texto libre. Los datos se distribuyen bajo licencia "
                "[Creative Commons Atribución 4.0 Internacional](https://creativecommons.org/licenses/by/4.0/deed.es)."
            )

    with st.container(border=True, key="seccion_datos"):
        st.subheader("Datos, documentación y contacto")
        st.markdown(
            "- Sitio de la ENMA: https://www.encuestamigrante.ar/\n"
            "- Bases públicas, documentación y código: https://github.com/natdebandi/ENMA\n"
            "- Documento metodológico: [enlace pendiente]\n"
            "- Anuario Migratorio Argentino 2024 (edición 2023): "
            "[anuario_enma_2023_vf.pdf](https://www.encuestamigrante.ar/wp-content/uploads/documentos/anuario_enma_2023_vf.pdf)\n"
            "- Cómo citar: según el [README del repositorio](https://github.com/natdebandi/ENMA#cómo-citar)\n"
            "- Consultas sobre el tablero: [ndebandi@unsam.edu.ar](mailto:ndebandi@unsam.edu.ar)"
        )
