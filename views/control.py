import re
from pathlib import Path

import streamlit as st

from data_utils import aplicar_filtros, filtro_edicion, formatear_n, iniciar_filtros, load_data

RAIZ = Path(__file__).resolve().parent.parent


def _archivos_a_revisar() -> list[Path]:
    archivos = [RAIZ / "app.py", RAIZ / "data_utils.py"]
    archivos += [
        f for f in (RAIZ / "views").glob("*.py")
        if f.name not in ("control.py", "__init__.py")
    ]
    return archivos


def _columnas_usadas(columnas) -> set[str]:
    """Una columna se considera usada si su nombre aparece como string literal
    (entre comillas) en el código de app.py, data_utils.py o cualquier otra view."""
    codigo = "\n".join(
        f.read_text(encoding="utf-8") for f in _archivos_a_revisar() if f.exists()
    )
    return {
        columna for columna in columnas
        if re.search(rf'["\']{re.escape(columna)}["\']', codigo)
    }


def render():
    df = load_data()
    contador = iniciar_filtros()

    mask = filtro_edicion(df, "control_edicion")

    df = aplicar_filtros(df, mask, contador)

    st.title("Control de variables")
    st.caption(
        "Variables del dataset que todavía no se usan en ninguna pestaña del tablero: "
        "opciones disponibles y cantidad de casos (en valor absoluto) de cada una."
    )

    usadas = _columnas_usadas(df.columns)
    columnas_no_usadas = [c for c in df.columns if c not in usadas]

    st.caption(f"{len(columnas_no_usadas)} de {len(df.columns)} columnas del dataset sin usar todavía.")

    for columna in columnas_no_usadas:
        conteo = df[columna].value_counts(dropna=False).reset_index()
        conteo.columns = ["Opción", "Cantidad"]
        conteo["Opción"] = conteo["Opción"].fillna("Sin dato").astype(str)
        with st.expander(f"{columna} ({len(conteo)} opciones)"):
            st.dataframe(conteo, use_container_width=True, hide_index=True)
            st.caption(f"Datos sin ponderar. N = {formatear_n(len(df))}")
