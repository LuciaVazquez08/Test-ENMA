# Encuesta Nacional de Migrantes Argentina (ENMA) 🇦🇷

Este proyecto consiste en el desarrollo de un tablero interactivo diseñado con *Streamlit* para la exploración y análisis de los datos de la **Encuesta Nacional de Migrantes Argentina (ENMA)** en sus ediciones 2020 y 2023.

El objetivo principal es proporcionar a investigadores, organismos y al público general una herramienta autónoma y sencilla para obtener **metricas** y visualizar **KPIs** (Indicadores Clave de Desempeño) sobre las trayectorias migratorias, acceso a derechos y condiciones de vida de la población migrante.

🔗 **Fuente oficial de datos:** [encuestamigrante.ar](https://www.encuestamigrante.ar/)

🔗 **Tablero:** [tablero Encuesta Nacional Migrante de Argentina](https://tablero-encuesta-nacional-migrante-de-argentina.streamlit.app/)
---

## 📊 Objetivos del Proyecto

* **Centralización:** Unificar los datos de las encuestas 2020 y 2023.
* **Armonización:** Resolver las discrepancias entre preguntas no repetidas o modificadas entre ambas ediciones mediante un proceso de ETL a partir de las preguntas que se corresponden entre ambos años.
* **Autonomía:** Permitir que usuarios sin conocimientos técnicos en ciencia de datos puedan filtrar y cruzar variables de forma interactiva.
* **Visualización:** Presentar indicadores complejos a través de gráficos dinámicos y mapas.

## 🛠️ Stack Tecnológico

* **Lenguaje:** Python
* **Procesamiento (ETL):** Pandas y NumPy.
* **Visualización:** Plotly, Seaborn, Matplotlib, HoloViews, hvPlot.
* **Framework de Aplicación:** Streamlit.

## 📁 Estructura del Repositorio

- `app.py`: Aplicación principal de Streamlit.
- `scripts/`: Scripts de Python para la limpieza y transformación de datos.
- `data/raw/`: Datasets originales (2020, 2023 y matriz de coincidencia).
- `data/processed/`: Dataset final armonizado utilizado por el tablero.
- `views/`: Las distintas paginas dentro del tablero..
- `requirements.txt`: Lista de dependencias con versiones específicas.

## ⚙️ Instalación y Reproducibilidad

Para ejecutar este proyecto localmente, sigue estos pasos:

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/LuciaVazquez08/ENMA.git](https://github.com/LuciaVazquez08/ENMA.git)
   cd ENMA