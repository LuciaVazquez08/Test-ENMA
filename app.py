import streamlit as st

from enma_palette import inject_fonts
from views import (
    control,
    discriminacion_violencia,
    documentacion,
    educacion,
    familia_hogar,
    hijos_educacion,
    participacion,
    salud,
    sociodemografico,
    trabajo,
    trayectoria_migratoria,
    vivienda,
)

st.set_page_config(
    page_title="ENMA - Tablero",
    page_icon="🌎",
    layout="wide",
)
inject_fonts()

paginas = [
    st.Page(sociodemografico.render, title="Datos sociodemográficos", icon="🧑‍🤝‍🧑", url_path="datos-sociodemograficos", default=True),
    st.Page(trayectoria_migratoria.render, title="Trayectoria y proyecto migratorio", icon="🧭", url_path="trayectoria-y-proyecto-migratorio"),
    st.Page(documentacion.render, title="Situación documentaria", icon="🪪", url_path="situacion-documentaria"),
    st.Page(familia_hogar.render, title="Situación familiar y hogar", icon="👪", url_path="situacion-familiar-y-hogar"),
    st.Page(hijos_educacion.render, title="Hijos/as y educación", icon="🧒", url_path="hijos-y-educacion"),
    st.Page(salud.render, title="Derecho a la salud", icon="🏥", url_path="derecho-a-la-salud"),
    st.Page(vivienda.render, title="Vivienda", icon="🏠", url_path="vivienda"),
    st.Page(educacion.render, title="Trayectoria educativa", icon="🎓", url_path="trayectoria-educativa-adultos"),
    st.Page(trabajo.render, title="Situación socioeconómica", icon="💼", url_path="situacion-socioeconomica"),
    st.Page(discriminacion_violencia.render, title="Discriminación y violencia", icon="⚠️", url_path="discriminacion-y-violencia"),
    st.Page(participacion.render, title="Participación social y política", icon="🗳️", url_path="participacion-social-y-politica"),
    st.Page(control.render, title="Control", icon="🛠️", url_path="control"),
]

navegacion = st.navigation(paginas)
navegacion.run()
