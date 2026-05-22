import streamlit as st
import pandas as pd

# Configuración inicial de la página
st.set_page_config(page_title="Calculadora Nutricional OMS", layout="centered")

@st.cache_data
def load_data():
    # Asegúrate de que los archivos CSV estén en la misma carpeta que app.py en GitHub
    df_boys = pd.read_csv("wfl_boys_0-to-2-years_zscores.csv")
    df_girls = pd.read_csv("wfl_girls_0-to-2-years_zscores.csv")
    return df_boys, df_girls

def calcular_zscore(peso_kg, l, m, s):
    # Aplicación de la fórmula LMS de la OMS
    if l == 0:
        import math
        return math.log(peso_kg / m) / s
    else:
        return (((peso_kg / m) ** l) - 1) / (l * s)

st.title("Calculadora de Estado Nutricional (0-2 años)")
st.markdown("Cálculo de Peso para la Longitud basado en los estándares de la OMS.")

# Sección de Entrada de Datos
st.header("Datos del Paciente")
col1, col2 = st.columns(2)

with col1:
    sexo = st.selectbox("Sexo:", ["Niño", "Niña"])
    # Las tablas OMS de longitud van usualmente hasta 110 cm
    talla_cm = st.number_input("Talla (cm)", min_value=45.0, max_value=110.0, value=65.0, step=0.5)

with col2:
    peso_g = st.number_input("Peso exacto (gramos)", min_value=1000, value=7500, step=10)

# Convertir gramos a kilogramos
peso_kg = peso_g / 1000.0

# Carga de las tablas
try:
    df_boys, df_girls = load_data()
    df = df_boys if sexo == "Niño" else df_girls
except FileNotFoundError:
    st.error("Error: No se encontraron los archivos CSV. Verifica que estén en el repositorio.")
    st.stop()

# Redondear la talla ingresada al 0.5 cm más cercano (resolución de tablas OMS)
talla_redondeada = round(talla_cm * 2) / 2
row = df[df['Length'] == talla_redondeada]

if not row.empty:
    # Extraer parámetros LMS
    l = row['L'].values[0]
    m = row['M'].values[0]  # M es la Mediana (Peso Ideal)
    s = row['S'].values[0]

    # Calcular Z-Score
    z_score = calcular_zscore(peso_kg, l, m, s)
    peso_ideal = m

    st.markdown("---")
    st.subheader("Resultados")
    
    res_col1, res_col2, res_col3 = st.columns(3)
    res_col1.metric("Peso Ingresado", f"{peso_kg:.3f} kg")
    res_col2.metric("Peso Ideal (Mediana)", f"{peso_ideal:.3f} kg")
    res_col3.metric("Z-Score (Desv. Est.)", f"{z_score:.2f}")

    # Lógica de Clasificación Nutricional
    st.markdown("### Diagnóstico")
    
    if z_score > 3:
        st.warning("Obesidad (> 3 DE)")
    elif 2 < z_score <= 3:
        st.warning("Sobrepeso (> 2 DE)")
    elif 1 < z_score <= 2:
        st.info("Riesgo de sobrepeso (> 1 DE)")
    elif -1 <= z_score <= 1:
        st.success("Estado Nutricional Normal")
    elif -2 <= z_score < -1:
        st.warning("Riesgo de desnutrición (Entre -1 y -2 DE)")
    elif -3 <= z_score < -2:
        # Aquí aplicamos tu lógica de proximidad
        if z_score >= -2.5:
            st.error("Desnutrición aguda moderada (Tendencia hacia -2 / más estable)")
        else:
            st.error("Desnutrición aguda moderada (Tendencia hacia -3 / límite con severa)")
    else: # z_score < -3
        st.error("Desnutrición aguda severa (< -3 DE)")

else:
    st.error("La talla ingresada está fuera del rango de las tablas de 0 a 2 años (45cm - 110cm).")
