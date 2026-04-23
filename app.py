"""
app.py - Punto de entrada principal de la aplicacion de Analisis de Datos.
Orquesta la carga del dataset y renderiza los tres tabs principales.
"""
import streamlit as st
from config import APP_TITLE, APP_SUBTITLE, CSS
from data_loader import cargar_datos

# --- Modulos de tabs ---
from tabs import tab_exploracion, tab_calidad, tab_graficos

# ---------------------------------------------------------------
# CONFIGURACION DE PAGINA
# ---------------------------------------------------------------
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="chart_with_upwards_trend",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------
# ENCABEZADO INSTITUCIONAL
# ---------------------------------------------------------------
st.title(APP_TITLE)
st.markdown(f"#### {APP_SUBTITLE}")
st.write("---")

# ---------------------------------------------------------------
# PANEL LATERAL
# ---------------------------------------------------------------
with st.sidebar:
    st.markdown("## Panel de Control")
    archivo = st.file_uploader("Cargar dataset (.csv)", type=["csv"])
    st.divider()
    st.markdown("**Formato del archivo**")
    separador = st.radio("Delimitador de columnas:", [";", ","], horizontal=True)
    decimal   = st.radio("Separador decimal:",        [",", "."], horizontal=True)


# ---------------------------------------------------------------
# ESTADO DE SESION  (persiste cambios de limpieza entre reruns)
# ---------------------------------------------------------------
SESSION_KEY = "df_activo"

if archivo is not None:
    # Solo recarga si cambia el archivo
    nombre = archivo.name
    if st.session_state.get("nombre_archivo") != nombre:
        df_cargado, error = cargar_datos(archivo, separador, decimal)
        if error:
            st.error(f"Error al cargar el archivo: {error}")
            st.stop()
        st.session_state[SESSION_KEY]        = df_cargado
        st.session_state["nombre_archivo"]   = nombre

    df = st.session_state.get(SESSION_KEY)
    if df is None:
        st.error("No se pudo cargar el archivo. Intente de nuevo.")
        st.stop()

    # ---------------------------------------------------------------
    # METRICAS RAPIDAS
    # ---------------------------------------------------------------
    m1, m2, m3, m4, m5 = st.columns(5)
    total_nulos  = df.isnull().sum().sum()
    completitud  = round((1 - total_nulos / df.size) * 100, 2) if df.size > 0 else 100.0
    n_duplicados = df.duplicated().sum()

    m1.metric("Registros",    df.shape[0])
    m2.metric("Variables",    df.shape[1])
    m3.metric("Nulos",        int(total_nulos))
    m4.metric("Integridad",   f"{completitud}%")
    m5.metric("Duplicados",   int(n_duplicados))

    st.write("")

    # ---------------------------------------------------------------
    # TABS PRINCIPALES
    # ---------------------------------------------------------------
    tab1, tab2, tab3 = st.tabs([
        "Exploracion de Datos",
        "Calidad y Limpieza",
        "Analisis Visual",
    ])

    with tab1:
        tab_exploracion.render(df)

    with tab2:
        tab_calidad.render(SESSION_KEY)

    with tab3:
        # Siempre usa el df actualizado desde session_state
        tab_graficos.render(st.session_state[SESSION_KEY])

else:
    # ---------------------------------------------------------------
    # PANTALLA DE BIENVENIDA
    # ---------------------------------------------------------------
    st.markdown("## Bienvenido al Sistema de Analisis de Datos")
    st.info("Carga un archivo CSV usando el panel lateral para comenzar el analisis.")

    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.markdown("**Exploracion**\n\nTabla de datos, tipos de variables y estadisticos descriptivos completos.")
    col_b.markdown("**Calidad**\n\nDiagnostico de nulos, heatmap de ausentes, imputacion y deteccion de duplicados.")
    col_c.markdown("**Graficos Univariados**\n\nHistograma+KDE, boxplot, violin, densidad, Q-Q plot y tallo y hoja.")
    col_d.markdown("**Graficos Avanzados**\n\nDispersion, elipse de confianza, correlacion, coordenadas paralelas y radar.")
