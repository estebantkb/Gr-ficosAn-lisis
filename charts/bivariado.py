import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from config import PALETTE, COLOR_SEQUENCE, PLOTLY_TEMPLATE, MARGIN


def scatter_regresion(df, col_x, col_y, col_color=None):
    """Dispersion con linea de regresion calculada con numpy (sin statsmodels)."""
    cols = [col_x, col_y] + ([col_color] if col_color else [])
    datos = df[cols].dropna()

    # Puntos base
    marker_kwargs = dict(size=9, opacity=0.8)
    if col_color:
        fig = px.scatter(
            datos, x=col_x, y=col_y, color=col_color,
            color_discrete_sequence=COLOR_SEQUENCE,
            title=f"Dispersion con Regresion: {col_x} vs {col_y}",
        )
    else:
        fig = px.scatter(
            datos, x=col_x, y=col_y,
            color_discrete_sequence=[PALETTE["primary"]],
            title=f"Dispersion con Regresion: {col_x} vs {col_y}",
        )

    # Linea de regresion manual
    d = datos[[col_x, col_y]].dropna()
    if len(d) >= 2:
        m, b = np.polyfit(d[col_x], d[col_y], 1)
        r    = np.corrcoef(d[col_x], d[col_y])[0, 1]
        x_rng = np.linspace(d[col_x].min(), d[col_x].max(), 200)
        fig.add_trace(go.Scatter(
            x=x_rng, y=m * x_rng + b,
            mode="lines", name="Regresion OLS",
            line=dict(color=PALETTE["danger"], width=2.5, dash="dash"),
        ))
        fig.add_annotation(
            x=0.04, y=0.95, xref="paper", yref="paper", showarrow=False,
            text=f"y = {m:.3f}x + {b:.3f}   |   R = {r:.3f}   |   R2 = {r**2:.3f}",
            bgcolor="rgba(255,255,255,0.88)", bordercolor=PALETTE["primary"],
            borderwidth=1, font=dict(size=11, color=PALETTE["text"]),
        )

    fig.update_layout(template=PLOTLY_TEMPLATE, margin=MARGIN)
    return fig


def scatter_elipse(df, col_x, col_y):
    """Dispersion con elipse de confianza al 95% (requiere scipy)."""
    datos = df[[col_x, col_y]].dropna()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=datos[col_x], y=datos[col_y], mode="markers", name="Datos",
        marker=dict(color=PALETTE["secondary"], size=9, opacity=0.75,
                    line=dict(width=1, color=PALETTE["primary"])),
    ))

    try:
        from scipy.stats import chi2
        cov = np.cov(datos[col_x], datos[col_y])
        mu = datos[[col_x, col_y]].mean().values
        eigvals, eigvecs = np.linalg.eigh(cov)
        angle = np.linspace(0, 2 * np.pi, 300)
        chi2_val = chi2.ppf(0.95, df=2)
        ellipse = np.array([
            np.sqrt(chi2_val * eigvals[0]) * np.cos(angle),
            np.sqrt(chi2_val * eigvals[1]) * np.sin(angle),
        ])
        rot = eigvecs @ ellipse
        fig.add_trace(go.Scatter(
            x=rot[0] + mu[0], y=rot[1] + mu[1],
            mode="lines", name="Elipse 95%",
            line=dict(color=PALETTE["danger"], width=2, dash="dash"),
        ))
    except ImportError:
        pass

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title=f"Dispersion con Elipse de Confianza 95% - {col_x} vs {col_y}",
        xaxis_title=col_x, yaxis_title=col_y, margin=MARGIN,
    )
    return fig


def bubble_chart(df, col_x, col_y, col_size, col_color=None):
    """Bubble chart con tres variables numericas."""
    cols = [col_x, col_y, col_size] + ([col_color] if col_color else [])
    datos = df[cols].dropna()

    kwargs = dict(x=col_x, y=col_y, size=col_size, opacity=0.72,
                  size_max=55, title=f"Bubble: {col_x} vs {col_y} (tam: {col_size})")
    if col_color:
        kwargs["color"] = col_color
        kwargs["color_discrete_sequence"] = COLOR_SEQUENCE
    else:
        kwargs["color_discrete_sequence"] = [PALETTE["secondary"]]

    fig = px.scatter(datos, **kwargs)
    fig.update_layout(template=PLOTLY_TEMPLATE, margin=MARGIN)
    return fig


def pairs_plot(df, columnas):
    """Matriz de diagramas de dispersion (SPLOM)."""
    datos = df[columnas].dropna()
    dims = [dict(label=c, values=datos[c]) for c in columnas]

    fig = go.Figure(go.Splom(
        dimensions=dims, showupperhalf=False,
        diagonal_visible=True,
        marker=dict(color=PALETTE["secondary"], size=5, opacity=0.7,
                    line=dict(width=0.5, color=PALETTE["primary"])),
    ))
    fig.update_layout(
        template=PLOTLY_TEMPLATE, title="Matriz de Dispersion (Pairs Plot)",
        margin=MARGIN, height=600,
    )
    return fig
