"""
tabs/tab_atipicos.py
Tab 4 - Identificacion de Datos Atipicos.

Cubre las diapositivas del ingeniero:
  Diapo 55  : Circulo de Correlaciones
  Diapo 56  : Definicion y estructura del boxplot con percentiles
  Diapo 57  : Limites superior/inferior, minimo/maximo
  Diapo 58  : Formula IQR factor 1.5
  Diapo 59  : Formula IQR factor 3.0 (outliers extremos)
  Diapo 60  : Identificacion de atipicos con EjemploEstudiantes.csv
  Diapo 61  : Boxplot de notas escolares y servicio al cliente
"""
import streamlit as st
from data_loader import cols_numericas
from charts import multivariado, atipicos


def render(df):
    st.subheader("Identificacion de Datos Atipicos (Outliers)")

    num_cols = cols_numericas(df)
    if len(num_cols) < 2:
        st.warning("Se necesitan al menos 2 variables numericas para este analisis.")
        return

    # -----------------------------------------------------------------------
    # SECCION A: Circulo de Correlaciones (diapo 55)
    # -----------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### Circulo de Correlaciones")
    with st.expander("¿Que es el Circulo de Correlaciones?", expanded=False):
        st.markdown(
            """
            El **Circulo de Correlaciones** muestra cada variable como un vector en el plano
            de los dos primeros componentes principales (CP1 y CP2).

            - **Vectores cercanos** (angulo pequeño) → variables **correlacionadas positivamente**.
            - **Vectores opuestos** (angulo ~180°) → variables **correlacionadas negativamente**.
            - **Vectores perpendiculares** (angulo ~90°) → variables **sin correlacion**.
            - La **longitud** del vector indica cuanto contribuye esa variable a los componentes.

            *Nota: CP1 y CP2 son calculados a partir de la matriz de correlacion de Pearson usando
            descomposicion espectral. No requiere librerias externas.*
            """
        )

    cols_circulo = st.multiselect(
        "Variables para el Circulo de Correlaciones:",
        options=num_cols,
        default=num_cols[:min(5, len(num_cols))],
        key="circulo_vars",
    )
    if len(cols_circulo) >= 2:
        fig_circ = multivariado.circulo_correlaciones(df, cols_circulo)
        st.plotly_chart(fig_circ, use_container_width=True)
    else:
        st.info("Selecciona al menos 2 variables.")

    # -----------------------------------------------------------------------
    # SECCION B: Teoria del Boxplot con Percentiles (diapos 56-59)
    # -----------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### Diagrama de Caja y Bigotes (Boxplot) con Percentiles")

    with st.expander("Teoria: componentes del boxplot y regla IQR", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(
                """
                **Componentes del boxplot:**
                | Elemento | Descripcion |
                |---|---|
                | **Min / Max** | Valores extremos que NO son atipicos |
                | **Li (Limite Inferior)** | Bigote inferior — valores dentro del rango |
                | **Ls (Limite Superior)** | Bigote superior — valores dentro del rango |
                | **Q1 (P25)** | Primer cuartil: 25% de los datos quedan por debajo |
                | **Q2 / Mediana (P50)** | Valor central de la distribucion |
                | **Q3 (P75)** | Tercer cuartil: 75% de los datos quedan por debajo |
                | **IQR / RIC** | Rango intercuartil = Q3 − Q1 (50% central) |
                | **Atipico ◆** | Valor fuera de los limites IQR |
                """
            )
        with c2:
            st.markdown(
                r"""
                **Reglas para detectar atipicos:**

                *Outliers moderados (factor = 1.5):*
                $$L_s = Q_3 + 1.5 \times IQR$$
                $$L_i = Q_1 - 1.5 \times IQR$$

                *Outliers extremos (factor = 3.0):*
                $$L_s = Q_3 + 3 \times IQR$$
                $$L_i = Q_1 - 3 \times IQR$$

                Cualquier valor fuera de estos limites se considera **dato atipico**.
                """
            )

    # -----------------------------------------------------------------------
    # SECCION C: Boxplot interactivo con percentiles (diapo 60-61)
    # -----------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### Analisis de Atipicos por Variable")

    col_izq, col_der = st.columns([1, 2])
    with col_izq:
        col_sel = st.selectbox(
            "Variable a analizar:",
            options=num_cols,
            key="atip_col",
        )
        factor_sel = st.radio(
            "Factor IQR:",
            options=[1.5, 3.0],
            format_func=lambda x: f"{x} (outliers {'moderados' if x == 1.5 else 'extremos'})",
            key="atip_factor",
            horizontal=False,
        )

        lims = atipicos.calcular_limites(df[col_sel].dropna(), factor_sel)
        st.markdown("**Estadisticos de referencia:**")
        for k, v in lims.items():
            if k != "factor":
                st.metric(k, v)

    with col_der:
        fig_bp = atipicos.boxplot_percentiles(df, col_sel, factor_sel)
        st.plotly_chart(fig_bp, use_container_width=True)

    # Tabla de atipicos
    st.markdown("#### Tabla de Datos Atipicos Detectados")
    df_out = atipicos.tabla_atipicos(df, col_sel, factor_sel)
    if len(df_out) == 0:
        st.success(
            f"No se detectaron datos atipicos en '{col_sel}' "
            f"con factor IQR = {factor_sel}."
        )
    else:
        st.error(
            f"Se detectaron **{len(df_out)} dato(s) atipico(s)** en '{col_sel}' "
            f"con factor IQR = {factor_sel}."
        )
        st.dataframe(
            df_out.style.apply(
                lambda row: [
                    "background-color: #fde8e8" if row["Tipo"] == "Superior"
                    else "background-color: #e8f0fe"
                ] * len(row),
                axis=1,
            ),
            use_container_width=True,
        )

    # -----------------------------------------------------------------------
    # SECCION D: Boxplot comparativo (notas escolares — diapo 61)
    # -----------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### Boxplot Comparativo — Multiples Variables")
    st.caption(
        "Util para comparar distribuciones de variables como notas por materia "
        "o puntuaciones de servicio al cliente de forma simultanea."
    )

    cols_comp = st.multiselect(
        "Variables a comparar:",
        options=num_cols,
        default=num_cols[:min(6, len(num_cols))],
        key="comp_vars",
    )
    factor_comp = st.radio(
        "Factor IQR para comparacion:",
        options=[1.5, 3.0],
        format_func=lambda x: f"{x}",
        key="comp_factor",
        horizontal=True,
    )

    if len(cols_comp) >= 2:
        fig_comp = atipicos.boxplot_comparativo(df, cols_comp, factor_comp)
        st.plotly_chart(fig_comp, use_container_width=True)
    else:
        st.info("Selecciona al menos 2 variables para el boxplot comparativo.")
