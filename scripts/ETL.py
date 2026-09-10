import pandas as pd
import numpy as np
import random
import unicodedata
import re
import openpyxl
import os

def normalizar_idioma(valor):
    if pd.isna(valor):
        return np.nan
    v = str(valor).strip().lower()
    
    # Español / Castellano
    if any(x in v for x in ['español', 'castellano', 'espa']):
        return 'Español / Castellano'
    # Guaraní
    if 'guarani' in v or 'guaraní' in v or 'guaranu' in v:
        return 'Guaraní'
    # Quechua
    if 'quechua' in v or 'kichua' in v:
        return 'Quechua'
    # Aymara
    if 'aymara' in v or 'ayamara' in v or 'áyáman' in v:
        return 'Aymara'
    # Creole
    if 'creole' in v or 'criollo' in v or 'creol' in v or 'kreyol' in v:
        return 'Creole haitiano'
    # Wolof
    if 'wolof' in v or 'wilof' in v or 'wollof' in v:
        return 'Wolof'
    # Wayuunaiki
    if 'wayuu' in v or 'wayu' in v:
        return 'Wayuunaiki'
    # Neerlandés
    if 'neerland' in v or 'holland' in v or 'hollandes' in v:
        return 'Neerlandés'
    # Alemán
    if 'alem' in v:
        return 'Alemán'
    # Ruso
    if v in ['ruso', 'ruso ']:
        return 'Ruso'
    # Italiano
    if 'italian' in v:
        return 'Italiano'
    # Portugués
    if 'portugu' in v:
        return 'Portugués'
    # Francés
    if 'franc' in v:
        return 'Francés'
    # Inglés
    if 'ingl' in v:
        return 'Inglés'
    # Árabe
    if 'arab' in v or 'arabe' in v or 'darija' in v:
        return 'Árabe'
    # Chino
    if 'chin' in v or '\u4e2d\u6587' in v or '琉球' in v:
        return 'Chino'
    # Catalán
    if 'catal' in v:
        return 'Catalán'
    # Gallego
    if 'gallego' in v:
        return 'Gallego'
    # Turco
    if 'turco' in v:
        return 'Turco'
    # Sueco
    if 'sueco' in v:
        return 'Sueco'
    # Armenio
    if 'armenio' in v:
        return 'Armenio'
    # Búlgaro
    if 'bulgar' in v or 'búlgar' in v:
        return 'Búlgaro'
    # Griego
    if 'grieg' in v or 'griega' in v or 'griego' in v:
        return 'Griego'
    # Serbio
    if 'serbio' in v:
        return 'Serbio'
    # Esloveno
    if 'esloveno' in v:
        return 'Esloveno'
    # Punjabi
    if 'punjabi' in v:
        return 'Punjabi'
    # Urdu
    if 'urdu' in v:
        return 'Urdu'
    # Hindi
    if 'hindi' in v:
        return 'Hindi'
    # Ucraniano
    if 'ucraniano' in v or 'ucrani' in v:
        return 'Ucraniano'
    # Lingala
    if 'lingala' in v:
        return 'Lingala'
    # Persa
    if 'persa' in v:
        return 'Persa'
    # Lituano
    if 'lituano' in v:
        return 'Lituano'
    # Polaco
    if 'polaco' in v:
        return 'Polaco'
    # Kabyle
    if 'kabyle' in v:
        return 'Kabyle'
    # Mapuche
    if 'mapuche' in v or 'mapuzungun' in v:
        return 'Mapuche (Mapuzungun)'
    # Twi / Akan
    if v in ['twi', 'akan']:
        return 'Twi / Akan'
    # Serere
    if 'serere' in v or 'serrere' in v or 'sérère' in v:
        return 'Serere'
    # Toucouleur
    if 'toucouleur' in v:
        return 'Toucouleur'
    if v in ['no se', 'no sé', 'kaf']:
        return np.nan

    return str(valor).strip().title()

def resolver_idioma(row, col_principal, col_otro, valor_otro):
    principal = row[col_principal]
    if principal == valor_otro:
        return normalizar_idioma(row[col_otro])
    return normalizar_idioma(principal)

def filtrar_por_frecuencia(df, col, minimo=5):
    conteo = df[col].value_counts()
    validos = conteo[conteo >= minimo].index
    df[col] = df[col].where(df[col].isin(validos), other='Otro')
    return df

def mapear_hijos_2023(row):
    tiene_hijos = row["q29_hijos_num"]
    arg = row["q30_hijos_arg"]
    ext = row["q30_hijos_exterior"]
    
    def valido(x):
        return x if (pd.notna(x) and x >= 0) else np.nan
    
    arg_v = valido(arg)
    ext_v = valido(ext)
      
    if tiene_hijos == "No":
        return "No, no tengo hijos"
    
    if tiene_hijos == "Si":
        tiene_arg = pd.notna(arg_v) and arg_v > 0
        tiene_ext = pd.notna(ext_v) and ext_v > 0
        
        if tiene_arg and tiene_ext:
            return "Sí, algunos nacidos en Argentina y otros/as en otro país"
        elif tiene_arg:
            return "Sí, nacidos en Argentina"
        elif tiene_ext:
            return "Sí, nacidos en otro país"
        else:
            return "Prefiero no responder"
    
    return np.nan


def run_etl():
    df_2020 = pd.read_csv('data/raw/ENMA_2020.csv', sep=';')
    df_2023 = pd.read_csv('data/raw/ENMA_2023.csv', sep=';', low_memory=False)

    df_2020.rename(columns={'Id': 'ID'}, inplace=True)
    
    #EDAD
    df_2020['edad_agrupada'] = pd.cut(df_2020['q2_edad'], bins=[0, 17, 29, 44, 64, 10000], labels=['0-17', '18-29', '30-44', '45-64', '65+'])
    df_2020.drop(columns=['q2_edad'], inplace=True)

    df_2023['edad_agrupada'] = pd.cut(df_2023['q2_edad'], bins=[0, 17, 29, 44, 64, 10000], labels=['0-17', '18-29', '30-44', '45-64', '65+'])
    df_2023.drop(columns=['q2_edad'], inplace=True)
    df_2023.drop(columns=['edad_agrup'], inplace=True)

    #NACIONALIDAD
    top10_nacionalidades = df_2020['nacionalidad_c'].value_counts().head(10).index
    df_2020['pais_nacimiento_var'] = df_2020['nacionalidad_c'].where(df_2020['nacionalidad_c'].isin(top10_nacionalidades)).fillna('Otro')
    df_2020.drop(columns=['q3_pais', 'q3_otro', 'nacionalidad_c'], inplace=True)

    df_2023['pais_nacimiento_var'] = df_2023['nacionalidad_var'].fillna('Otro')
    df_2023.drop(columns=["q3_pais_nacimiento", "q3_pais_otro", "nacionalidad_var"], inplace=True)

    #GENERO
    df_2020["genero_agrup"] = np.where(df_2020['q1_genero'] == 'Mujer', df_2020['q1_genero'], np.where(df_2020['q1_genero'] == 'Hombre', 'Varón', np.where(df_2020['q1_genero'] == 'No quiere informar', 'Prefiero no responder', 'Otro género')))
    df_2020.drop(columns=['q1_genero', 'Genero_i'], inplace=True)
    df_2023.drop(columns=['q4_genero'], inplace=True)

    #IDIOMA
    df_2020['idioma'] = df_2020.apply(lambda r: resolver_idioma(r, 'q5_idioma', 'q5_otro', 'Otro (especifique)'), axis=1)
    df_2023['idioma'] = df_2023.apply(lambda r: resolver_idioma(r, 'q6_idioma', 'q6_otro', 'Otro'), axis=1)
    
    df_2020 = filtrar_por_frecuencia(df_2020, 'idioma')
    df_2023 = filtrar_por_frecuencia(df_2023, 'idioma')

    conteo_total = (df_2020['idioma'].value_counts().add(df_2023['idioma'].value_counts(), fill_value=0)    )
    conteo_total = conteo_total.drop(labels='Otro', errors='ignore')
    top7 = conteo_total.nlargest(7).index.tolist()

    df_2020['idioma_var'] = df_2020['idioma'].where(df_2020['idioma'].isin(top7), other='Otro')
    df_2023['idioma_var'] = df_2023['idioma'].where(df_2023['idioma'].isin(top7), other='Otro')


    #DESCENDENCIA
    df_2020["descendencia"] = df_2020['q4_descendientes']
    df_2020.replace({'descendencia': {'Asiático/a o descendiente de asiático/a.':'Descendencia Asiática', np.nan: 'Ninguna de las anteriores', 'Indígena o descendiente de pueblos indígenas u originarios': 'Descendencia Indígena', 'Afrodescendiente, africano o afroargentino/a': 'Afrodescendiente'}}, inplace=True)
    df_2020.drop(columns=['q4_descendientes'], inplace=True)

    df_2023["descendencia"] = np.where(df_2023['q5_descendencia_afro'] == 1, 'Afrodescendiente',np.where(df_2023['q5_descendencia_indigena'] == 1, 'Descendencia Indígena', np.where(df_2023['q5_descendencia_asiatica'] == 1, 'Descendencia Asiática', 'Ninguna de las anteriores')))
    df_2023.drop(columns=['q5_descendencia_afro', 'q5_descendencia_indigena', 'q5_descendencia_asiatica', 'q5_descendencia_ninguno', 'q5_descendencia_otro'], inplace=True)

    # REGION

    PARTIDOS_AMBA = {
        "tigre", "san fernando", "san isidro", "vicente lopez", "vicente lópez",
        "general san martin", "general san martín", "gral san martin", "gral. san martín",
        "tres de febrero", "hurlingham", "ituzaingo", "ituzaingó",
        "moron", "la matanza", "merlo", "moreno",
        "jose c paz", "josé c paz", "jose c. paz", "josé c. paz",
        "malvinas argentinas", "san miguel",
        "avellaneda", "lanus", "lanús", "quilmes", "berazategui",
        "florencio varela", "almirante brown", "lomas de zamora",
        "esteban echeverria", "esteban echeverría", "ezeiza",
    }

    PROVINCIA_A_REGION = {
        "Ciudad de Buenos Aires (CABA)": "AMBA",
        # Buenos Aires (Provincia) → se resuelve aparte
        "Córdoba":           "Región Pampeana",
        "Santa Fe":          "Región Pampeana",
        "Entre Ríos":        "Región Pampeana",
        "La Pampa":          "Región Pampeana",
        "Mendoza":           "Cuyo",
        "San Juan":          "Cuyo",
        "San Luis":          "Cuyo",
        "Río Negro":         "Patagonia",
        "Neuquén":           "Patagonia",
        "Chubut":            "Patagonia",
        "Santa Cruz":        "Patagonia",
        "Tierra del Fuego, Antártida e Islas del Atlántico Sur": "Patagonia",
        "Misiones":          "NEA",
        "Chaco":             "NEA",
        "Corrientes":        "NEA",
        "Formosa":           "NEA",
        "Salta":             "NOA",
        "Jujuy":             "NOA",
        "Tucumán":           "NOA",
        "Santiago del Estero": "NOA",
        "Catamarca":         "NOA",
        "La Rioja":          "NOA",
    }

    def normalize(text: str) -> str:
        if not isinstance(text, str):
            return ""
        text = text.lower().strip()
        text = unicodedata.normalize("NFD", text)
        text = "".join(c for c in text if unicodedata.category(c) != "Mn")
        text = re.sub(r"[.\-_]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def is_amba_localidad(localidad: str) -> bool:
        n = normalize(localidad)
        return any(
            n == p or n in p or p in n
            for p in PARTIDOS_AMBA  # ya están normalizados en el set
        )

    def get_region(provincia: str, localidad: str) -> str | None:
        if provincia == "Buenos Aires (Provincia)":
            return "AMBA" if is_amba_localidad(localidad) else "Región Pampeana"
        return PROVINCIA_A_REGION.get(provincia)
    
    df_2020["region"] = df_2020.apply(lambda r: get_region(r["q7_provincia_res"], r["q8_localidad"]), axis=1)
    df_2020.drop(columns=['q7_provincia_res', 'q8_localidad'], inplace=True)

    df_2023['region'] = df_2023['region_amba_agrup']
    df_2023.drop(columns=['region_amba_agrup', 'q8_provincia_res', 'q9_localidad', 'q10_barrio'], inplace=True)

    #VIVIO EN OTRA PROVINCIA
    df_2020.rename(columns={'q9_otra_provincia': 'vivio_otra_provincia'}, inplace=True)
    df_2023.rename(columns={'q11_otra_provincia': 'vivio_otra_provincia'}, inplace=True)

    #MUDANZA
    df_2020.replace({'q12_ida_retorno': {'No, me establecí aquí': 'No', 'No lo sé':'No sé', 'Prefiero no contestar': 'Prefiero no responder'}}, inplace=True)
    df_2020.rename(columns={'q12_ida_retorno': 'mudanza_futura'}, inplace=True)

    df_2023["mudanza_futura"] = np.where(df_2023['q15_mudanza'] == 'No', 'No',
                                         np.where(df_2023['q15_mudanza'] == 'No sé', 'No sé',
                                         np.where(df_2023['q16_mudanza_lugar'] == 'Prefiero no responder', 'Prefiero no responder',
                                         np.where(df_2023['q16_mudanza_lugar'] == 'A otro país que no es mi país de origen', 'Sí, a otro país que no es mi país de origen',
                                        np.where(df_2023['q16_mudanza_lugar'] == 'A mi país de origen', 'Sí, a mí país de origen',
                                        np.where(df_2023['q16_mudanza_lugar'] == 'A otra provincia en Argentina', 'Sí, a otra provincia en Argentina', 'Sí, a otra ciudad en Argentina'
                                        ))))))
    
    df_2023.drop(columns=['q15_mudanza', 'q16_mudanza_lugar'], inplace=True)

    #TIEMPO DE RESIDENCIA
    df_2020["periodo_residencia"] = df_2020['tiempo_i']
    df_2020["migracion_reciente"] = np.where(df_2020['q10_anios_res'] == 'Entre 1 y 2 años', 'si', np.where(df_2020['q10_anios_res'] == 'Menos de 1 año', 'si', 'no'))
    df_2020.drop(columns=['q10_anios_res', 'tiempo_i'], inplace=True)

    df_2023["periodo_residencia"] = df_2023['tiempo_residencia_agrup'].replace({'2 10 años o +': 'Más de 10 años', '1 De 6 a 9 años': 'Entre 5 y 9 años', '0 Hasta 5 años': 'Hasta 5 años'})
    df_2023["migracion_reciente"] = np.where(df_2023['q13_anio_llegada'] == 2022, 'si', np.where(df_2023['q13_anio_llegada'] == 2021, 'si', np.where(df_2023['q13_anio_llegada'] == 2023, 'si', 'no')))
    df_2023.drop(columns=['q13_anio_llegada','tiempo_residencia_agrup'], inplace=True)

    #MOTIVO MIGRATORIO
    df_2020["motivo_estudios_nuevas_experiencias"] = np.where((df_2020['q11_motivos_estudio'] == 'Para estudiar') | (df_2020['q11_motivos_experiencias'] == 'Para tener nuevas experiencias'), 1, 0)
    df_2020["motivo_mejor_trabajo"] = np.where(df_2020['q11_motivos_trabajo'] == 'Por trabajo', 1, 0)
    df_2020["motivo_violencias_persecuciones"] = np.where((df_2020['q11_motivos_discriminacion'] == 'Por violencia y/o discriminación (racismo, pertenencia étnica, de género)') | (df_2020['q11_motivos_violencias'] == 'Por violencias y/o persecuciones políticas'), 1, 0)
    df_2020["motivo_necesidades_basicas"] = np.where((df_2020['q11_motivos_salud'] == 'Por problemas de salud (para tratamiento)') | (df_2020['q11_motivos_sit_economica'] == "Por la situación económica/no podía cubrir mis necesidades básicas"), 1, 0)
    df_2020["motivo_familiar"] = np.where((df_2020['q11_motivos_familia'] == 'Para reencontrarme con mi familia') | (df_2020['q11_motivos_proyecto_otro'] == 'Para acompañar el proyecto de trabajo o estudio de otro/a'),1,0)
    df_2020.rename(columns={'q11_motivos_otros': 'motivo_otro'}, inplace=True)

    df_2020.drop(columns=['q11_motivos_proyecto_otro','q11_motivos_familia','q11_motivos_estudio', 'q11_motivos_experiencias', 'q11_motivos_trabajo', 'q11_motivos_discriminacion', 'q11_motivos_violencias', 'q11_motivos_salud', 'q11_motivos_sit_economica'], inplace=True)
    detalle = df_2023["q14_motivos_otros_detalle"].fillna('').str.lower()

    df_2023["motivo_estudios_nuevas_experiencias"] = np.where((df_2023['q14_motivos_estudio'] == 1) | (df_2023['q14_motivos_nuevas_experiencias'] == 1), 1, 0)
    df_2023['motivo_estudios_nuevas_experiencias'] = np.where(
        (df_2023['motivo_estudios_nuevas_experiencias'] == 1) |
        detalle.str.contains(
            'estudi|doctorado|seminar|jesuita|religios|intercambio|cultura|viajar|experiencia|idioma',
            regex=True
        ),
        1, 0
    )
    df_2023['motivo_mejor_trabajo'] = np.where(
        (df_2023['q14_motivos_mejor_trabajo'] == 1) |
        detalle.str.contains(
            'trabajo|laboral|empresa|expatri|designación|startup|camionero',
            regex=True
        ),
        1, 0
    )
    df_2023["motivo_violencias_persecuciones"] = np.where((df_2023['q14_motivos_violencia_genero'] == 1) | (df_2023['q14_motivos_orientacion_sexual'] == 1) | (df_2023['q14_motivos_persecucion'] == 1), 1, 0)
    df_2023['motivo_violencias_persecuciones'] = np.where(
        (df_2023['motivo_violencias_persecuciones'] == 1) |
        detalle.str.contains(
            'violencia|guerra|dictadura|chavismo|terrorismo|persec|xenofobia|inseguridad|comunismo',
            regex=True
        ),
        1, 0
    )
    df_2023["motivo_necesidades_basicas"] = np.where((df_2023['q14_motivos_salud'] == 1) | (df_2023['q14_motivos_necesidades_basicas'] == 1), 1, 0)
    df_2023["motivo_familiar"] = np.where(
        (df_2023['q14_motivos_reunificacion'] == 1) |
        (df_2023['q14_motivos_acompañar_otrx'] == 1) |
        (detalle.str.contains(
            'amor|pareja|novio|novia|espos|marid|casa|matrimonio|familia|padre|madre|hijo|me trajeron|menor|conyuge',
            regex=True
        )),
        1,0)
    df_2023["motivos_habitat"] = df_2023['q14_motivos_habitat']

    df_2023['motivo_necesidades_basicas'] = np.where(
        (df_2023['motivo_necesidades_basicas'] == 1) |
        detalle.str.contains(
            'calidad de vida|escasez|servicios|inflación|econom|salud|cáncer|comida|futuro mejor',
            regex=True
        ),
        1, 0
    )
    df_2023["motivo_otro"] = np.where(
        (df_2023["motivo_estudios_nuevas_experiencias"] == 0) &
        (df_2023["motivo_mejor_trabajo"] == 0) &
        (df_2023["motivo_violencias_persecuciones"] == 0) &
        (df_2023["motivo_necesidades_basicas"] == 0) &
        (df_2023["motivo_familiar"] == 0) &
        (df_2023["motivos_habitat"] == 0),
        1,
        0
    )
    df_2023.drop(columns=['q14_motivos_otros', 'q14_motivos_otros_detalle','q14_motivos','q14_motivos_estudio', 'q14_motivos_nuevas_experiencias', 'q14_motivos_mejor_trabajo', 'q14_motivos_violencia_genero', 'q14_motivos_orientacion_sexual', 'q14_motivos_persecucion', 'q14_motivos_salud', 'q14_motivos_necesidades_basicas', 'q14_motivos_reunificacion', 'q14_motivos_acompañar_otrx', 'q14_motivos_habitat'], inplace=True)

    #HIJOS
    df_2020["hijos"] = df_2020['q19_hijes']
    df_2020.drop(columns=['q19_hijes'], inplace=True)

    df_2023["hijos"] = df_2023.apply(mapear_hijos_2023, axis=1)
    df_2023.drop(columns=['q30_hijos_exterior', 'q30_hijos_arg', 'q29_hijos_num'], inplace=True)
    # print(df_2023['hijos'].value_counts())

    df_2023.drop(columns=['q31_hijos_menores_exterior'], inplace=True)

    #EDUCACION HIJOS
    def resolver_asistencia_2020(row):
        asiste = pd.notna(row['q20_educ_inicial']) or pd.notna(row['q20_educ_primario']) or pd.notna(row['q20_educ_secundario'])
        if asiste:
            return 'Sí'

        no_asiste = pd.notna(row['q20_educ_hijes_chicos']) or pd.notna(row['q20_educ_sin_escolaridad'])
        if no_asiste:
            return 'No'

        return np.nan

    df_2020['asistencia_educacion'] = df_2020.apply(resolver_asistencia_2020, axis=1)
    df_2020.drop(columns=['q20_educ_inicial', 'q20_educ_primario', 'q20_educ_secundario', 'q20_educ_terciario', 'q20_educ_hijes_chicos', 'q20_educ_sin_escolaridad', 'q20_educ_sinhijes'], inplace=True)

    df_2023['asistencia_educacion'] = df_2023['q32_asistencia_educacion'].replace({
        'Si, al menos alguno/a': 'Sí',
        'No, ninguno': 'No'
    })
    df_2023.drop(columns=['q32_asistencia_educacion'], inplace=True)

    #INCONVENIENTES INSCRIPCION ESCOLAR
    # Nota metodológica (*): en 2023 la pregunta desagrega la documentación en 3 categorías
    # (falta de DNI argentino / documentación escolar del país de origen / falta de documentación
    # escolar argentina) que en 2020 se relevaban como una única categoría. Para poder comparar
    # ambos años se agrupan las 3 categorías de 2023 en la única categoría de "documentación" de 2020.
    df_2020['inconveniente_educacion'] = df_2020['q22_pbm_inscripcion'].replace({
        'NO': 'No',
        'Si, otros problemas': 'Sí, otros problemas',
        'Si, problemas con la inscripción (no pude o no supe hacerla)': 'Sí, problemas con la inscripción (no pude o no supe hacerla)',
        'Sí, problemas con la documentación de mi hijo/a (falta de DNI, documentación del país de origen, falta de sellos)':
            'Sí, problemas con la documentación del hijo/a (falta de DNI, documentación del país de origen, falta de sellos) *'
    })
    df_2020.drop(columns=['q22_pbm_inscripcion', 'q22_otros'], inplace=True)

    def resolver_inconveniente_educacion_2023(row):
        if row['q33_incoveniente_educacion_no'] == 1.0:
            return 'No'
        if row['q33_incoveniente_educacion_cupo'] == 1.0:
            return 'Sí, problemas de cupo en la escuela'
        if row['q33_inconveniente_educacion_inscripcion'] == 1.0:
            return 'Sí, problemas con la inscripción (no pude o no supe hacerla)'
        if (row['q33_inconveniente_educacion_dni'] == 1.0
                or row['q33_inconveniente_educacion_documentacion_origen'] == 1.0
                or row['q33_inconveniente_educacion_documentacion_argentina'] == 1.0):
            return 'Sí, problemas con la documentación del hijo/a (falta de DNI, documentación del país de origen, falta de sellos) *'
        if row['q33_inconveniente_educacion_otro'] == 1.0:
            return 'Sí, otros problemas'
        return np.nan

    df_2023['inconveniente_educacion'] = df_2023.apply(resolver_inconveniente_educacion_2023, axis=1)
    df_2023.drop(columns=[
        'q33_incoveniente_educacion', 'q33_incoveniente_educacion_no', 'q33_incoveniente_educacion_cupo',
        'q33_inconveniente_educacion_inscripcion', 'q33_inconveniente_educacion_dni',
        'q33_inconveniente_educacion_documentacion_origen', 'q33_inconveniente_educacion_documentacion_argentina',
        'q33_inconveniente_educacion_otro', 'q33_especificar_educacion'
    ], inplace=True)

    #VALIDAR: pregunta nueva en 2023 (condicional), sin equivalente en 2020. Se elimina por ahora.
    df_2023.drop(columns=['q34_asistencia_educacion_razon', 'q34_especificar_razon'], inplace=True)

    #VALIDAR: pregunta nueva en 2023, sin equivalente en 2020. Se elimina por ahora.
    df_2023.drop(columns=['q35_educacion_discriminacion'], inplace=True)

    #SALUD
    df_2020['salud_cobertura'] = df_2020['q25_obra_social'].replace({
        'PAMI': 'Obra social (incluye PAMI)',
        'Obra social': 'Obra social (incluye PAMI)',
        'Prepaga (privada)': 'Prepaga o seguro privado'
    })
    df_2020.drop(columns=['q25_obra_social'], inplace=True)

    df_2023['salud_cobertura'] = df_2023['q36_salud']
    df_2023.drop(columns=['q36_salud'], inplace=True)

    #VALIDAR: la pregunta no es estrictamente equivalente entre años. En 2020 se relevan
    # enfermedades/condiciones crónicas (¿tenés alguna enfermedad?), mientras que en 2023 se
    # releva si acudió al sistema de salud por salud física, mental o sexual/reproductiva en
    # los últimos 2 años. Se arma como aproximación Sí/No/Prefiero no responder; pendiente de
    # validación por el equipo de coordinación de ENMA.
    def resolver_problemas_salud_2020(row):
        if pd.notna(row['q29_enfermedad_ninguna']):
            return 'No'

        columnas_enfermedad = [
            'q29_enfermedad_cardio', 'q29_enfermedad_cancer', 'q29_enfermedad_respiratoria',
            'q29_enfermedad_diabetes', 'q30_enfermedad_renal', 'q30_enfermedad_otra'
        ]
        if row[columnas_enfermedad].notna().any():
            return 'Sí'

        return 'Prefiero no responder'

    df_2020['salud_problemas'] = df_2020.apply(resolver_problemas_salud_2020, axis=1)
    df_2020.drop(columns=[
        'q29_enfermedad_ninguna', 'q29_enfermedad_cardio', 'q29_enfermedad_cancer',
        'q29_enfermedad_respiratoria', 'q29_enfermedad_diabetes', 'q30_enfermedad_renal', 'q30_enfermedad_otra'
    ], inplace=True)

    def resolver_problemas_salud_2023(row):
        if row['q37_salud_problemas_no'] == 1.0:
            return 'No'
        if (row['q37_salud_problemas_fisica'] == 1.0
                or row['q37_salud_problemas_mental'] == 1.0
                or row['q37_salud_problemas_esi'] == 1.0):
            return 'Sí'
        return 'Prefiero no responder'

    df_2023['salud_problemas'] = df_2023.apply(resolver_problemas_salud_2023, axis=1)
    df_2023.drop(columns=[
        'q37_salud_problemas', 'q37_salud_problemas_fisica', 'q37_salud_problemas_mental',
        'q37_salud_problemas_esi', 'q37_salud_problemas_no'
    ], inplace=True)

    #ACCESO A LA SALUD (agrupado según tablero)
    # Nota: en 2020 no existían las opciones "no pudo atenderse" ni "nunca necesité atenderme".
    # Como la pregunta es de selección múltiple, se resuelve a una sola categoría por persona
    # con esta prioridad: nunca necesitó > no pudo atenderse > salud pública > obra social/privada > tradicional/familiar/comunitaria.
    def resolver_acceso_salud_2020(row):
        publica = pd.notna(row['q26_salud_guardias']) or pd.notna(row['q26_salud_centros']) or pd.notna(row['q26_salud_consultorios'])
        obrasocial = pd.notna(row['q26_salud_obrasocial'])
        tradicional = pd.notna(row['q26_salud_comunitarios']) or pd.notna(row['q26_salud_tradicional']) or pd.notna(row['q26_salud_familia'])

        if publica:
            return 'Salud pública'
        if obrasocial:
            return 'Obra social, prepaga o privada'
        if tradicional:
            return 'Medicina tradicional, familiar o comunitaria'
        return np.nan

    df_2020['metodo_acceso_salud'] = df_2020.apply(resolver_acceso_salud_2020, axis=1)
    df_2020.drop(columns=[
        'q26_salud_guardias', 'q26_salud_centros', 'q26_salud_consultorios', 'q26_salud_obrasocial',
        'q26_salud_comunitarios', 'q26_salud_tradicional', 'q26_salud_familia', 'q26_salud_otros'
    ], inplace=True)

    def resolver_acceso_salud_2023(row):
        if row['q38_salud_resolver_problema_no'] == 1.0:
            return 'Nunca necesité atenderme'
        if row['q38_salud_resolver_problema_imposibilidad'] == 1.0:
            return 'No pudo atenderse'
        if row['q38_salud_resolver_problema_hospitalpub'] == 1.0 or row['q38_salud_resolver_problema_cen_ate_prim'] == 1.0:
            return 'Salud pública'
        if row['q38_salud_resolver_problema_prepaga'] == 1.0 or row['q38_salud_resolver_problema_pago_consulta'] == 1.0:
            return 'Obra social, prepaga o privada'
        if row['q38_salud_resolver_problema_tracional'] == 1.0 or row['q38_salud_resolver_problema_recomendaciones'] == 1.0:
            return 'Medicina tradicional, familiar o comunitaria'
        return np.nan

    df_2023['metodo_acceso_salud'] = df_2023.apply(resolver_acceso_salud_2023, axis=1)
    df_2023.drop(columns=[
        'q38_salud_resolver_problema', 'q38_salud_resolver_problema_no', 'q38_salud_resolver_problema_hospitalpub',
        'q38_salud_resolver_problema_cen_ate_prim', 'q38_salud_resolver_problema_prepaga',
        'q38_salud_resolver_problema_pago_consulta', 'q38_salud_resolver_problema_tracional',
        'q38_salud_resolver_problema_recomendaciones', 'q38_salud_resolver_problema_imposibilidad',
        'q38_salud_resolver_problema_otro'
    ], inplace=True)

    df_2020['salud_dificultad_acceso'] = df_2020['q27_dificultades']
    df_2020.drop(columns=['q27_dificultades'], inplace=True)

    df_2023['salud_dificultad_acceso'] = df_2023['q39_salud_acceso']
    df_2023.drop(columns=['q39_salud_acceso'], inplace=True)

    #TIPO DE DIFICULTAD DE ACCESO A LA SALUD (agrupado según categorías amplias)
    # Nota: "Barreras administrativas" combina, en 2020, dificultades de transporte/horarios/
    # distancia/información para llegar al establecimiento, y en 2023 solo falta de información o
    # desconocimiento de los trámites; no son estrictamente equivalentes (2020 incluye barreras de
    # traslado que 2023 no releva). "Barreras de comunicación" (idioma) es una categoría nueva de
    # 2023, sin equivalente en 2020. "Sin dificultades" solo existe en 2020, ya que en 2023 esta
    # pregunta es condicional (solo se hace a quien ya declaró haber tenido dificultades en Q39).
    # Como es de selección múltiple, se resuelve a una sola categoría por persona con esta
    # prioridad: sin dificultades > maltrato o discriminación > barreras económicas > barreras
    # administrativas > barreras de comunicación > barreras de acceso al servicio > otras.
    def resolver_tipo_dificultad_2020(row):
        if pd.notna(row['q28_dificultades_no']):
            return 'Sin dificultades'
        if pd.notna(row['q28_dificultades_discrim']):
            return 'Maltrato o discriminación'
        if pd.notna(row['q28_dificultades_pago']):
            return 'Barreras económicas'
        if pd.notna(row['q28_dificultades_dni']) or pd.notna(row['q28_dificultades_domicilio']) or pd.notna(row['q28_dificultades_acceso']):
            return 'Barreras administrativas'
        if pd.notna(row['q28_dificultades_turnos']):
            return 'Barreras de acceso al servicio'
        if pd.notna(row['q28_dificultades_otras']):
            return 'Otras'
        return np.nan

    df_2020['tipo_dificultad_salud'] = df_2020.apply(resolver_tipo_dificultad_2020, axis=1)
    #VALIDAR: los casos sin dato se asumen como "Sin dificultades"; a confirmar con coordinación.
    df_2020['tipo_dificultad_salud'] = df_2020['tipo_dificultad_salud'].fillna('Sin dificultades')
    df_2020.drop(columns=[
        'q28_dificultades_no', 'q28_dificultades_dni', 'q28_dificultades_domicilio', 'q28_dificultades_discrim',
        'q28_dificultades_pago', 'q28_dificultades_acceso', 'q28_dificultades_turnos', 'q28_dificultades_otras'
    ], inplace=True)

    def resolver_tipo_dificultad_2023(row):
        if row['q40_salud_acceso_dificultades_maltrato'] == 1.0:
            return 'Maltrato o discriminación'
        if row['q40_salud_acceso_dificultades_pago'] == 1.0:
            return 'Barreras económicas'
        if (row['q40_salud_acceso_dificultades_dni'] == 1.0
                or row['q40_salud_acceso_dificultades_domicilio'] == 1.0
                or row['q40_salud_acceso_dificultades_desconocimiento'] == 1.0):
            return 'Barreras administrativas'
        if row['q40_salud_acceso_dificultades_idioma'] == 1.0:
            return 'Barreras de comunicación'
        if row['q40_salud_acceso_dificultades_turnos'] == 1.0:
            return 'Barreras de acceso al servicio'
        if row['q40_salud_acceso_dificultades_otra'] == 1.0:
            return 'Otras'
        return np.nan

    df_2023['tipo_dificultad_salud'] = df_2023.apply(resolver_tipo_dificultad_2023, axis=1)
    #VALIDAR: los casos sin dato se asumen como "Sin dificultades"; a confirmar con coordinación.
    df_2023['tipo_dificultad_salud'] = df_2023['tipo_dificultad_salud'].fillna('Sin dificultades')
    df_2023.drop(columns=[
        'q40_salud_acceso_dificultades', 'q40_salud_acceso_dificultades_dni', 'q40_salud_acceso_dificultades_domicilio',
        'q40_salud_acceso_dificultades_maltrato', 'q40_salud_acceso_dificultades_pago',
        'q40_salud_acceso_dificultades_desconocimiento', 'q40_salud_acceso_dificultades_turnos',
        'q40_salud_acceso_dificultades_idioma', 'q40_salud_acceso_dificultades_otra'
    ], inplace=True)

    # SITUACION DOCUMENTAL 
    df_2020['dni_tenencia'] = (df_2020['q13_sit_docu'].str.contains('Tengo DNI', na=False).map({True: 'Si', False: 'No'}))
    df_2020.drop(columns=['q13_sit_docu'], inplace=True)

    df_2023["dni_tenencia"] = df_2023['q17_dni_tenencia']
    df_2023.drop(columns=['q17_dni_tenencia', 'q18_dni_situacion', 'q19_situacion_documentaria'], inplace=True)

    #SOLICITUD DE ASILO / REFUGIO / VISA HUMANITARIA
    def mapear_asilo_2020(valor):
        if pd.isna(valor):
            return 'Prefiero no responder'
        if valor == 'No':
            return 'No'
        if valor == 'No quiero responder':
            return 'Prefiero no responder'
        if valor == 'No sé en qué consisten el refugio ni los visados humanitarios':
            return 'Prefiero no responder'
        if valor.startswith('Sí,'):
            return 'Sí'
        return 'Prefiero no responder'

    df_2020['solicitud_asilo_refugio'] = df_2020['q15_sol_asilo'].apply(mapear_asilo_2020)
    df_2020.drop(columns=['q15_sol_asilo'], inplace=True)

    df_2023['solicitud_asilo_refugio'] = df_2023['q22_solicitud_asilo'].replace({
        'Si': 'Sí',
        np.nan: 'Prefiero no responder'
    })
    df_2023.drop(columns=['q22_solicitud_asilo', 'q23_solicitud_asilo_si', 'q24_solicitud_asilo_no'], inplace=True)

    #DIFICULTAD DNI
    dificultad_cols = {
        'q21_dni_dificultad_turnos':               'Sí, no pude sacar turno o me lo postergaron',
        'q21_dni_dificultad_demora':               'Sí, no pude sacar turno o me lo postergaron',
        'q21_dni_dificultad_costo':                'Sí, por dificultades económicas',
        'q21_dni_dificultad_documentacion_origen': 'Sí, me falta documentación de mi país de origen para completar el trámite',
        'q21_dni_dificultad_falta_info':           'Sí, no sé cómo iniciar el trámite (no entiendo el idioma, etc.)',
        'q21_dni_dificultad_internet':             'Sí, no tengo internet o herramientas para hacerlo (teléfono, computadora, etc.)',
        'q21_dni_dificultad_identidad_genero':     'Otro (especifique)',
        'q21_dni_dificultad_otros':                'Otro (especifique)',
    } 

    def resolver_dificultad_2023(row):
        if row['q20_dni_dificultad_binaria'] == 'No':
            return 'No, no he tenido dificultades'

        if row['q20_dni_dificultad_binaria'] == 'Prefiero no responder':
            return 'Prefiero no responder'

        for col, categoria in dificultad_cols.items():
            if row.get(col) == 1.0:
                return categoria

        return 'Prefiero no responder'

    df_2023['dni_dificultad'] = df_2023.apply(resolver_dificultad_2023, axis=1)

    df_2020['dni_dificultad'] = df_2020['q14_problemas_docu'].replace({
        np.nan: 'Prefiero no responder'
    })
    df_2020['dni_dificultad'] = df_2020['dni_dificultad'].replace({
        'Sí, no cumplo con los requisitos para regularizarme': 'Otro (especifique)',
        'Sí, no sé usar el sistema online para el trámite (RADEX)': 'Sí, no tengo internet o herramientas para hacerlo (teléfono, computadora, etc.)'
    })

    df_2020.drop(columns=['q14_problemas_docu'], inplace=True)
    df_2023.drop(columns=list(dificultad_cols.keys()) + ['q20_dni_dificultad_binaria'], inplace=True)

    #FAMILIA Y HOGAR
    df_2020['hogar_personas'] = df_2020['q34_cant_perso']
    df_2020.drop(columns=['q34_cant_perso'], inplace=True)

    df_2023['hogar_personas'] = df_2023['q26_hogar_personas']
    df_2023.drop(columns=['q26_hogar_personas'], inplace=True)

    df_2020.loc[df_2020['hogar_personas'] < 0, 'hogar_personas'] = 0
    df_2023.loc[df_2023['hogar_personas'] < 0, 'hogar_personas'] = 0

    df_2020['hogar_discapacidad'] = df_2020['q18_disca'].replace({
        'No quiero responder': 'Prefiero no responder',
        np.nan: 'Prefiero no responder'
    })
    df_2020.drop(columns=['q18_disca'], inplace=True)

    df_2023['hogar_discapacidad'] = df_2023['q27_hogar_discapacidad'].replace({
        np.nan: 'Prefiero no responder'
    })
    df_2023.drop(columns=['q27_hogar_discapacidad'], inplace=True)

    df_2020['hogar_convivencia'] = df_2020['q17_casado'].replace({
        'Si, con una persona nacida en otro país (migrante o extranjero/a)': 'Sí, con una persona nacida en otro país (migrante o extranjero/a)',
        'Si, con una persona nacida en Argentina': 'Sí, con una persona nacida en Argentina',
        'No quiero contestar': 'Prefiero no responder',
        np.nan: 'Prefiero no responder'
    })
    df_2020.drop(columns=['q17_casado'], inplace=True)

    df_2023['hogar_convivencia'] = df_2023['q28_hogar_convivencia'].replace({
        np.nan: 'Prefiero no responder'
    })
    df_2023.drop(columns=['q28_hogar_convivencia'], inplace=True)

    #PREGUNTAS SOLO UN AÑO
    df_2023.drop(columns=['q12_modo_ingreso'], inplace=True)

    #VIVIENDA
    # Tablero: no incluir estas preguntas.
    df_2020.drop(columns=['q31_vivienda_tipo'], inplace=True)
    df_2023.drop(columns=['q41_vivienda_lugar', 'q42_vivienda_tipo', 'q42_vivienda_especificar'], inplace=True)

    df_2020['vivienda_tenencia'] = df_2020['q32_vivienda_condicion'].replace({
        'Alquiler con contrato': 'Alquiler con contrato formal',
        'Alquiler informal': 'Alquiler informal / anticrético',
        'Propio (de usted o un familiar)': 'Propia (de usted o un miembro de su hogar)'
    })
    df_2020.drop(columns=['q32_vivienda_condicion'], inplace=True)

    #VALIDAR: en 2023 la categoría "Otro" viene acompañada de un campo de texto libre
    # (q43_vivienda_es_especificar) que no se recodifica; se descarta y se mantiene "Otro" tal cual.
    df_2023['vivienda_tenencia'] = df_2023['q43_vivienda_es']
    df_2023.drop(columns=['q43_vivienda_es', 'q43_vivienda_es_especificar'], inplace=True)

    #DIFICULTADES DE ACCESO A LA VIVIENDA (agrupado según categorías amplias)
    #VALIDAR: como es de selección múltiple, se resuelve a una sola categoría por persona con esta
    # prioridad (a confirmar con coordinación): sin dificultades > conflictos habitacionales >
    # barreras para alquilar > barreras económicas > acceso a programas de vivienda > otras.
    # "Conflictos habitacionales" (desalojo, estafa) es una categoría nueva de 2023, sin
    # equivalente en 2020.
    def resolver_dificultad_vivienda_2020(row):
        if pd.notna(row['q33_accesovivienda_sinprob']):
            return 'Sin dificultades'
        if pd.notna(row['q33_accesovivienda_extranjero']) or pd.notna(row['q33_accesovivienda_garantia']):
            return 'Barreras para alquilar'
        if pd.notna(row['q33_accesovivienda_costo']) or pd.notna(row['q33_accesovivienda_compra']):
            return 'Barreras económicas'
        if pd.notna(row['q33_accesovivienda_programas']):
            return 'Acceso a programas de vivienda'
        if pd.notna(row['q33_accesovivienda_otros']):
            return 'Otras'
        return np.nan

    df_2020['dificultad_vivienda'] = df_2020.apply(resolver_dificultad_vivienda_2020, axis=1)
    df_2020['dificultad_vivienda'] = df_2020['dificultad_vivienda'].fillna('Sin dificultades')
    df_2020.drop(columns=[
        'q33_accesovivienda_sinprob', 'q33_accesovivienda_costo', 'q33_accesovivienda_extranjero',
        'q33_accesovivienda_garantia', 'q33_accesovivienda_compra', 'q33_accesovivienda_programas',
        'q33_accesovivienda_otros'
    ], inplace=True)

    def resolver_dificultad_vivienda_2023(row):
        if row['q44_vivienda_problemas_no'] == 1.0:
            return 'Sin dificultades'
        if row['q44_vivienda_problemas_desalojo'] == 1.0 or row['q44_vivienda_problemas_estafa'] == 1.0:
            return 'Conflictos habitacionales'
        if row['q44_vivienda_problemas_discriminacion'] == 1.0 or row['q44_vivienda_problemas_garantia'] == 1.0:
            return 'Barreras para alquilar'
        if row['q44_vivienda_problemas_precio'] == 1.0 or row['q44_vivienda_problemas_compra'] == 1.0:
            return 'Barreras económicas'
        if row['q44_vivienda_problemas_ayudasocial'] == 1.0:
            return 'Acceso a programas de vivienda'
        if row['q44_vivienda_problemas_otra'] == 1.0:
            return 'Otras'
        return np.nan

    df_2023['dificultad_vivienda'] = df_2023.apply(resolver_dificultad_vivienda_2023, axis=1)
    df_2023['dificultad_vivienda'] = df_2023['dificultad_vivienda'].fillna('Sin dificultades')
    df_2023.drop(columns=[
        'q44_vivienda_problemas', 'q44_vivienda_problemas_no', 'q44_vivienda_problemas_precio',
        'q44_vivienda_problemas_discriminacion', 'q44_vivienda_problemas_garantia', 'q44_vivienda_problemas_compra',
        'q44_vivienda_problemas_ayudasocial', 'q44_vivienda_problemas_desalojo', 'q44_vivienda_problemas_estafa',
        'q44_vivienda_problemas_otra', 'q44_vivienda_problemas_otra_especificar'
    ], inplace=True)

    # Tablero: no incluir estas preguntas.
    df_2020.drop(columns=[
        'q35_servicios_luz', 'q35_servicios_agua', 'q35_servicios_gas', 'q35_servicios_telefono',
        'q35_servicios_internet', 'q35_servicios_cloaca', 'q35_servicios_alumbrado',
        'q35_servicios_pavimento', 'q35_servicios_basura', 'q35_servicios_todos'
    ], inplace=True)
    df_2023.drop(columns=[
        'q45_vivienda_servicios', 'q45_vivienda_servicios_luz', 'q45_vivienda_servicios_agua',
        'q45_vivienda_servicios_gas', 'q45_vivienda_servicios_telefono', 'q45_vivienda_servicios_internet',
        'q45_vivienda_servicios_cloaca', 'q45_vivienda_servicios_alumbrado',
        'q45_vivienda_servicios_pavimentacion', 'q45_vivienda_servicios_rec_basura', 'q45_vivienda_servicios_todos'
    ], inplace=True)

    #NIVEL EDUCATIVO (agrupación del anuario)
    #VALIDAR: agrupación tomada del anuario; a confirmar con coordinación. Los sin dato en 2020
    # se completan como "Prefiero no responder".
    mapa_nivel_educativo = {
        'Primario incompleto': 'Hasta secundario incompleto',
        'Primario incompleto o en curso': 'Hasta secundario incompleto',
        'Primario completo': 'Hasta secundario incompleto',
        'Secundario incompleto': 'Hasta secundario incompleto',
        'Secundario incompleto o en curso': 'Hasta secundario incompleto',
        'Secundario completo': 'Secundario completo',
        'Terciario incompleto': 'Secundario completo',
        'Terciario incompleto o en curso': 'Secundario completo',
        'Universitario incompleto': 'Secundario completo',
        'Universitario incompleto o en curso': 'Secundario completo',
        'Terciario completo': 'Superior o universitario completo y más',
        'Universitario completo': 'Superior o universitario completo y más',
        'Prefiero no contestar': 'Prefiero no responder',
        'Prefiero no responder': 'Prefiero no responder'
    }

    df_2020['nivel_educativo_agrup'] = df_2020['q37_nivel_educativo'].replace(mapa_nivel_educativo)
    df_2020['nivel_educativo_agrup'] = df_2020['nivel_educativo_agrup'].fillna('Prefiero no responder')
    df_2020.drop(columns=['q37_nivel_educativo'], inplace=True)

    df_2023['nivel_educativo_agrup'] = df_2023['q46_estudios'].replace(mapa_nivel_educativo)
    df_2023['nivel_educativo_agrup'] = df_2023['nivel_educativo_agrup'].fillna('Prefiero no responder')
    df_2023.drop(columns=['q46_estudios'], inplace=True)

    df_2020['estudiando_actualmente'] = df_2020['q38_estudia']
    df_2020.drop(columns=['q38_estudia'], inplace=True)

    df_2023['estudiando_actualmente'] = df_2023['q47_estudiando_argentina'].replace({'Si': 'Sí'})
    df_2023.drop(columns=['q47_estudiando_argentina'], inplace=True)

    #TIPO DE ESTUDIO EN CURSO (una sola columna, priorización)
    # Nota: en 2020 la pregunta se releva como selección única (una sola categoría por persona)
    # aunque el cuestionario original la presentaba como selección múltiple; en 2023 sí admite
    # selección múltiple real, por lo que se resuelve a una sola categoría con esta prioridad:
    # Primario > Secundario > Terciario > Universitario (grado) > Postgrado > Capacitaciones.
    # "Postgrado" es una categoría nueva de 2023, sin equivalente en 2020. "Capacitaciones" agrupa,
    # en 2020, cursos de idioma + capacitaciones laborales/profesionales + talleres o cursos generales.
    mapa_tipo_estudio_2020 = {
        'Primario (incluye FinEs, primaria en el marco de bachilleratos populares, CEBA)': 'Primario',
        'Secundario (incluye FinEs, bachillerato popular, CENS)': 'Secundario',
        'Terciario': 'Terciario',
        'Universitario': 'Universitario (grado)',
        'Cursos de idioma': 'Capacitaciones laborales, profesionales, en oficios, cursos de idioma',
        'Capacitaciones laborales  o profesionales': 'Capacitaciones laborales, profesionales, en oficios, cursos de idioma',
        'Talleres o cursos generales (cultura, oficios, etc.)': 'Capacitaciones laborales, profesionales, en oficios, cursos de idioma'
    }
    df_2020['tipo_estudio'] = df_2020['q39_tipo_estudio'].map(mapa_tipo_estudio_2020)
    df_2020['tipo_estudio'] = df_2020['tipo_estudio'].fillna('No está realizando estudios')
    df_2020.drop(columns=['q39_tipo_estudio'], inplace=True)

    def resolver_tipo_estudio_2023(row):
        if row['q48_estudiando_nivel_prim'] == 1.0:
            return 'Primario'
        if row['q48_estudiando_nivel_sec'] == 1.0:
            return 'Secundario'
        if row['q48_estudiando_nivel_ter'] == 1.0:
            return 'Terciario'
        if row['q48_estudiando_nivel_uni'] == 1.0:
            return 'Universitario (grado)'
        if row['q48_estudiando_nivel_postgrado'] == 1.0:
            return 'Postgrado'
        if row['q48_estudiando_nivel_capacitaciones'] == 1.0:
            return 'Capacitaciones laborales, profesionales, en oficios, cursos de idioma'
        return np.nan

    df_2023['tipo_estudio'] = df_2023.apply(resolver_tipo_estudio_2023, axis=1)
    df_2023['tipo_estudio'] = df_2023['tipo_estudio'].fillna('No está realizando estudios')
    df_2023.drop(columns=[
        'q48_estudiando_nivel', 'q48_estudiando_nivel_prim', 'q48_estudiando_nivel_sec',
        'q48_estudiando_nivel_ter', 'q48_estudiando_nivel_uni', 'q48_estudiando_nivel_postgrado',
        'q48_estudiando_nivel_capacitaciones'
    ], inplace=True)

    #INCONVENIENTES DE INSCRIPCION AL ESTUDIO (una sola columna, priorización)
    #VALIDAR: "problemas con documentación del país de origen"/"equivalencias" (2020) y
    # "documentación escolar argentina"/"costos"/"títulos y competencias del país de origen" (2023)
    # no tienen categoría propia en el tablero, se agrupan en "otros". Prioridad: Sin problemas >
    # Problemas con el DNI > Discriminación o xenofobia > Problemas con la inscripción > otros.
    def resolver_inconveniente_inscripcion_2020(row):
        if pd.notna(row['q40_inscripcion_no']):
            return 'Sin problemas'
        if pd.notna(row['q40_inscripcion_dni']):
            return 'Problemas con el DNI'
        if pd.notna(row['q40_inscripcion_requisitos']):
            return 'Discriminación o xenofobia'
        if pd.notna(row['q40_inscripcion_online']):
            return 'Problemas con la inscripción'
        if (pd.notna(row['q40_inscripcion_documentacion']) or pd.notna(row['q40_inscripcion_equivalencias'])
                or pd.notna(row['q40_inscripcion_otros'])):
            return 'otros'
        return np.nan

    df_2020['inconveniente_inscripcion_estudio'] = df_2020.apply(resolver_inconveniente_inscripcion_2020, axis=1)
    df_2020['inconveniente_inscripcion_estudio'] = df_2020['inconveniente_inscripcion_estudio'].fillna('Sin problemas')
    df_2020.drop(columns=[
        'q40_inscripcion_no', 'q40_inscripcion_dni', 'q40_inscripcion_requisitos',
        'q40_inscripcion_documentacion', 'q40_inscripcion_equivalencias', 'q40_inscripcion_online',
        'q40_inscripcion_otros'
    ], inplace=True)

    def resolver_inconveniente_inscripcion_2023(row):
        if row['q49_estudiando_inconvenientes'] == 'No tuve ningún problema':
            return 'Sin problemas'
        if row['q50_problemas_dni'] == 1.0:
            return 'Problemas con el DNI'
        if row['q50_problemas_discriminacion'] == 1.0:
            return 'Discriminación o xenofobia'
        if row['q50_problemas_inscripcion_online'] == 1.0:
            return 'Problemas con la inscripción'
        if (row['q50_problemas_doc_escolar'] == 1.0 or row['q50_problemas_costos'] == 1.0
                or row['q50_problemas_titulos_origen'] == 1.0 or row['q50_problemas_otros'] == 1.0):
            return 'otros'
        return np.nan

    df_2023['inconveniente_inscripcion_estudio'] = df_2023.apply(resolver_inconveniente_inscripcion_2023, axis=1)
    df_2023['inconveniente_inscripcion_estudio'] = df_2023['inconveniente_inscripcion_estudio'].fillna('Sin problemas')
    df_2023.drop(columns=[
        'q49_estudiando_inconvenientes', 'q50_estudiando_problemas', 'q50_problemas_titulos_origen',
        'q50_problemas_dni', 'q50_problemas_doc_escolar', 'q50_problemas_inscripcion_online',
        'q50_problemas_costos', 'q50_problemas_discriminacion', 'q50_problemas_otros'
    ], inplace=True)

    #SITUACION OCUPACIONAL (agrupado según tablero)
    #VALIDAR: en 2020 la pregunta se relevó en referencia a la situación previa a la pandemia
    # ("Antes de la pandemia..."), mientras que en 2023 es la situación actual; se homologan como
    # la variable de situación ocupacional de cada año, a confirmar con coordinación. La categoría
    # "Otra" de 2023, los sin dato y "Prefiero no responder" quedan agrupados en "Otra".
    mapa_situacion_ocupacional_2020 = {
        'Trabajo en relación de dependencia o con un salario fijo': 'Trabaja',
        'Trabajo independiente\xa0 (monotributo social, trabajador de la economía popular)': 'Trabaja',
        'Changas o trabajos esporádicos': 'Trabaja',
        'Trabajo de temporada o estacional': 'Trabaja',
        'Sin trabajar por licencia (problemas de salud u otras licencias)': 'Trabaja',
        'Trabajo en cooperativa u organizaciones': 'Trabaja',
        'Trabajos no remunerados (ama de casa, cuidado de familiares, etc.)': 'Trabaja',
        'Retirado/a o jubilado/a': 'Jubilado-retirado',
        'Estudio (no trabajo)': 'Solo estudia',
        'Desempleado/a (buscando trabajo)': 'Desempleado'
    }
    df_2020['situacion_ocupacional_agrup'] = df_2020['q42_trabajo_preCOVID'].replace(mapa_situacion_ocupacional_2020)
    df_2020['situacion_ocupacional_agrup'] = df_2020['situacion_ocupacional_agrup'].fillna('Otra')
    df_2020.drop(columns=['q42_trabajo_preCOVID'], inplace=True)

    mapa_situacion_ocupacional_2023 = {
        'Con trabajo y una remuneración fija': 'Trabaja',
        'Con trabajo por cuenta propia': 'Trabaja',
        'Venta ambulante': 'Trabaja',
        'Realizando changas, trabajos esporádicos o subempleado': 'Trabaja',
        'Realizando trabajos sin remuneración': 'Trabaja',
        'Sin trabajar con licencia': 'Trabaja',
        'Jubilado/a, retirado/a': 'Jubilado-retirado',
        'Estudiando': 'Solo estudia',
        'Desempleado/ buscando trabajo': 'Desempleado',
        'Otra': 'Otra',
        'Prefiero no responder': 'Otra'
    }
    df_2023['situacion_ocupacional_agrup'] = df_2023['q51_situacion_ocupacional'].replace(mapa_situacion_ocupacional_2023)
    df_2023['situacion_ocupacional_agrup'] = df_2023['situacion_ocupacional_agrup'].fillna('Otra')
    df_2023.drop(columns=['q51_situacion_ocupacional', 'q51_situacion_ocupacional_esp'], inplace=True)

    #CIRCUITOS LABORALES
    #VALIDAR: en 2023 "circuitos_laborales" ya viene calculada en la base (probablemente construida
    # a partir del texto libre de q54_ocupacion), por lo que se conserva tal cual y se descarta el
    # texto libre. En 2020 no existe esa variable, así que se construye a partir de las 14 categorías
    # cerradas de q44_ocupacion, mapeándolas a los mismos 5 circuitos de 2023. Este mapeo es una
    # interpretación propia (varias categorías podrían encuadrar en más de un circuito) y debe ser
    # validada por el equipo de coordinación. La categoría "Otra (especifique)" de 2020 —la más
    # numerosa, ~25% de los casos— no se pudo clasificar en ningún circuito y queda sin dato.
    mapa_circuitos_2020 = {
        'Agricultura/horticultura/ fruticultura / forestación': 'Circuito de producción y comercialización de alimentos',
        'Servicios gastronómicos (restaurantes, elaboración de comida, etc.)': 'Circuito de producción y comercialización de alimentos',
        'Trabajo en casas particulares (cuidado, limpieza, jardinería, etc.)': 'Circuito de economía de los cuidados',
        'Salud y la sanidad (medicina, enfermería, otros)': 'Circuito de economía de los cuidados',
        'Construcción': 'Circuito de trabajo asalariado clásico',
        'Comercialización directa (tiendas, supermercados, negocios varios)': 'Circuito de trabajo asalariado clásico',
        'Servicios de limpieza (no domésticos)': 'Circuito de trabajo asalariado clásico',
        'Educación (docencia, clases particulares, investigación, etc.)': 'Circuito de la economía de la información y conocimiento',
        'Traslados basados en plataformas de internet (Uber, Cabify, otros)': 'Circuito de la economía de la información y conocimiento',
        'Producción industrial y artesanal (artesanías, confección, manufactura)': 'Circuito de trabajo autónomo',
        'Transportes (taxi, remis, colectivo, camión, etc.)': 'Circuito de trabajo autónomo',
        'Reparación de bienes de consumo (gasista, mecánico, electricista, etc.)': 'Circuito de trabajo autónomo',
        'Venta ambulante/venta por catálogo / feriante': 'Circuito de trabajo autónomo',
        'Otra (especifique)': np.nan
    }
    df_2020['circuitos_laborales'] = df_2020['q44_ocupacion'].replace(mapa_circuitos_2020)
    df_2020.drop(columns=['q44_ocupacion', 'q44_ocupacion_otra'], inplace=True)

    df_2023.drop(columns=['q54_ocupacion'], inplace=True)

    #TRABAJO EN AREA DE EXPERIENCIA
    df_2020['trabajo_en_area_experiencia'] = df_2020['q46_trabajo_experiencia'].replace({
        'No quiero responder': 'Prefiero no responder'
    })
    df_2020.drop(columns=['q46_trabajo_experiencia'], inplace=True)

    df_2023['trabajo_en_area_experiencia'] = df_2023['q55_experiencia'].replace({'Si': 'Sí'})
    df_2023.drop(columns=['q55_experiencia'], inplace=True)

    #DIFICULTAD PARA CONSEGUIR TRABAJO EN AREA DE EXPERIENCIA
    # Nota: pregunta nueva de 2023, sin equivalente en 2020 (queda en NaN para ese año).
    df_2020['dificultad_trabajo_experiencia'] = np.nan

    df_2023['dificultad_trabajo_experiencia'] = df_2023['q56_ocupacion_dificultad'].replace({'Si': 'Sí'})
    df_2023.drop(columns=['q56_ocupacion_dificultad'], inplace=True)

    #TIPO DE DIFICULTAD PARA ACCEDER AL TRABAJO (una sola columna, priorización)
    #VALIDAR: la nota de la tabla de mapeo decía que Q57 estaba excluida de la base pública de
    # 2023, pero las columnas q57_dificultad_* sí están presentes en el archivo entregado, así que
    # se usan igual; confirmar con coordinación que corresponde incluirlas. Se resuelve a una sola
    # categoría por persona con esta prioridad: Convalidación de títulos > Discriminación por ser
    # extranjero/a > Discriminación por género u orientación sexual > Documentación faltante >
    # Idioma > Edad > No calificado/sin experiencia previa > Cuidado de personas del hogar >
    # Condición de salud o discapacidad > Falta de oferta/no consigo trabajo > No sé dónde buscar
    # trabajo > Prefiero no responder. "Discriminación por género u orientación sexual", "Cuidado
    # de personas del hogar", "Condición de salud o discapacidad" y "No sé dónde buscar trabajo"
    # son categorías nuevas de 2023, sin equivalente en 2020.
    def resolver_dificultad_trabajo_tipo_2020(row):
        if pd.notna(row['q47_problemas_convalidacion']):
            return 'Convalidación de títulos'
        if pd.notna(row['q47_problemas_discriminacion']):
            return 'Discriminación por ser extranjero/a'
        if pd.notna(row['q47_problemas_documentos']):
            return 'Documentación faltante'
        if pd.notna(row['q47_problemas_idioma']):
            return 'Idioma'
        if pd.notna(row['q47_problemas_edad']):
            return 'Edad'
        if pd.notna(row['q47_problemas_nocalificado']):
            return 'No calificado/sin experiencia previa'
        if pd.notna(row['q47_problemas_trabajo']):
            return 'Falta de oferta/no consigo trabajo'
        if pd.notna(row['q47_problemas_norespondo']):
            return 'Prefiero no responder'
        return np.nan

    df_2020['tipo_dificultad_trabajo'] = df_2020.apply(resolver_dificultad_trabajo_tipo_2020, axis=1)
    df_2020.drop(columns=[
        'q47_problemas_convalidacion', 'q47_problemas_trabajo', 'q47_problemas_discriminacion',
        'q47_problemas_documentos', 'q47_problemas_idioma', 'q47_problemas_nocalificado',
        'q47_problemas_edad', 'q47_problemas_norespondo'
    ], inplace=True)

    def resolver_dificultad_trabajo_tipo_2023(row):
        if row['q57_dificultad_titulos'] == 1.0:
            return 'Convalidación de títulos'
        if row['q57_dificultad_discriminacion'] == 1.0:
            return 'Discriminación por ser extranjero/a'
        if row['q57_dificultad_sexual'] == 1.0:
            return 'Discriminación por género u orientación sexual'
        if row['q57_dificultad_documentacion'] == 1.0:
            return 'Documentación faltante'
        if row['q57_dificultad_idioma'] == 1.0:
            return 'Idioma'
        if row['q57_dificultad_edad'] == 1.0:
            return 'Edad'
        if row['q57_dificultad_inexperiencia'] == 1.0:
            return 'No calificado/sin experiencia previa'
        if row['q57_dificultad_hogar'] == 1.0:
            return 'Cuidado de personas del hogar'
        if row['q57_dificultad_salud'] == 1.0:
            return 'Condición de salud o discapacidad'
        if row['q57_dificultad_falta_oferta'] == 1.0:
            return 'Falta de oferta/no consigo trabajo'
        if row['q57_dificultad_desconocimiento'] == 1.0:
            return 'No sé dónde buscar trabajo'
        if row['q57_dificultad_prefiero_no'] == 1.0:
            return 'Prefiero no responder'
        return np.nan

    df_2023['tipo_dificultad_trabajo'] = df_2023.apply(resolver_dificultad_trabajo_tipo_2023, axis=1)
    df_2023.drop(columns=[
        'q57_dificultad_trabajo', 'q57_dificultad_titulos', 'q57_dificultad_discriminacion',
        'q57_dificultad_hogar', 'q57_dificultad_sexual', 'q57_dificultad_documentacion',
        'q57_dificultad_idioma', 'q57_dificultad_edad', 'q57_dificultad_inexperiencia',
        'q57_dificultad_falta_oferta', 'q57_dificultad_salud', 'q57_dificultad_desconocimiento',
        'q57_dificultad_prefiero_no'
    ], inplace=True)

    #ENVIO DE DINERO AL EXTERIOR
    #VALIDAR: 2020 pregunta si cambió el monto enviado (aumentó/disminuyó/igual/no pudo enviar
    # más) y 2023 pregunta frecuencia (regular/de vez en cuando/no); solo se puede comparar la
    # dimensión "envía o no envía dinero". Se pierde el detalle de variación (2020) y de
    # frecuencia (2023). "Prefiero no responder" (2023) no encuadra en Sí/No y queda sin dato.
    df_2020['envia_dinero_exterior'] = df_2020['q48_remesas'].replace({
        'Envío más': 'Sí',
        'Envío menos': 'Sí',
        'Se mantuvo igual el envío': 'Sí',
        'No pude enviar más': 'Sí',
        'No envío dinero': 'No'
    })
    df_2020.drop(columns=['q48_remesas'], inplace=True)

    df_2023['envia_dinero_exterior'] = df_2023['q58_envio_dinero'].replace({
        'Sí, regularmente': 'Sí',
        'Sí, de vez en cuando': 'Sí',
        'Prefiero no responder': np.nan
    })
    df_2023.drop(columns=['q58_envio_dinero'], inplace=True)

    #RECIBE AYUDA ECONOMICA/ALIMENTARIA (binario, según tablero)
    #VALIDAR: se complementa con q52_programas_* (detalle de programas estatales específicos: AUH,
    # jubilación, pensión, PROGRESAR, Potenciar Trabajo, comedor, PUAM, monotributo social, etc.)
    # para resolver los casos "No sé" que tenían algún programa marcado. Hay ~358 casos que
    # marcaron "No, me mantengo con mi salario..." en q51 pero igual tienen un programa específico
    # marcado en q52 (posible inconsistencia de carga o beneficio percibido por otro miembro del
    # hogar); no se sobrescribe ese "No" automáticamente, queda tal cual respondieron.
    columnas_programas_2020 = [
        'q52_programas_auh', 'q52_programas_jubilacion', 'q52_programas_pension',
        'q52_programas_discpacidad', 'q52_programas_progresar', 'q52_programas_provincial',
        'q52_programas_comedor', 'q52_programas_puam', 'q52_programas_subsidio',
        'q52_programas_comida', 'q52_programas_monotributo', 'q52_programas_otro'
    ]

    def resolver_recibe_ayuda_2020(row):
        if pd.notna(row['q51_ayudas_no']):
            return 'No'
        columnas_ayuda = [
            'q51_ayudas_estado', 'q51_ayudas_comedores', 'q51_ayudas_organismos', 'q51_ayudas_iglesia',
            'q51_ayudas_organizaciones', 'q51_ayudas_paisorigen', 'q51_ayudas_comunidad'
        ]
        if row[columnas_ayuda].notna().any():
            return 'Sí'
        if row[columnas_programas_2020].notna().any():
            return 'Sí'
        return 'No sé'

    df_2020['recibe_ayuda_economica'] = df_2020.apply(resolver_recibe_ayuda_2020, axis=1)
    df_2020.drop(columns=[
        'q51_ayudas_no', 'q51_ayudas_estado', 'q51_ayudas_comedores', 'q51_ayudas_organismos',
        'q51_ayudas_iglesia', 'q51_ayudas_organizaciones', 'q51_ayudas_paisorigen', 'q51_ayudas_comunidad'
    ] + columnas_programas_2020, inplace=True)
    df_2020.drop(columns=['q52_programas_no'], inplace=True)

    def resolver_recibe_ayuda_2023(row):
        if row['q60_subsidios_prefiero_no'] == 1:
            return 'No sé'
        if row['q60_subsidios_no'] == 1:
            return 'No'
        if row['q60_subsidios_no'] == 0:
            return 'Sí'
        return 'No sé'

    df_2023['recibe_ayuda_economica'] = df_2023.apply(resolver_recibe_ayuda_2023, axis=1)
    df_2023.drop(columns=[
        'q60_subsidios', 'q60_subsidios_no', 'q60_subsidios_auh', 'q60_subsidios_embarazo',
        'q60_subsidios_jubilacion', 'q60_subsidios_pension', 'q60_subsidios_pension_no_contrib',
        'q60_subsidios_progresar', 'q60_subsidios_potenciar_trabajo', 'q60_subsidios_inclusion_joven',
        'q60_subsidios_tarjeta_alimentar', 'q60_subsidios_pieza', 'q60_subsidios_desempleo',
        'q60_subsidios_otro', 'q60_subsidios_prefiero_no', 'q60_subsidios_especificar'
    ], inplace=True)

    #VALIDAR: pregunta nueva de 2023, sin equivalente en 2020 (queda en NaN para ese año).
    df_2020['dificultad_gestion_subsidios'] = np.nan
    df_2023['dificultad_gestion_subsidios'] = df_2023['q61_subsidios_problemas']
    df_2023.drop(columns=['q61_subsidios_problemas'], inplace=True)

    # Tablero: pendiente / eliminar esta columna. Pregunta nueva de 2023, sin equivalente en 2020.
    df_2023.drop(columns=[
        'q59_gastos', 'q59_gastos_ahorros', 'q59_gastos_préstamos_entorno', 'q59_gastos_préstamos_bancos',
        'q59_gastos_cuotas', 'q59_gastos_fiado', 'q59_gastos_venta_pertenencias', 'q59_gastos_ayuda_estatal',
        'q59_gastos_ayuda_organizaciones', 'q59_gastos_ninguna', 'q59_gastos_prefiero_no'
    ], inplace=True)

    #DISCRIMINACION EXPERIMENTADA (homologado a No / Sí, alguna vez / Sí)
    df_2020['discriminacion_experimentada'] = df_2020['q53_discriminacion'].replace({
        'No, nunca': 'No',
        'Sí, esporádicamente': 'Sí',
        'Sí, frecuentemente': 'Sí',
        'Sí, siempre': 'Sí'
    })
    df_2020.drop(columns=['q53_discriminacion'], inplace=True)

    df_2023['discriminacion_experimentada'] = df_2023['q62_discriminacion'].replace({
        'No, nunca': 'No',
        'Sí, frecuentemente': 'Sí'
    })
    df_2023.drop(columns=['q62_discriminacion'], inplace=True)

    #LUGAR DE DISCRIMINACION (una sola columna, priorización)
    #VALIDAR: "Por parte de fuerzas de seguridad y control" es una categoría nueva de 2023, sin
    # equivalente en 2020; se agrupa en "Otros" según lo indicado. Prioridad: trámites del Estado >
    # atención médica > escuela/universidad > trabajo > transporte público > calle > grupos
    # sociales > medios de comunicación > otros.
    def resolver_lugar_discriminacion_2020(row):
        if pd.notna(row['q54_lugares_estado']):
            return 'Trámites del Estado'
        if pd.notna(row['q54_lugares_salud']):
            return 'Atención médica'
        if pd.notna(row['q54_lugares_estudio']):
            return 'Escuela y/o universidad'
        if pd.notna(row['q54_lugares_trabajo']):
            return 'Trabajo'
        if pd.notna(row['q54_lugares_transporte']):
            return 'Transporte público'
        if pd.notna(row['q54_lugares_calle']):
            return 'Calle'
        if pd.notna(row['q54_lugares_grupos']):
            return 'Grupos sociales'
        if pd.notna(row['q54_lugares_medios']):
            return 'Medios de comunicación'
        if pd.notna(row['q54_lugares_otros']):
            return 'Otros'
        return np.nan

    df_2020['lugar_discriminacion'] = df_2020.apply(resolver_lugar_discriminacion_2020, axis=1)
    df_2020.drop(columns=[
        'q54_lugares_estado', 'q54_lugares_salud', 'q54_lugares_estudio', 'q54_lugares_calle',
        'q54_lugares_trabajo', 'q54_lugares_grupos', 'q54_lugares_transporte', 'q54_lugares_medios',
        'q54_lugares_otros'
    ], inplace=True)

    def resolver_lugar_discriminacion_2023(row):
        if row['q63_discriminacion_estado'] == 1.0:
            return 'Trámites del Estado'
        if row['q63_discriminacion_atencion_medica'] == 1.0:
            return 'Atención médica'
        if row['q63_discriminacion_educacion'] == 1.0:
            return 'Escuela y/o universidad'
        if row['q63_discriminacion_trabajo'] == 1.0:
            return 'Trabajo'
        if row['q63_discriminacion_transporte'] == 1.0:
            return 'Transporte público'
        if row['q63_discriminacion_calle'] == 1.0:
            return 'Calle'
        if row['q63_discriminacion_grupos_sociales'] == 1.0:
            return 'Grupos sociales'
        if row['q63_discriminacion_medios_comunicacion'] == 1.0:
            return 'Medios de comunicación'
        if row['q63_discriminacion_fuerzas'] == 1.0 or row['q63_discriminacion_otros'] == 1.0:
            return 'Otros'
        return np.nan

    df_2023['lugar_discriminacion'] = df_2023.apply(resolver_lugar_discriminacion_2023, axis=1)
    df_2023.drop(columns=[
        'q63_discriminacion', 'q63_discriminacion_estado', 'q63_discriminacion_fuerzas',
        'q63_discriminacion_atencion_medica', 'q63_discriminacion_educacion', 'q63_discriminacion_calle',
        'q63_discriminacion_trabajo', 'q63_discriminacion_grupos_sociales', 'q63_discriminacion_transporte',
        'q63_discriminacion_medios_comunicacion', 'q63_discriminacion_otros', 'q63_discriminacion_especificar'
    ], inplace=True)

    #VIOLENCIA POR FUERZAS DE SEGURIDAD (homologado a No / Sí, alguna vez / Sí)
    df_2020['violencia_fuerza_seguridad'] = df_2020['q55_violencia'].replace({
        'No, nunca': 'No',
        'Sí, esporádicamente': 'Sí',
        'Sí, frecuentemente': 'Sí',
        'Sí, siempre': 'Sí'
    })
    df_2020['violencia_fuerza_seguridad'] = df_2020['violencia_fuerza_seguridad'].fillna('Prefiero no responder')
    df_2020.drop(columns=['q55_violencia'], inplace=True)

    df_2023['violencia_fuerza_seguridad'] = df_2023['q64_violencia_fuerza_seguridad'].replace({
        'No, nunca': 'No',
        'Sí, frecuentemente': 'Sí'
    })
    df_2023['violencia_fuerza_seguridad'] = df_2023['violencia_fuerza_seguridad'].fillna('Prefiero no responder')
    df_2023.drop(columns=['q64_violencia_fuerza_seguridad'], inplace=True)

    #VIOLENCIA POR RAZONES DE GENERO
    #VALIDAR: "Tal vez" (2020) se agrupa en "Prefiero no responder" al no encuadrar en Sí/No.
    df_2020['violencia_genero'] = df_2020['q56_violencia_genero'].replace({
        'Tal vez': 'Prefiero no responder',
        'No quiero responder': 'Prefiero no responder'
    })
    df_2020.drop(columns=['q56_violencia_genero'], inplace=True)

    df_2023['violencia_genero'] = df_2023['q65_violencia_genero']
    df_2023.drop(columns=['q65_violencia_genero'], inplace=True)

    #TIPO DE PARTICIPACION EN ORGANIZACIONES (una sola columna, formato 2020)
    #VALIDAR: en 2020 "Organización social" y "Organización barrial o comunitaria" son categorías
    # separadas, pero en 2023 se fusionan en una sola ("Organización social, barrial o
    # comunitaria"); se unifican también en 2020 bajo ese mismo nombre para poder comparar.
    # "Movimiento social" es una categoría nueva de 2023, sin equivalente en 2020. Prioridad:
    # No participo en ninguna > Organización de migrantes > Organización social, barrial o
    # comunitaria > Movimiento social > Partido político > Iglesia o comunidad religiosa >
    # Cooperativa de trabajo o sindicato > Otra > Prefiero no responder.
    def resolver_participacion_2020(row):
        if pd.notna(row['q57_participacion_no']):
            return 'No participo en ninguna'
        if pd.notna(row['q57_participacion_orgamigrantes']):
            return 'Organización de migrantes'
        if pd.notna(row['q57_participacion_orgasocial']) or pd.notna(row['q57_participacion_orgabarrial']):
            return 'Organización social, barrial o comunitaria'
        if pd.notna(row['q57_participacion_partido']):
            return 'Partido político'
        if pd.notna(row['q57_participacion_iglesia']):
            return 'Iglesia o comunidad religiosa'
        if pd.notna(row['q57_participacion_cooperativa']):
            return 'Cooperativa de trabajo o sindicato'
        if pd.notna(row['q57_participacion_otra']):
            return 'Otra'
        return np.nan

    df_2020['tipo_participacion_organizacion'] = df_2020.apply(resolver_participacion_2020, axis=1)
    df_2020['tipo_participacion_organizacion'] = df_2020['tipo_participacion_organizacion'].fillna('Prefiero no responder')
    df_2020.drop(columns=[
        'q57_participacion_no', 'q57_participacion_orgasocial', 'q57_participacion_orgabarrial',
        'q57_participacion_partido', 'q57_participacion_orgamigrantes', 'q57_participacion_iglesia',
        'q57_participacion_cooperativa', 'q57_participacion_otra'
    ], inplace=True)

    def resolver_participacion_2023(row):
        if row['q66_participacion_organizacion'] == 'No':
            return 'No participo en ninguna'
        if row['q66_participacion_organizacion'] == 'Prefiero no responder':
            return 'Prefiero no responder'
        if row['q67_organizacion_migrantes'] == 1.0:
            return 'Organización de migrantes'
        if row['q67_organizacion_social'] == 1.0:
            return 'Organización social, barrial o comunitaria'
        if row['q67_organizacion_movimiento_social'] == 1.0:
            return 'Movimiento social'
        if row['q67_organizacion_partido'] == 1.0:
            return 'Partido político'
        if row['q67_organizacion_religiosa'] == 1.0:
            return 'Iglesia o comunidad religiosa'
        if row['q67_organizacion_cooperativa'] == 1.0:
            return 'Cooperativa de trabajo o sindicato'
        if row['q67_organizacion_otra'] == 1.0:
            return 'Otra'
        return np.nan

    df_2023['tipo_participacion_organizacion'] = df_2023.apply(resolver_participacion_2023, axis=1)
    df_2023['tipo_participacion_organizacion'] = df_2023['tipo_participacion_organizacion'].fillna('Prefiero no responder')
    df_2023.drop(columns=[
        'q66_participacion_organizacion', 'q67_organizacion_', 'q67_organizacion_migrantes',
        'q67_organizacion_social', 'q67_organizacion_movimiento_social', 'q67_organizacion_partido',
        'q67_organizacion_religiosa', 'q67_organizacion_cooperativa', 'q67_organizacion_otra',
        'q67_organizacion_especificar'
    ], inplace=True)

    #VOTO EN ELECCIONES LOCALES (binarizado como 2023)
    #VALIDAR: "No sabía que tenía este derecho", "No, en mi localidad no reconocen este derecho",
    # "No me interesa votar" y "No he podido votar" (2020) se agrupan todas en "No", perdiendo el
    # detalle del motivo por el que no votó (ver motivo_no_voto más abajo).
    df_2020['voto_elecciones_locales'] = df_2020['q58_voto'].replace({
        'Sí, he votado': 'Sí',
        'No sabía que tenía este derecho': 'No',
        'No, en mi localidad no reconocen este derecho': 'No',
        'No me interesa votar': 'No',
        'No he podido votar': 'No'
    })

    df_2023['voto_elecciones_locales'] = df_2023['q68_participacion_elecciones_locales'].replace({'Si': 'Sí'})
    df_2023.drop(columns=['q68_participacion_elecciones_locales'], inplace=True)

    #MOTIVO DE NO VOTO
    def resolver_motivo_no_voto_2020(row):
        if row['q58_voto'] == 'No sabía que tenía este derecho':
            return 'No sabía que tenía este derecho'
        if row['q58_voto'] == 'No me interesa votar':
            return 'No me interesa votar'
        if row['q58_voto'] == 'No, en mi localidad no reconocen este derecho':
            return 'En mi localidad no lo permiten / no está habilitado'
        if row['q58_voto'] == 'No he podido votar':
            if pd.notna(row['q59_causas_dni']):
                return 'No tengo DNI'
            if pd.notna(row['q59_causas_anios']):
                return 'No tengo la suficiente antigüedad'
            if pd.notna(row['q59_causas_padron']):
                return 'No estoy inscripto/a en el padrón'
            if pd.notna(row['q59_causas_distancia']):
                return 'Vivo lejos de las mesas de votación'
            if pd.notna(row['q59_causas_lugar']):
                return 'No sé dónde, cómo o qué se vota en las elecciones'
            if pd.notna(row['q59_causas_nose']):
                return 'No sabía que tenía este derecho'
            return np.nan
        return np.nan

    df_2020['motivo_no_voto'] = df_2020.apply(resolver_motivo_no_voto_2020, axis=1)
    df_2020.drop(columns=[
        'q58_voto', 'q59_causas_anios', 'q59_causas_distancia', 'q59_causas_dni',
        'q59_causas_lugar', 'q59_causas_nose', 'q59_causas_padron'
    ], inplace=True)

    def resolver_motivo_no_voto_2023(row):
        if row['q69_participacion_no_sabia'] == 1.0:
            return 'No sabía que tenía este derecho'
        if row['q69_participacion_no_interes'] == 1.0:
            return 'No me interesa votar'
        if row['q69_participacion_no_dni'] == 1.0:
            return 'No tengo DNI'
        if row['q69_participacion_no_antiguedad'] == 1.0:
            return 'No tengo la suficiente antigüedad'
        if row['q69_participacion_no_padron'] == 1.0:
            return 'No estoy inscripto/a en el padrón'
        if row['q69_participacion_no_lejania'] == 1.0:
            return 'Vivo lejos de las mesas de votación'
        if row['q69_participacion_no_desconocimiento'] == 1.0:
            return 'No sé dónde, cómo o qué se vota en las elecciones'
        if row['q69_participacion_no_permiso'] == 1.0:
            return 'En mi localidad no lo permiten / no está habilitado'
        return np.nan

    df_2023['motivo_no_voto'] = df_2023.apply(resolver_motivo_no_voto_2023, axis=1)
    df_2023.drop(columns=[
        'q69_participacion_no_', 'q69_participacion_no_sabia', 'q69_participacion_no_interes',
        'q69_participacion_no_dni', 'q69_participacion_no_antiguedad', 'q69_participacion_no_padron',
        'q69_participacion_no_lejania', 'q69_participacion_no_desconocimiento', 'q69_participacion_no_permiso'
    ], inplace=True)

    #VOTO EN ELECCIONES DEL PAIS DE ORIGEN (binarizado Sí/No)
    #VALIDAR: "No, mi país no lo permite", "No, no sé si mi país lo permite" y "No, no me interesa"
    # (2020) se agrupan todas en "No", perdiendo el detalle del motivo.
    df_2020['voto_elecciones_pais_origen'] = df_2020['q60_voto_extranjero'].replace({
        'Sí, siempre': 'Sí',
        'Sí, alguna vez': 'Sí',
        'No, mi país no lo permite': 'No',
        'No, no sé si mi país lo permite': 'No',
        'No, no me interesa': 'No'
    })
    df_2020['voto_elecciones_pais_origen'] = df_2020['voto_elecciones_pais_origen'].fillna('Prefiero no responder')
    df_2020.drop(columns=['q60_voto_extranjero'], inplace=True)

    df_2023['voto_elecciones_pais_origen'] = df_2023['q70_paricipacion_elecciones_extranjero'].replace({
        'Sí, sólo una vez': 'Sí',
        'Sí, solo una vez': 'Sí',
        'Sí, dos o más veces': 'Sí',
        'Sí, siempre': 'Sí'
    })
    df_2023['voto_elecciones_pais_origen'] = df_2023['voto_elecciones_pais_origen'].fillna('Prefiero no responder')
    df_2023.drop(columns=['q70_paricipacion_elecciones_extranjero'], inplace=True)

    #MOTIVO DE NO VOTO EN EL EXTRANJERO (solo 2023 — pregunta nueva, sin equivalente en 2020)
    df_2020['motivo_no_voto_extranjero'] = np.nan
    df_2023['motivo_no_voto_extranjero'] = df_2023['q71_participacion_no_motivo']
    df_2023.drop(columns=['q71_participacion_no_motivo'], inplace=True)

    #SITUACION DE VIDA EN ARGENTINA (CIERRE)
    df_2020['situacion_vida_argentina'] = df_2020['q61_situacion_anio']
    df_2020.drop(columns=['q61_situacion_anio'], inplace=True)

    df_2023['situacion_vida_argentina'] = df_2023['q72_situacion_argentina_2anos']
    df_2023.drop(columns=['q72_situacion_argentina_2anos'], inplace=True)
    
    #PREGUNTAS ELIMINADAS
    #nivel castellano
    df_2020.drop(columns=['q6_nivel_castellano'], inplace=True)
    df_2023.drop(columns=['q7_nivel_castellano'], inplace=True)

    #naturalizacion
    df_2020.drop(columns=['q16_naturalizacion'], inplace=True)
    df_2023.drop(columns=['q25_naturalizacion'], inplace=True)

    #pandemia
    df_2020.drop(columns=[
        'q23_continuidad_no', 'q23_continuidad_mail', 'q23_continuidad_zoom', 'q23_continuidad_radio',
        'q23_continuidad_tv', 'q23_continuidad_plataforma', 'q23_continuidad_telefono',
        'q23_continuidad_cuadernillosdig', 'q23_continuidad_cuadernillos', 'q23_continuidad_presencial',
        'q23_continuidad_redes', 'q23_continuidad_telfijo', 'q23_continuidad_otro',
        'q24_dificultades_acompaniamiento', 'q24_dificultades_dispositivos', 'q24_dificultades_docentes',
        'q24_dificultades_hogar', 'q24_dificultades_internet', 'q24_dificultades_motivacion',
        'q24_dificultades_no', 'q24_dificultades_otras',
        'q30_covid', 'q36_covidvivienda_renovacion', 'q36_covidvivienda_expulsion',
        'q36_covidvivienda_desalojo', 'q36_covidvivienda_aumento', 'q36_covidvivienda_amenaza',
        'q36_covidvivienda_pago', 'q36_covidvivienda_nopbm', 'q36_covidvivienda_otro',
        'q41_continuidad', 'q41_otro', 'q50_ife'
    ], inplace=True)

    #PESOS MUESTRALES
    # Nota: mismo concepto (ponderador para estimaciones), distinto nombre entre años. Los valores
    # vienen con coma como separador decimal en ambos años; se convierten a float con punto.
    df_2020['peso_muestral_total'] = df_2020['pesos_para_estimaciones_totales'].astype(str).str.replace(',', '.').astype(float)
    df_2020['peso_muestral_nacionalidad'] = df_2020['pesos_para_estimaciones_por_nacionalidad'].astype(str).str.replace(',', '.').astype(float)
    df_2020.drop(columns=['pesos_para_estimaciones_totales', 'pesos_para_estimaciones_por_nacionalidad'], inplace=True)

    df_2023['peso_muestral_total'] = df_2023['weightvec'].astype(str).str.replace(',', '.').astype(float)
    df_2023['peso_muestral_nacionalidad'] = df_2023['weightvec_0'].astype(str).str.replace(',', '.').astype(float)
    df_2023.drop(columns=['weightvec', 'weightvec_0'], inplace=True)

    #COLUMNAS SIN PAR (sin equivalente en el otro año, no armonizables)
    df_2020.drop(columns=[
        'documentos_i', 'edad_i', 'estudios_i', 'language', 'q14_otros',
        'q21_establecimiento_mixto', 'q21_establecimiento_privado', 'q21_establecimiento_publico',
        'q43_trab_registrado', 'q45_trabajo_interrupcion',
        'q49_deudas_agencias', 'q49_deudas_amigosarg', 'q49_deudas_bancoarg', 'q49_deudas_bancosorigen',
        'q49_deudas_familiaresorig', 'q49_deudas_no', 'q5_idioma', 'q5_otro'
    ], inplace=True)
    df_2023.drop(columns=[
        'anios_residencia', 'motivos_habitat', 'nacionalidad_agrup', 'niveled_agrup',
        'q19_documento_detalle', 'q21_dificultad_dni_detalle', 'q21_dni_dificultad', 'q21_dni_dificultad_turnos.1',
        'q4_otro', 'q5_descendencia', 'q5_descendencia_otro_descrip', 'q6_idioma', 'q6_otro', 'sec_completo_agrup'
    ], inplace=True)

    print("ETL completado con éxito.")
    print(" ")

    df_2020['Año'] = 2020
    df_2023['Año'] = 2023

    columnas_comunes = [c for c in df_2020.columns if c in df_2023.columns and c != 'Año']
    columnas_comunes = ['Año'] + columnas_comunes

    df_final = pd.concat([df_2020[columnas_comunes], df_2023[columnas_comunes]], ignore_index=True)

    ruta_salida = r'C:\Users\Usuario\ENMA\data\processed'
    os.makedirs(ruta_salida, exist_ok=True)
    ruta_archivo = os.path.join(ruta_salida, 'ENMA.csv')
    df_final.to_csv(ruta_archivo, index=False, encoding='utf-8-sig')

    print(" ")
    print(f"Archivo final guardado en: {ruta_archivo}")
    print(f"Filas: {len(df_final)} | Columnas: {len(df_final.columns)}")

if __name__ == "__main__":
    run_etl()