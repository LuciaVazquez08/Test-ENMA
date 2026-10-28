# Encuesta Nacional de Migrantes Argentina (ENMA) 🇦🇷

Este proyecto consiste en el desarrollo de un tablero interactivo diseñado con *Streamlit* para la exploración y análisis de los datos de la **Encuesta Nacional de Migrantes Argentina (ENMA)** en sus ediciones 2020 y 2023.

El objetivo principal es proporcionar a investigadores, organismos y al público general una herramienta autónoma y sencilla para obtener **metricas** y visualizar **KPIs** (Indicadores Clave de Desempeño) sobre las trayectorias migratorias, acceso a derechos y condiciones de vida de la población migrante.

🔗 **Fuente oficial de datos:** [encuestamigrante.ar](https://www.encuestamigrante.ar/)

🔗 **Tablero:** [tablero Encuesta Nacional Migrante de Argentina](https://test-enma-bi4bwfx775usbxawazftxp.streamlit.app/)
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
- `data/raw/`: Bases públicas anonimizadas de la ENMA, tal como se publican en [natdebandi/ENMA](https://github.com/natdebandi/ENMA): `ENMA2020_anonima_v1.csv` ([release datos-2020-v1](https://github.com/natdebandi/ENMA/releases/tag/datos-2020-v1)) y `ENMA2023_anonima_v4.csv` ([release datos-2023-v3](https://github.com/natdebandi/ENMA/releases/tag/datos-2023-v3)). No incluyen identificadores, fecha, provincia, localidad, barrio ni textos libres de "Otros"; el nivel territorial disponible es la región.
- `data/processed/`: Dataset final armonizado utilizado por el tablero.
- `views/`: Las distintas paginas dentro del tablero (`inicio.py` es la página inicial de presentación de la encuesta).
- `assets/`: Logos de la ENMA y del CIAI (ECyT-UNSAM) usados en la página inicial, y el ícono de la pestaña del navegador (`favicon_enma.png`).
- `requirements.txt`: Lista de dependencias con versiones específicas.

## 📐 Nota metodológica: ponderadores

Debajo de cada gráfico se indica el ponderador usado y el N (cantidad de personas encuestadas, sin ponderar, con dato en la variable graficada). Los porcentajes se muestran sin decimales.

**Los países del gráfico no coinciden con los que tienen ponderador intra nacionalidad.** Según la documentación de las bases, el ajuste intra nacionalidad solo se calculó para diez nacionalidades, las mismas en ambas ediciones: Venezuela, Paraguay, Bolivia, Perú, Colombia, Chile, Brasil, Uruguay, Italia y España. En cambio, los países que el tablero muestra por separado salen de la cantidad de casos de cada encuesta, y no coinciden con esa lista:

- **2020:** se muestran los diez países con más casos, entre ellos Senegal, Haití y Ecuador. Esos tres no tienen ajuste propio: su ponderador intra nacionalidad vale 1 para todos los casos, así que sus filas muestran la distribución de la muestra sin ponderar. Uruguay, Italia y España sí tienen ajuste, pero quedan dentro de "Otro".
- **2023:** se muestran exactamente las diez nacionalidades con ajuste propio.
- **"Otro" (ambos años):** junta nacionalidades con ponderador 1 y, en 2023, valores del ponderador intra nacionalidad que no corresponden a un ajuste de ese grupo. Su distribución debe leerse con cautela.

Por decisión del tablero, todas las filas por país usan igualmente el ponderador intra nacionalidad, aunque valga 1, y solo la fila "Población migrante total" usa el general.

## ⚙️ Instalación y Reproducibilidad

Para ejecutar este proyecto localmente, sigue estos pasos:

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/LuciaVazquez08/ENMA.git](https://github.com/LuciaVazquez08/ENMA.git)
   cd ENMA