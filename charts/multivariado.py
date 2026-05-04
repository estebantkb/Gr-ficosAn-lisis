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


def circulo_correlaciones(df, columnas):
    """Circulo de correlaciones (biplot simplificado).

    Cada variable se muestra como un vector en el plano de los dos primeros
    componentes principales calculados a partir de la matriz de correlacion.
    El angulo entre dos vectores aproxima la correlacion entre esas variables:
      - angulo ~0 grados  -> correlacion positiva fuerte
      - angulo ~90 grados -> sin correlacion
      - angulo ~180 grados -> correlacion negativa fuerte
    """
    datos = df[columnas].dropna().astype(float)
    if len(datos) < 3 or len(columnas) < 2:
        fig = go.Figure()
        fig.add_annotation(text="Se necesitan al menos 2 variables y 3 filas",
                           xref="paper", yref="paper", x=0.5, y=0.5,
                           showarrow=False, font=dict(size=14))
        return fig

    # Estandarizar y calcular matriz de correlacion
    Z = (datos - datos.mean()) / (datos.std() + 1e-9)
    R = np.corrcoef(Z.T)  # shape: (p, p)

    # Descomposicion espectral de R
    valores, vectores = np.linalg.eigh(R)
    # Ordenar descendente
    idx = np.argsort(valores)[::-1]
    valores  = valores[idx]
    vectores = vectores[:, idx]

    # Cargas: coordenadas de cada variable en el espacio de los 2 primeros CP
    cargas = vectores[:, :2] * np.sqrt(np.maximum(valores[:2], 0))

    varianza_total = np.sum(np.maximum(valores, 0))
    pct1 = round(valores[0] / varianza_total * 100, 1) if varianza_total > 0 else 0
    pct2 = round(valores[1] / varianza_total * 100, 1) if varianza_total > 0 else 0

    fig = go.Figure()

    # Circulo unitario de referencia
    theta = np.linspace(0, 2 * np.pi, 200)
    fig.add_trace(go.Scatter(
        x=np.cos(theta), y=np.sin(theta), mode="lines",
        line=dict(color="lightgray", width=1, dash="dot"),
        showlegend=False, hoverinfo="skip",
    ))

    # Flechas de cada variable
    colores_var = COLOR_SEQUENCE * (len(columnas) // len(COLOR_SEQUENCE) + 1)
    for i, var in enumerate(columnas):
        x_end, y_end = float(cargas[i, 0]), float(cargas[i, 1])
        corr_cp1 = round(x_end, 3)
        corr_cp2 = round(y_end, 3)

        # Linea de flecha
        fig.add_trace(go.Scatter(
            x=[0, x_end], y=[0, y_end], mode="lines",
            line=dict(color=colores_var[i], width=2.5),
            showlegend=False, hoverinfo="skip",
        ))
        # Punta y etiqueta
        fig.add_trace(go.Scatter(
            x=[x_end], y=[y_end], mode="markers+text",
            marker=dict(color=colores_var[i], size=10,
                        symbol="arrow", angleref="previous"),
            text=[var],
            textposition="top center" if y_end >= 0 else "bottom center",
            textfont=dict(size=11, color=colores_var[i]),
            name=var,
            hovertemplate=(f"<b>{var}</b><br>CP1: {corr_cp1}<br>CP2: {corr_cp2}"
                           "<extra></extra>"),
        ))

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title=f"Circulo de Correlaciones  (CP1={pct1}%  CP2={pct2}%)",
        xaxis=dict(
            title=f"Componente 1 ({pct1}%)",
            range=[-1.25, 1.25], zeroline=True,
            zerolinecolor="lightgray", scaleanchor="y",
        ),
        yaxis=dict(
            title=f"Componente 2 ({pct2}%)",
            range=[-1.25, 1.25], zeroline=True,
            zerolinecolor="lightgray",
        ),
        margin=MARGIN, height=480,
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
