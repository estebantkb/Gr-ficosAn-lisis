"""
tabs/tab_estandarizacion.py
Tab 5 - Centrar y Reducir (Estandarizacion Z-score).

Cubre las diapositivas del ingeniero 62-66:
  Diapo 62 : Concepto de centrar y reducir
  Diapo 63 : Formula Z-score paso a paso
  Diapo 64 : Tabla de transformacion xi -> zi
  Diapo 65 : Distribucion antes y despues
  Diapo 66 : Comparacion de variables estandarizadas
"""
import streamlit as st
from data_loader import cols_numericas
from charts import estandarizacion


def render(df):
    st.subheader("Centrar y Reducir — Estandarizacion Z-score")

    num_cols = cols_numericas(df)
    if len(num_cols) == 0:
        st.warning("No hay variables numericas en el dataset.")
        return

    # -----------------------------------------------------------------------
    # TEORIA (diapos 62-63)
    # -----------------------------------------------------------------------
    with st.expander("¿Que significa Centrar y Reducir?", expanded=True):
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(
                r"""
                ### Formula Z-score

                $$z_i = \frac{x_i - \mu}{\sigma}$$

                | Termino | Significado |
                |---|---|
                | $x_i$ | Valor original de la observacion $i$ |
                | $\mu$ | Media de la variable |
                | $\sigma$ | Desviacion estandar de la variable |
                | $z_i$ | Valor estandarizado (sin unidades) |

                **Centrar**: restar la media → la nueva media es **0**

                **Reducir**: dividir por σ → la nueva desviacion estandar es **1**
                """
            )
        with col_b:
            st.markdown(
                """
                ### ¿Para que sirve?

                - **Comparar variables** con distintas escalas o unidades
                  (ej.: notas 0-10 vs edades 15-60 vs ingresos en dolares).
                - **Eliminar el efecto de la magnitud** en metodos estadisticos
                  que son sensibles a la escala (correlacion, PCA, clustering).
                - **Identificar observaciones extremas** de forma estandarizada:
                  un `|z| > 2` es sospechoso y `|z| > 3` suele considerarse atipico.
                - **Interpretar posicion relativa**: un zi = 1.5 significa que esa
                  observacion esta 1.5 desviaciones estandar por encima de la media.
                """
            )

    # -----------------------------------------------------------------------
    # SELECTOR DE VARIABLE (diapo 64: tabla Z)
    # -----------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### Tabla de Transformacion Z-score por Variable")

    col_sel = st.selectbox(
        "Variable a estandarizar:",
        options=num_cols,
        key="est_col",
    )

    df_z, mu, sigma = estandarizacion.tabla_z_scores(df, col_sel)

    m1, m2, m3 = st.columns(3)
    m1.metric("Media (μ)",           f"{mu:.4f}")
    m2.metric("Desv. Estandar (σ)",  f"{sigma:.4f}")
    m3.metric("Observaciones",       len(df_z))

    def _color_z(val):
        """Colorea la celda segun el valor Z: rojo si negativo extremo,
        verde si positivo extremo, blanco cerca de 0. Sin matplotlib."""
        try:
            v = float(val)
        except (TypeError, ValueError):
            return ""
        v = max(-3.0, min(3.0, v))   # limitar a [-3, 3]
        if v >= 0:
            # blanco -> verde
            ratio = v / 3.0
            r = int(255 - ratio * (255 - 39))
            g = int(255 - ratio * (255 - 174))
            b = int(255 - ratio * (255 - 96))
        else:
            # rojo -> blanco
            ratio = (-v) / 3.0
            r = int(255 - ratio * (255 - 220))
            g = int(255 - ratio * 255)
            b = int(255 - ratio * 255)
        return f"background-color: rgb({r},{g},{b}); color: #111"

    col_z = "zi = (xi-mu)/sigma"
    # pandas >= 2.1 renombro applymap -> map
    styler = df_z.style.format(precision=4)
    try:
        styler = styler.map(_color_z, subset=[col_z])
    except AttributeError:
        styler = styler.applymap(_color_z, subset=[col_z])
    st.dataframe(styler, use_container_width=True)

    # Resaltar valores |z| > 2
    atipicos_z = df_z[df_z[col_z].abs() > 2]
    if len(atipicos_z) > 0:
        st.warning(
            f"**{len(atipicos_z)} observacion(es)** con |z| > 2 "
            f"(potencialmente atipicas): filas {atipicos_z.index.tolist()}"
        )
    else:
        st.success("Ninguna observacion supera |z| > 2.")

    # -----------------------------------------------------------------------
    # DISTRIBUCION ANTES / DESPUES (diapo 65)
    # -----------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### Distribucion Original vs Estandarizada")
    st.caption(
        "La forma de la distribucion es identica antes y despues de estandarizar. "
        "Solo cambia la escala del eje X."
    )

    fig_hist = estandarizacion.histograma_antes_despues(df, col_sel)
    st.plotly_chart(fig_hist, use_container_width=True)

    # Scatter transformacion
    st.markdown("#### Relacion Lineal: xi → zi")
    st.caption("La transformacion Z-score es una funcion lineal de pendiente 1/σ.")
    fig_scat = estandarizacion.scatter_transformacion(df, col_sel)
    st.plotly_chart(fig_scat, use_container_width=True)

    # -----------------------------------------------------------------------
    # BOXPLOT COMPARATIVO ESTANDARIZADO (diapo 66)
    # -----------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### Comparacion de Variables Estandarizadas")
    st.caption(
        "Al llevar todas las variables a escala Z es posible compararlas "
        "directamente en un solo grafico. La linea central (media=0) y las "
        "bandas ±1σ sirven como referencia."
    )

    cols_est = st.multiselect(
        "Variables a comparar (estandarizadas):",
        options=num_cols,
        default=num_cols[:min(6, len(num_cols))],
        key="est_comp_vars",
    )

    if len(cols_est) >= 2:
        fig_box_z = estandarizacion.boxplot_estandarizado(df, cols_est)
        st.plotly_chart(fig_box_z, use_container_width=True)
    else:
        st.info("Selecciona al menos 2 variables.")
