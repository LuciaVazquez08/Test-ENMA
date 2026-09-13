"""
Paleta de marca extraída de encuestamigrante.ar (bloque :root del CSS del sitio).

Uso típico en un dashboard Streamlit:

    import streamlit as st
    from enma_palette import COLORS, CHART_SEQUENCE, inject_fonts

    st.set_page_config(page_title="ENMA", layout="wide")
    inject_fonts()  # aplica Syncopate a los títulos vía CSS

    st.markdown(f"<h1 style='color:{COLORS['text']}'>Encuesta Nacional Migrante</h1>",
                unsafe_allow_html=True)

    fig = px.bar(df, x="region", y="valor", color_discrete_sequence=CHART_SEQUENCE)
"""

COLORS = {
    "yellow_1": "#FFC456",
    "yellow_2": "#FFA602",
    "orange_1": "#FF7900",   
    "orange_2": "#FF4900",

    "blue": "#027BFF",
    "blue_dark": "#0055CC",
    "blue_pale": "#D6EAFF",
    "blue_accent": "#3DA0FF",

    "text": "#0F0F1A",    
    "text_2": "#2E2E4A",  
    "text_3": "#6B6B8A",  

    "border": "#E6E9F2",
    "background": "#FFFFFF",
    "background_alt": "#F5F7FB",
}

CHART_SEQUENCE = [
    COLORS["orange_1"],
    COLORS["blue"],
    COLORS["yellow_2"],
    COLORS["blue_accent"],
    COLORS["orange_2"],
    COLORS["yellow_1"],
    COLORS["blue_dark"],
    COLORS["text_3"],
]


FONT_HEADINGS = '"Syncopate", sans-serif'   
FONT_BODY = '"DM Sans", sans-serif'         


def inject_fonts() -> None:
    """
    Inyecta las fuentes de Google Fonts y aplica Syncopate a los títulos
    y DM Sans al resto de la app. Llamar una sola vez, después de st.set_page_config().
    Requiere: import streamlit as st (se importa acá adentro para no forzar
    la dependencia si solo se usan los diccionarios de colores).
    """
    import streamlit as st

    st.markdown(
        f"""
        <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Syncopate:wght@400;700&display=swap" rel="stylesheet">
        <style>
        html, body, [class*="css"] {{
            font-family: {FONT_BODY};
            color: {COLORS['text']};
        }}
        h1{{
            font-family: {FONT_HEADINGS} !important; 
            letter-spacing: 0.02em;
            text-transform: uppercase;
        }}
        .block-container {{
            padding-top: 1rem;
            padding-bottom: 1rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
