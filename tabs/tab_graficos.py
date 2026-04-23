"""Tab 3 - Analisis Visual: graficos estadisticos univariados, bivariados y multivariados."""
import streamlit as st
from data_loader import cols_numericas, cols_categoricas
from charts import univariado, bivariado, categorico, multivariado


ANALISIS_NUM = [
    "Histograma + Densidad",
    "Diagrama de Caja (Boxplot)",
    "Violin",
    "Curva de Densidad KDE",
    "Q-Q Plot (Normalidad)",
    "Tallo y Hoja",
]
ANALISIS_BIV = [
    "Dispersion con Regresion",
    "Dispersion con Elipse 95%",
    "Bubble Chart",
    "Pairs Plot (Matriz de Dispersion)",
]
ANALISIS_CAT = [
    "Barras de Frecuencias",
    "Grafico de Dona",
    "Treemap",
    "Tabla de Frecuencias",
]
ANALISIS_MULTI = [
    "Heatmap de Correlacion",
    "Coordenadas Paralelas",
    "Grafico de Radar",
    "Heatmap de Datos",
]


def render(df):
    nums = cols_numericas(df)
    cats = cols_categoricas(df)

    st.subheader("Generador de Graficos Estadisticos")

    tipo_grupo = st.radio(
        "Categoria de Analisis:",
        ["Univariado Numerico", "Bivariado / Correlacion",
         "Variable Categorica", "Multivariado"],
        horizontal=True,
    )
    st.divider()

    # ---------- UNIVARIADO NUMERICO ----------
    if tipo_grupo == "Univariado Numerico":
        if not nums:
            st.warning("El dataset no contiene variables numericas.")
            return

        c_ctrl, c_graf = st.columns([1, 3])
        with c_ctrl:
            analisis = st.selectbox("Tipo de grafico:", ANALISIS_NUM)
            var_x = st.selectbox("Variable:", nums)
            cats_disp = cats if cats else None
            col_grupo = None
            if analisis == "Violin" and cats_disp:
                col_grupo = st.selectbox("Agrupar por (opcional):", ["(ninguna)"] + cats_disp)
                col_grupo = None if col_grupo == "(ninguna)" else col_grupo

        with c_graf:
            if analisis == "Histograma + Densidad":
                st.plotly_chart(univariado.histograma_kde(df, var_x), use_container_width=True)

            elif analisis == "Diagrama de Caja (Boxplot)":
                st.plotly_chart(univariado.boxplot(df, var_x), use_container_width=True)

            elif analisis == "Violin":
                st.plotly_chart(univariado.violin(df, var_x, col_grupo), use_container_width=True)

            elif analisis == "Curva de Densidad KDE":
                st.plotly_chart(univariado.densidad(df, var_x), use_container_width=True)

            elif analisis == "Q-Q Plot (Normalidad)":
                st.plotly_chart(univariado.qq_plot(df, var_x), use_container_width=True)

            elif analisis == "Tallo y Hoja":
                st.markdown(f"**Diagrama de Tallo y Hoja - {var_x}**")
                st.code(univariado.tallo_hoja(df, var_x), language="")

    # ---------- BIVARIADO ----------
    elif tipo_grupo == "Bivariado / Correlacion":
        if len(nums) < 2:
            st.warning("Se necesitan al menos 2 variables numericas para analisis bivariado.")
            return

        c_ctrl, c_graf = st.columns([1, 3])
        with c_ctrl:
            analisis = st.selectbox("Tipo de grafico:", ANALISIS_BIV)
            var_x = st.selectbox("Variable X:", nums, index=0)
            var_y = st.selectbox("Variable Y:", nums, index=min(1, len(nums) - 1))
            col_color = col_size = None

            if analisis == "Dispersion con Regresion" and cats:
                col_color = st.selectbox("Color por (opcional):", ["(ninguna)"] + cats)
                col_color = None if col_color == "(ninguna)" else col_color

            if analisis == "Bubble Chart":
                var_size_opts = [n for n in nums if n not in [var_x, var_y]]
                if var_size_opts:
                    col_size = st.selectbox("Tamano (variable):", var_size_opts)
                else:
                    st.info("Se necesita una tercera variable numerica para el tamano.")

            if analisis == "Pairs Plot (Matriz de Dispersion)":
                sel = st.multiselect("Variables a incluir:", nums, default=nums[:min(5, len(nums))])

        with c_graf:
            if analisis == "Dispersion con Regresion":
                st.plotly_chart(bivariado.scatter_regresion(df, var_x, var_y, col_color), use_container_width=True)

            elif analisis == "Dispersion con Elipse 95%":
                st.plotly_chart(bivariado.scatter_elipse(df, var_x, var_y), use_container_width=True)

            elif analisis == "Bubble Chart":
                if col_size:
                    st.plotly_chart(bivariado.bubble_chart(df, var_x, var_y, col_size), use_container_width=True)
                else:
                    st.info("Selecciona una variable de tamano en el panel izquierdo.")

            elif analisis == "Pairs Plot (Matriz de Dispersion)":
                if len(sel) >= 2:
                    st.plotly_chart(bivariado.pairs_plot(df, sel), use_container_width=True)
                else:
                    st.info("Selecciona al menos 2 variables.")

    # ---------- CATEGORICO ----------
    elif tipo_grupo == "Variable Categorica":
        if not cats:
            st.warning("El dataset no contiene variables categoricas.")
            return

        c_ctrl, c_graf = st.columns([1, 3])
        with c_ctrl:
            analisis = st.selectbox("Tipo de grafico:", ANALISIS_CAT)
            var_cat = st.selectbox("Variable categorica:", cats)

        with c_graf:
            if analisis == "Barras de Frecuencias":
                st.plotly_chart(categorico.barras_frecuencia(df, var_cat), use_container_width=True)

            elif analisis == "Grafico de Dona":
                st.plotly_chart(categorico.pie_dona(df, var_cat), use_container_width=True)

            elif analisis == "Treemap":
                st.plotly_chart(categorico.treemap_frecuencias(df, var_cat), use_container_width=True)

            elif analisis == "Tabla de Frecuencias":
                tabla = categorico.tabla_frecuencias(df, var_cat)
                st.markdown(f"**Tabla de Frecuencias - {var_cat}**")
                st.dataframe(tabla, use_container_width=True, hide_index=True)

    # ---------- MULTIVARIADO ----------
    elif tipo_grupo == "Multivariado":
        if len(nums) < 2:
            st.warning("Se necesitan al menos 2 variables numericas para analisis multivariado.")
            return

        c_ctrl, c_graf = st.columns([1, 3])
        with c_ctrl:
            analisis = st.selectbox("Tipo de grafico:", ANALISIS_MULTI)
            vars_sel = st.multiselect(
                "Variables a incluir:", nums,
                default=nums[:min(6, len(nums))],
            )
            col_color_par = None
            fila_radar = None

            if analisis == "Coordenadas Paralelas" and cats:
                col_color_par = st.selectbox("Color por variable numerica (opcional):", ["(ninguna)"] + nums)
                col_color_par = None if col_color_par == "(ninguna)" else col_color_par

            if analisis == "Grafico de Radar":
                n_filas = len(df.dropna(subset=vars_sel if vars_sel else nums))
                opcion = st.radio("Mostrar:", ["Promedio general", "Registro especifico"])
                if opcion == "Registro especifico":
                    fila_radar = st.number_input("Numero de registro (1-based):", min_value=1,
                                                  max_value=max(1, n_filas), value=1) - 1

        with c_graf:
            if not vars_sel:
                st.info("Selecciona al menos 2 variables en el panel izquierdo.")
            elif analisis == "Heatmap de Correlacion":
                if len(vars_sel) >= 2:
                    fig_corr, corr_df = multivariado.heatmap_correlacion(df, vars_sel)
                    st.plotly_chart(fig_corr, use_container_width=True)
                    with st.expander("Ver tabla de correlaciones"):
                        st.dataframe(corr_df.style.format("{:.3f}"), use_container_width=True)

            elif analisis == "Coordenadas Paralelas":
                if len(vars_sel) >= 2:
                    st.plotly_chart(
                        multivariado.coordenadas_paralelas(df, vars_sel, col_color_par),
                        use_container_width=True,
                    )

            elif analisis == "Grafico de Radar":
                if len(vars_sel) >= 3:
                    st.plotly_chart(
                        multivariado.radar(df, vars_sel, fila_radar),
                        use_container_width=True,
                    )
                else:
                    st.info("Selecciona al menos 3 variables para el radar.")

            elif analisis == "Heatmap de Datos":
                if len(vars_sel) >= 1:
                    st.plotly_chart(multivariado.heatmap_datos(df, vars_sel), use_container_width=True)
