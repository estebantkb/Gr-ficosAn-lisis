"""Tab 1 - Exploracion de datos: tabla maestra, tipos de columnas y estadisticos."""
import streamlit as st
from data_loader import resumen_estadistico, cols_numericas, cols_categoricas


def render(df):
    st.subheader("Tabla de Datos")
    st.dataframe(df, use_container_width=True, height=380)

    st.divider()

    col_tipos, col_stats = st.columns([1, 2])

    with col_tipos:
        st.subheader("Tipos de Variables")
        nums = cols_numericas(df)
        cats = cols_categoricas(df)
        st.markdown(f"**Numericas ({len(nums)}):**")
        for c in nums:
            st.markdown(f"- {c}")
        if cats:
            st.markdown(f"**Categoricas ({len(cats)}):**")
            for c in cats:
                st.markdown(f"- {c}")

    with col_stats:
        st.subheader("Estadisticos Descriptivos Completos")
        resumen = resumen_estadistico(df)
        if resumen is not None:
            st.dataframe(
                resumen.style.format(
                    {c: "{:.4f}" for c in resumen.columns if resumen[c].dtype == "float64"},
                    na_rep="-",
                ),
                use_container_width=True,
                height=340,
            )
        else:
            st.info("No hay variables numericas para calcular estadisticos.")
