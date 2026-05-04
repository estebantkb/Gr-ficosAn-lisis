"""
charts/estandarizacion.py
Graficos para la seccion 'Centrar y Reducir' (estandarizacion Z-score).

La transformacion Z-score centra la variable en 0 (media = 0) y la reduce
a desviacion estandar = 1 aplicando la formula:
    z_i = (x_i - mu) / sigma

Esto permite comparar variables medidas en escalas distintas, eliminar el
efecto de la unidad de medida y preparar los datos para metodos que asumen
variables estandarizadas (PCA, clustering, regresion regularizada, etc.).
"""
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from config import PALETTE, COLOR_SEQUENCE, PLOTLY_TEMPLATE, MARGIN


# ---------------------------------------------------------------------------
# Tabla Z-score detallada
# ---------------------------------------------------------------------------

def tabla_z_scores(df, columna):
    """Genera un DataFrame con la transformacion Z-score paso a paso.

    Columnas:
      xi        : valor original
      xi - mu   : desviacion respecto a la media
      zi        : valor estandarizado  (xi - mu) / sigma
    """
    serie = df[columna].dropna().astype(float).reset_index(drop=True)
    mu    = float(serie.mean())
    sigma = float(serie.std(ddof=1))

    result = pd.DataFrame({
        "xi":       serie.round(4),
        "xi - mu":  (serie - mu).round(4),
        "zi = (xi-mu)/sigma": ((serie - mu) / sigma if sigma > 0 else serie * 0).round(4),
    })
    result.index = result.index + 1
    result.index.name = "Obs."
    return result, mu, sigma


# ---------------------------------------------------------------------------
# Histograma antes / despues de estandarizar
# ---------------------------------------------------------------------------

def histograma_antes_despues(df, columna):
    """Dos histogramas con KDE superpuesta: variable original vs Z-score.

    Demuestra visualmente que la forma de la distribucion NO cambia,
    solo cambian la escala y la posicion del eje X.
    """
    serie = df[columna].dropna().astype(float)
    mu    = float(serie.mean())
    sigma = float(serie.std(ddof=1)) if float(serie.std(ddof=1)) > 0 else 1.0
    z     = (serie - mu) / sigma

    def kde_manual(datos, x_r):
        n = len(datos)
        h = max(1.06 * datos.std() * n ** (-0.2), 1e-6)
        y = np.zeros(len(x_r))
        for xi in datos:
            u = (x_r - xi) / h
            y += np.exp(-0.5 * u**2) / np.sqrt(2 * np.pi)
        return y / (n * h)

    fig = go.Figure()

    # --- Original ---
    x_orig = np.linspace(float(serie.min()), float(serie.max()), 300)
    y_kde_orig = kde_manual(serie.values, x_orig)

    fig.add_trace(go.Histogram(
        x=serie, histnorm="probability density",
        name="Original", opacity=0.55,
        marker_color=PALETTE["secondary"],
        legendgroup="orig",
    ))
    fig.add_trace(go.Scatter(
        x=x_orig, y=y_kde_orig, mode="lines",
        name="KDE Original",
        line=dict(color=PALETTE["primary"], width=2.5),
        legendgroup="orig",
    ))

    # --- Estandarizado ---
    x_z = np.linspace(float(z.min()), float(z.max()), 300)
    y_kde_z = kde_manual(z.values, x_z)

    fig.add_trace(go.Histogram(
        x=z, histnorm="probability density",
        name="Estandarizado (Z)", opacity=0.55,
        marker_color=PALETTE["accent"],
        legendgroup="zsc",
    ))
    fig.add_trace(go.Scatter(
        x=x_z, y=y_kde_z, mode="lines",
        name="KDE Z-score",
        line=dict(color=PALETTE["danger"], width=2.5, dash="dash"),
        legendgroup="zsc",
    ))

    # Media Z siempre en 0
    fig.add_vline(x=0, line_dash="dot", line_color=PALETTE["success"],
                  annotation_text="Media Z = 0", annotation_position="top right")

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title=f"Distribucion Original vs Estandarizada - {columna}",
        xaxis_title="Valor",
        yaxis_title="Densidad",
        barmode="overlay",
        legend=dict(orientation="h", y=1.08),
        margin=MARGIN,
    )
    return fig


# ---------------------------------------------------------------------------
# Boxplot de variables estandarizadas (comparacion en escala Z)
# ---------------------------------------------------------------------------

def boxplot_estandarizado(df, columnas):
    """Boxplot de todas las columnas seleccionadas transformadas a Z-score.

    Como todas quedan en la misma escala (media=0, sd=1) es posible
    compararlas directamente en un solo grafico.
    """
    fig = go.Figure()
    colores = COLOR_SEQUENCE * (len(columnas) // len(COLOR_SEQUENCE) + 1)

    for i, col in enumerate(columnas):
        serie = df[col].dropna().astype(float)
        if len(serie) < 2:
            continue
        mu    = float(serie.mean())
        sigma = float(serie.std(ddof=1)) if float(serie.std(ddof=1)) > 0 else 1.0
        z     = (serie - mu) / sigma

        fig.add_trace(go.Box(
            y=z, name=col,
            boxmean="sd",
            boxpoints="outliers",
            marker=dict(color=PALETTE["danger"], size=7, opacity=0.8,
                        line=dict(width=1, color="darkred")),
            line=dict(color=colores[i], width=2),
            fillcolor="rgba(46,134,193,0.12)",
        ))

    # Lineas de referencia: media=0 y ±1 sd
    for yval, etq, dash in [(0, "Media=0", "dot"), (1, "+1σ", "dash"), (-1, "−1σ", "dash")]:
        fig.add_hline(y=yval, line_dash=dash,
                      line_color=PALETTE["muted"], line_width=1.2,
                      annotation_text=etq, annotation_position="right",
                      annotation_font=dict(size=9))

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title="Boxplot de Variables Estandarizadas (Z-score)",
        yaxis_title="Valor Z  (media=0, σ=1)",
        xaxis_title="Variable",
        height=460,
        margin=MARGIN,
    )
    return fig


# ---------------------------------------------------------------------------
# Scatter original vs Z-score (visualiza la transformacion lineal)
# ---------------------------------------------------------------------------

def scatter_transformacion(df, columna):
    """Grafico de dispersion xi vs zi que muestra la relacion lineal
    de la transformacion Z-score.  La pendiente es 1/sigma."""
    serie = df[columna].dropna().astype(float).reset_index(drop=True)
    mu    = float(serie.mean())
    sigma = float(serie.std(ddof=1)) if float(serie.std(ddof=1)) > 0 else 1.0
    z     = (serie - mu) / sigma

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=serie, y=z, mode="markers",
        marker=dict(color=PALETTE["secondary"], size=9, opacity=0.8,
                    line=dict(width=1, color=PALETTE["primary"])),
        name="Observaciones",
        hovertemplate="xi=%{x:.3f}  zi=%{y:.3f}<extra></extra>",
    ))

    # Recta teorica
    x_line = np.linspace(float(serie.min()), float(serie.max()), 100)
    y_line = (x_line - mu) / sigma
    fig.add_trace(go.Scatter(
        x=x_line, y=y_line, mode="lines",
        line=dict(color=PALETTE["danger"], width=2, dash="dash"),
        name=f"z = (x - {mu:.2f}) / {sigma:.2f}",
    ))

    fig.add_hline(y=0, line_dash="dot", line_color="lightgray")
    fig.add_vline(x=mu, line_dash="dot", line_color="lightgray",
                  annotation_text=f"μ={mu:.2f}", annotation_position="top")

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title=f"Transformacion Lineal Z-score - {columna}",
        xaxis_title=f"Valor original ({columna})",
        yaxis_title="Valor estandarizado (z)",
        margin=MARGIN,
    )
    return fig
