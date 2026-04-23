import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from config import PALETTE, COLOR_SEQUENCE, PLOTLY_TEMPLATE, MARGIN


def _kde_manual(datos, x_r):
    """KDE manual usando regla de Silverman, sin scipy."""
    n = len(datos)
    h = 1.06 * datos.std() * n ** (-1 / 5)
    if h == 0:
        h = 1e-6
    y = np.zeros(len(x_r))
    for xi in datos:
        u = (x_r - xi) / h
        y += np.exp(-0.5 * u ** 2) / (np.sqrt(2 * np.pi))
    return y / (n * h)


def histograma_kde(df, columna):
    """Histograma con curva KDE y curva normal teorica superpuestas."""
    datos = df[columna].dropna().astype(float)
    n = len(datos)
    nbins = min(30, max(5, n // 3))

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=datos, nbinsx=nbins, histnorm="probability density",
        name="Frecuencia", marker_color=PALETTE["secondary"], opacity=0.65,
    ))

    x_r = np.linspace(float(datos.min()), float(datos.max()), 300)

    # KDE (con scipy o manual)
    try:
        from scipy.stats import gaussian_kde
        y_kde = gaussian_kde(datos)(x_r)
    except ImportError:
        y_kde = _kde_manual(datos.values, x_r)

    fig.add_trace(go.Scatter(
        x=x_r, y=y_kde, mode="lines", name="KDE",
        line=dict(color=PALETTE["danger"], width=2.5),
    ))

    # Curva normal teorica
    mu, sigma = float(datos.mean()), float(datos.std())
    if sigma > 0:
        y_norm = (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_r - mu) / sigma) ** 2)
        fig.add_trace(go.Scatter(
            x=x_r, y=y_norm, mode="lines", name="Normal teorica",
            line=dict(color=PALETTE["accent"], width=2, dash="dash"),
        ))

    fig.add_vline(x=mu, line_dash="dot", line_color=PALETTE["primary"],
                  annotation_text=f"Media={mu:.2f}", annotation_position="top right")

    fig.update_layout(
        template=PLOTLY_TEMPLATE, title=f"Histograma con Densidad - {columna}",
        xaxis_title=columna, yaxis_title="Densidad",
        legend=dict(orientation="h", y=1.05), margin=MARGIN,
    )
    return fig


def boxplot(df, columna):
    """Boxplot horizontal. La muesca (notch) solo se activa cuando n >= 30
    para evitar el efecto triangulo/corbata en muestras pequenas."""
    datos = df[columna].dropna().astype(float)
    n = len(datos)

    q1      = float(datos.quantile(0.25))
    q3      = float(datos.quantile(0.75))
    iqr     = q3 - q1
    mediana = float(datos.median())
    vmin    = float(datos.min())
    vmax    = float(datos.max())

    # La formula de la muesca de Plotly es: +/- 1.57 * IQR / sqrt(n)
    # Si la muesca excede los cuartiles -> triangulo. Se desactiva notch en ese caso.
    notch_hw = 1.57 * iqr / np.sqrt(n) if n > 1 else 0
    usar_notch = bool((n >= 30) and (mediana - notch_hw >= q1) and (mediana + notch_hw <= q3))

    fig = go.Figure(go.Box(
        x=datos,
        name=columna,
        boxmean="sd",
        notched=usar_notch,
        boxpoints="outliers",
        marker=dict(
            color=PALETTE["danger"],
            size=7,
            opacity=0.85,
            line=dict(width=1, color=PALETTE["primary"]),
        ),
        line=dict(color=PALETTE["primary"], width=1.8),
        fillcolor=PALETTE["light"],
        opacity=0.9,
    ))

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title=f"Diagrama de Caja y Bigotes - {columna}",
        xaxis_title=columna,
        yaxis_title="",
        yaxis=dict(showticklabels=False),
        margin=MARGIN,
        height=320,
        annotations=[dict(
            x=mediana, y=1.18, xref="x", yref="paper",
            text=(f"Min={vmin:.2f}  Q1={q1:.2f}  Med={mediana:.2f}"
                  f"  Q3={q3:.2f}  Max={vmax:.2f}  IQR={iqr:.2f}"),
            showarrow=False,
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor=PALETTE["primary"], borderwidth=1,
            font=dict(size=10, color=PALETTE["text"]),
        )],
    )
    return fig


def violin(df, columna, col_grupo=None):
    """Violin plot con caja interna y puntos outliers."""
    datos = df.dropna(subset=[columna])

    if col_grupo and col_grupo in df.columns:
        fig = px.violin(
            datos, y=columna, x=col_grupo, color=col_grupo,
            box=True, points="outliers",
            color_discrete_sequence=COLOR_SEQUENCE,
            title=f"Violin - {columna} por {col_grupo}",
        )
    else:
        fig = px.violin(
            datos, y=columna, box=True, points="outliers",
            color_discrete_sequence=[PALETTE["secondary"]],
            title=f"Violin - {columna}",
        )
    fig.update_layout(template=PLOTLY_TEMPLATE, margin=MARGIN)
    return fig


def densidad(df, columna):
    """Curva de densidad KDE pura con areas rellenas y lineas de media/mediana."""
    datos = df[columna].dropna().astype(float)
    x_r   = np.linspace(float(datos.min()), float(datos.max()), 300)

    # KDE con scipy o manual
    try:
        from scipy.stats import gaussian_kde
        y_kde = gaussian_kde(datos)(x_r)
    except ImportError:
        y_kde = _kde_manual(datos.values, x_r)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_r, y=y_kde, mode="lines", fill="tozeroy",
        name="KDE",
        line=dict(color=PALETTE["primary"], width=2.5),
        fillcolor="rgba(46,134,193,0.18)",
    ))

    mu  = float(datos.mean())
    med = float(datos.median())

    fig.add_vline(x=mu, line_dash="dash", line_color=PALETTE["danger"],
                  annotation_text=f"Media={mu:.2f}", annotation_position="top right")
    fig.add_vline(x=med, line_dash="dot", line_color=PALETTE["accent"],
                  annotation_text=f"Mediana={med:.2f}", annotation_position="top left")

    fig.update_layout(
        template=PLOTLY_TEMPLATE, title=f"Curva de Densidad KDE - {columna}",
        xaxis_title=columna, yaxis_title="Densidad", margin=MARGIN,
    )
    return fig


def qq_plot(df, columna):
    """Q-Q Plot de normalidad. Usa scipy si esta disponible; si no, aproximacion manual."""
    datos = df[columna].dropna().astype(float).values
    fig   = go.Figure()

    try:
        from scipy import stats
        (osm, osr), (slope, intercept, r) = stats.probplot(datos, dist="norm")
        osm  = list(osm)
        osr  = list(osr)
        fig.add_trace(go.Scatter(
            x=osm, y=osr, mode="markers", name="Datos observados",
            marker=dict(color=PALETTE["secondary"], size=9, opacity=0.85,
                        line=dict(width=1, color=PALETTE["primary"])),
        ))
        x_line = [min(osm), max(osm)]
        fig.add_trace(go.Scatter(
            x=x_line,
            y=[slope * x_line[0] + intercept, slope * x_line[1] + intercept],
            mode="lines",
            name=f"Referencia normal  R={r:.3f}",
            line=dict(color=PALETTE["danger"], width=2, dash="dash"),
        ))
        titulo = f"Q-Q Plot (Normalidad) - {columna}   |   R={r:.3f}"

    except ImportError:
        # Aproximacion manual: cuantiles normales teoricos por formula de Hazen
        datos_ord = np.sort(datos)
        n = len(datos_ord)
        p = (np.arange(1, n + 1) - 0.5) / n
        # Aproximacion polinomial de la inversa normal (Abramowitz & Stegun)
        def norm_ppf(prob):
            t = np.sqrt(-2 * np.log(np.where(prob < 0.5, prob, 1 - prob)))
            c = [2.515517, 0.802853, 0.010328]
            d = [1.432788, 0.189269, 0.001308]
            val = t - (c[0] + c[1]*t + c[2]*t**2) / (1 + d[0]*t + d[1]*t**2 + d[2]*t**3)
            return np.where(prob < 0.5, -val, val)

        teoricos  = norm_ppf(p)
        datos_std = (datos_ord - datos_ord.mean()) / (datos_ord.std() + 1e-9)

        fig.add_trace(go.Scatter(
            x=list(teoricos), y=list(datos_std), mode="markers", name="Datos observados",
            marker=dict(color=PALETTE["secondary"], size=9, opacity=0.85,
                        line=dict(width=1, color=PALETTE["primary"])),
        ))
        fig.add_trace(go.Scatter(
            x=[-3, 3], y=[-3, 3], mode="lines", name="Referencia normal",
            line=dict(color=PALETTE["danger"], width=2, dash="dash"),
        ))
        titulo = f"Q-Q Plot (Normalidad) - {columna}"

    fig.update_layout(
        template=PLOTLY_TEMPLATE, title=titulo,
        xaxis_title="Cuantiles Teoricos",
        yaxis_title="Cuantiles Observados",
        margin=MARGIN,
    )
    return fig


def tallo_hoja(df, columna):
    """Representacion de tallo y hoja como cadena de texto formateada."""
    datos = df[columna].dropna().sort_values().reset_index(drop=True).astype(float)
    tallos = {}
    for val in datos:
        t = int(np.floor(val))
        h = int(round(abs(val - t) * 10)) % 10
        tallos.setdefault(t, []).append(str(h))

    lineas = [f"  {'Tallo':>6} | Hojas (unidad: 0.1)", "  " + "-" * 35]
    for t in sorted(tallos):
        lineas.append(f"  {t:>6} | {' '.join(tallos[t])}")
    return "\n".join(lineas)
