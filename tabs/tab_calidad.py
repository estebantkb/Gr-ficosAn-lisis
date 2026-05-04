"""Tab 2 - Calidad y limpieza de datos: nulos, duplicados e imputacion."""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from config import PALETTE, COLOR_SEQUENCE, PLOTLY_TEMPLATE, MARGIN


def _fig_nulos(df):
    nulos = df.isnull().sum()
    nulos = nulos[nulos > 0]
    pct   = (nulos / len(df) * 100).round(2)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=nulos.index.tolist(), y=nulos.values,
        name="Absolutos", marker_color=PALETTE["danger"], opacity=0.85,
        text=nulos.values, textposition="outside",
    ))
    fig.add_trace(go.Scatter(
        x=pct.index.tolist(), y=pct.values,
        name="Porcentaje (%)", yaxis="y2", mode="lines+markers",
        line=dict(color=PALETTE["accent"], width=2.5),
        marker=dict(size=8),
    ))
    fig.update_layout(
        template=PLOTLY_TEMPLATE, title="Valores Ausentes por Variable",
        xaxis_title="Variable", yaxis_title="Cantidad de Nulos",
        yaxis2=dict(title="% de Nulos", overlaying="y", side="right", showgrid=False),
        legend=dict(orientation="h", y=1.05), margin=MARGIN,
    )
    return fig


def _heatmap_nulos(df):
    """Heatmap estilo missingno: 1=presente, 0=ausente."""
    binario = df.isnull().astype(int)
    fig = go.Figure(go.Heatmap(
        z=binario.values,
        x=df.columns.tolist(),
        y=[str(i + 1) for i in range(len(df))],
        colorscale=[[0, PALETTE["light"]], [1, PALETTE["danger"]]],
        showscale=False,
        hovertemplate="Fila %{y} | Col %{x}: %{z}<extra></extra>",
    ))
    fig.update_layout(
        template=PLOTLY_TEMPLATE, title="Mapa de Valores Ausentes (rojo=ausente)",
        xaxis_title="Variable", yaxis_title="Registro",
        margin=MARGIN, height=max(300, len(df) * 18 + 80),
    )
    return fig


def render(df_key="df"):
    """Renderiza el tab de calidad. Usa st.session_state[df_key]."""
    df = st.session_state[df_key]

    # --- NULOS ---
    st.subheader("Diagnostico de Datos Ausentes")
    total_nulos = df.isnull().sum().sum()

    if total_nulos > 0:
        c_izq, c_der = st.columns([1, 1])
        with c_izq:
            st.plotly_chart(_fig_nulos(df), use_container_width=True)
        with c_der:
            st.plotly_chart(_heatmap_nulos(df), use_container_width=True)

        st.divider()
        st.subheader("Acciones de Limpieza")
        btn1, btn2 = st.columns(2)

        if btn1.button("Eliminar filas con nulos", use_container_width=True):
            st.session_state[df_key] = df.dropna().reset_index(drop=True)
            st.success("Filas con nulos eliminadas correctamente.")
            st.rerun()

        if btn2.button("Imputar (Media / Moda)", use_container_width=True):
            df_imp = df.copy()
            for col in df_imp.columns:
                if df_imp[col].isnull().sum() == 0:
                    continue
                if pd.api.types.is_numeric_dtype(df_imp[col]):
                    df_imp[col].fillna(df_imp[col].mean(), inplace=True)
                else:
                    moda = df_imp[col].mode()
                    if not moda.empty:
                        df_imp[col].fillna(moda.iloc[0], inplace=True)
            st.session_state[df_key] = df_imp
            st.success("Imputacion estadistica completada.")
            st.rerun()
    else:
        st.success("El dataset no contiene valores ausentes.")

    # --- DUPLICADOS ---
    st.divider()
    st.subheader("Registros Duplicados")
    n_dup = df.duplicated().sum()
    if n_dup > 0:
        st.warning(f"Se detectaron {n_dup} filas duplicadas.")
        if st.button("Eliminar duplicados", use_container_width=False):
            st.session_state[df_key] = df.drop_duplicates().reset_index(drop=True)
            st.success("Duplicados eliminados.")
            st.rerun()
        st.dataframe(df[df.duplicated(keep=False)], use_container_width=True)
    else:
        st.success("No se detectaron registros duplicados.")
