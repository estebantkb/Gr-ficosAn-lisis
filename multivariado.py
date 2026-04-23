import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from config import PALETTE, COLOR_SEQUENCE, PLOTLY_TEMPLATE, MARGIN


def heatmap_correlacion(df, columnas):
    """Heatmap de la matriz de correlacion de Pearson con valores anotados."""
    datos = df[columnas].dropna()
    corr = datos.corr().round(3)

    fig = go.Figure(go.Heatmap(
        z=corr.values,
        x=corr.columns.tolist(),
        y=corr.index.tolist(),
        colorscale=[[0, PALETTE["danger"]], [0.5, "#FFFFFF"], [1, PALETTE["primary"]]],
        zmid=0, zmin=-1, zmax=1,
        text=corr.values.round(2),
        texttemplate="%{text}",
        textfont=dict(size=11, color=PALETTE["text"]),
        colorbar=dict(title="r Pearson"),
    ))
    fig.update_layout(
        template=PLOTLY_TEMPLATE, title="Matriz de Correlacion de Pearson",
        margin=MARGIN, height=max(380, len(columnas) * 55),
    )
    return fig, corr


def coordenadas_paralelas(df, columnas, col_color=None):
    """Coordenadas paralelas para visualizar patrones multivariados."""
    cols = columnas + ([col_color] if col_color and col_color not in columnas else [])
    datos = df[cols].dropna()

    dims = [
        dict(range=[datos[c].min(), datos[c].max()], label=c, values=datos[c])
        for c in columnas
    ]

    if col_color and col_color in datos.columns:
        try:
            line = dict(color=datos[col_color],
                        colorscale="Blues", showscale=True,
                        colorbar=dict(title=col_color))
        except Exception:
            line = dict(color=PALETTE["secondary"])
    else:
        line = dict(color=PALETTE["secondary"])

    fig = go.Figure(go.Parcoords(dimensions=dims, line=line))
    fig.update_layout(
        template=PLOTLY_TEMPLATE, title="Coordenadas Paralelas",
        margin=dict(l=90, r=90, t=60, b=30), height=460,
    )
    return fig


def radar(df, columnas, fila_idx=None):
    """Radar (spider) chart. Muestra perfil de una fila o el promedio general."""
    datos = df[columnas].dropna().reset_index(drop=True)
    cats = columnas + [columnas[0]]  # cerrar el poligono

    fig = go.Figure()
    if fila_idx is not None and fila_idx < len(datos):
        vals = datos.iloc[fila_idx].tolist()
        fig.add_trace(go.Scatterpolar(
            r=vals + [vals[0]], theta=cats, fill="toself",
            name=f"Registro {fila_idx + 1}",
            line=dict(color=PALETTE["primary"]),
            fillcolor="rgba(27,79,138,0.18)",
        ))
    else:
        medias = datos.mean().tolist()
        fig.add_trace(go.Scatterpolar(
            r=medias + [medias[0]], theta=cats, fill="toself",
            name="Promedio general",
            line=dict(color=PALETTE["primary"]),
            fillcolor="rgba(27,79,138,0.18)",
        ))

    fig.update_layout(
        template=PLOTLY_TEMPLATE, title="Grafico de Radar (Spider Chart)",
        polar=dict(radialaxis=dict(visible=True, color=PALETTE["muted"])),
        margin=MARGIN,
    )
    return fig


def heatmap_datos(df, columnas):
    """Heatmap de todos los registros normalizado entre 0 y 1."""
    datos = df[columnas].dropna().reset_index(drop=True)
    normalizado = (datos - datos.min()) / (datos.max() - datos.min() + 1e-9)

    fig = go.Figure(go.Heatmap(
        z=normalizado.values,
        x=columnas,
        y=[str(i + 1) for i in range(len(normalizado))],
        colorscale=[[0, PALETTE["light"]], [0.5, PALETTE["secondary"]], [1, PALETTE["primary"]]],
        text=datos.values.round(2),
        texttemplate="%{text}",
        textfont=dict(size=9),
        colorbar=dict(title="Valor norm."),
    ))
    fig.update_layout(
        template=PLOTLY_TEMPLATE, title="Mapa de Calor de los Datos (Normalizado)",
        xaxis_title="Variable", yaxis_title="Registro",
        margin=MARGIN, height=max(350, len(datos) * 22 + 100),
    )
    return fig
