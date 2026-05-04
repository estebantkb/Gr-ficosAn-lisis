"""
charts/atipicos.py
Graficos y tablas para la identificacion de datos atipicos (outliers).

Implementa la logica de la regla del rango intercuartil (RIC/IQR):
  Limite superior moderado : Q3 + 1.5 * IQR
  Limite inferior moderado : Q1 - 1.5 * IQR
  Limite superior extremo  : Q3 + 3.0 * IQR
  Limite inferior extremo  : Q1 - 3.0 * IQR
"""
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from config import PALETTE, COLOR_SEQUENCE, PLOTLY_TEMPLATE, MARGIN


# ---------------------------------------------------------------------------
# Calculo de limites IQR
# ---------------------------------------------------------------------------

def calcular_limites(serie, factor=1.5):
    """Devuelve un dict con Q1, Q2, Q3, IQR y limites superior/inferior."""
    s = serie.dropna().astype(float)
    q1  = float(s.quantile(0.25))
    q2  = float(s.quantile(0.50))
    q3  = float(s.quantile(0.75))
    iqr = q3 - q1
    return {
        "Q1":  q1,
        "Q2 (Mediana)": q2,
        "Q3":  q3,
        "IQR": round(iqr, 4),
        "Limite Inferior": round(q1 - factor * iqr, 4),
        "Limite Superior": round(q3 + factor * iqr, 4),
        "factor": factor,
    }


# ---------------------------------------------------------------------------
# Tabla de atipicos detectados
# ---------------------------------------------------------------------------

def tabla_atipicos(df, columna, factor=1.5):
    """Retorna un DataFrame con todos los outliers detectados.

    Columnas del resultado:
      - Indice     : posicion en el dataset original
      - Nombre     : valor del indice (o numero de fila)
      - Valor      : valor numerico del dato atipico
      - Tipo       : 'Superior' o 'Inferior'
      - Diferencia : cuanto supera el limite
    """
    serie  = df[columna].dropna().astype(float)
    lims   = calcular_limites(serie, factor)
    li     = lims["Limite Inferior"]
    ls     = lims["Limite Superior"]

    # Reconstruir serie con indice original del df
    serie_completa = df[columna].dropna().astype(float)

    filas = []
    for idx, val in serie_completa.items():
        if val < li:
            filas.append({
                "Fila":       idx,
                "Valor":      round(val, 4),
                "Tipo":       "Inferior",
                "Limite":     round(li, 4),
                "Diferencia": round(li - val, 4),
            })
        elif val > ls:
            filas.append({
                "Fila":       idx,
                "Valor":      round(val, 4),
                "Tipo":       "Superior",
                "Limite":     round(ls, 4),
                "Diferencia": round(val - ls, 4),
            })

    if filas:
        return pd.DataFrame(filas).reset_index(drop=True)
    return pd.DataFrame(columns=["Fila", "Valor", "Tipo", "Limite", "Diferencia"])


# ---------------------------------------------------------------------------
# Boxplot con percentiles anotados (diapo 56)
# ---------------------------------------------------------------------------

def boxplot_percentiles(df, columna, factor=1.5):
    """Boxplot horizontal que muestra explicitamente los percentiles
    10, 25, 50, 75, 90 con lineas verticales y etiquetas, ademas de
    los limites IQR y los outliers coloreados en rojo."""
    datos = df[columna].dropna().astype(float)
    n     = len(datos)

    lims  = calcular_limites(datos, factor)
    q1    = lims["Q1"]
    q2    = lims["Q2 (Mediana)"]
    q3    = lims["Q3"]
    iqr   = lims["IQR"]
    li    = lims["Limite Inferior"]
    ls    = lims["Limite Superior"]

    p10 = float(datos.quantile(0.10))
    p90 = float(datos.quantile(0.90))

    notch_hw   = 1.57 * iqr / np.sqrt(n) if n > 1 else 0
    usar_notch = bool(
        (n >= 30) and
        (q2 - notch_hw >= q1) and
        (q2 + notch_hw <= q3)
    )

    # Separar outliers de valores normales
    mask_out = (datos < li) | (datos > ls)
    normales  = datos[~mask_out]
    atipicos  = datos[mask_out]

    fig = go.Figure()

    # Boxplot principal (sin mostrar puntos — los ponemos manualmente)
    fig.add_trace(go.Box(
        x=normales,
        name=columna,
        boxmean="sd",
        notched=usar_notch,
        boxpoints=False,
        line=dict(color=PALETTE["primary"], width=2),
        fillcolor="rgba(46,134,193,0.18)",
        marker=dict(color=PALETTE["primary"]),
    ))

    # Puntos normales
    if len(normales) > 0:
        fig.add_trace(go.Scatter(
            x=normales,
            y=[columna] * len(normales),
            mode="markers",
            marker=dict(color=PALETTE["secondary"], size=7, opacity=0.6),
            name="Datos normales",
            hovertemplate="%{x:.3f}<extra>Normal</extra>",
        ))

    # Outliers en rojo
    if len(atipicos) > 0:
        fig.add_trace(go.Scatter(
            x=atipicos,
            y=[columna] * len(atipicos),
            mode="markers",
            marker=dict(color=PALETTE["danger"], size=10, opacity=0.9,
                        symbol="diamond",
                        line=dict(width=1.5, color="darkred")),
            name="Atipicos",
            hovertemplate="%{x:.3f}<extra>ATIPICO</extra>",
        ))

    # Lineas de percentiles
    percentiles_info = [
        (p10, "P10", "dash",   PALETTE["muted"]),
        (q1,  "Q1 (P25)", "dot", PALETTE["accent"]),
        (q2,  "Mediana (P50)", "solid", PALETTE["success"]),
        (q3,  "Q3 (P75)", "dot", PALETTE["accent"]),
        (p90, "P90", "dash",   PALETTE["muted"]),
    ]
    for val, etq, estilo, color in percentiles_info:
        fig.add_vline(
            x=val, line_dash=estilo, line_color=color, line_width=1.5,
            annotation_text=f"{etq}={val:.2f}",
            annotation_position="top",
            annotation_font=dict(size=9, color=color),
        )

    # Limites IQR
    fig.add_vline(x=li, line_dash="longdash", line_color=PALETTE["danger"],
                  line_width=1.5,
                  annotation_text=f"Li={li:.2f}",
                  annotation_position="bottom",
                  annotation_font=dict(size=9, color=PALETTE["danger"]))
    fig.add_vline(x=ls, line_dash="longdash", line_color=PALETTE["danger"],
                  line_width=1.5,
                  annotation_text=f"Ls={ls:.2f}",
                  annotation_position="bottom",
                  annotation_font=dict(size=9, color=PALETTE["danger"]))

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title=(f"Boxplot con Percentiles - {columna}  "
               f"(n={n}  IQR={iqr:.2f}  factor={factor})"),
        xaxis_title=columna,
        yaxis=dict(showticklabels=False),
        height=380,
        margin=dict(l=60, r=60, t=90, b=50),
        showlegend=True,
        legend=dict(orientation="h", y=-0.15),
    )
    return fig


# ---------------------------------------------------------------------------
# Boxplot comparativo de multiples columnas (diapos 56-61)
# ---------------------------------------------------------------------------

def boxplot_comparativo(df, columnas, factor=1.5):
    """Un boxplot por cada columna seleccionada, todos en el mismo grafico
    para comparar su distribucion y detectar outliers de forma conjunta."""
    fig = go.Figure()
    colores = COLOR_SEQUENCE * (len(columnas) // len(COLOR_SEQUENCE) + 1)

    for i, col in enumerate(columnas):
        serie = df[col].dropna().astype(float)
        if len(serie) == 0:
            continue

        lims   = calcular_limites(serie, factor)
        li     = lims["Limite Inferior"]
        ls     = lims["Limite Superior"]
        mask   = (serie < li) | (serie > ls)
        out_x  = serie[mask].tolist()
        out_y  = [col] * len(out_x)

        fig.add_trace(go.Box(
            y=serie, name=col,
            boxmean="sd",
            boxpoints=False,
            line=dict(color=colores[i], width=2),
            fillcolor=f"rgba(46,134,193,0.12)",
            marker=dict(color=colores[i]),
        ))
        # Outliers marcados
        if out_x:
            fig.add_trace(go.Scatter(
                x=[col] * len(out_x),
                y=out_x,
                mode="markers",
                marker=dict(color=PALETTE["danger"], size=9, symbol="diamond",
                            line=dict(width=1.5, color="darkred")),
                name=f"Atipicos {col}",
                hovertemplate=f"<b>{col}</b>: %{{y:.3f}}<extra>ATIPICO</extra>",
            ))

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title="Boxplot Comparativo - Multiples Variables",
        yaxis_title="Valor",
        xaxis_title="Variable",
        height=480,
        margin=MARGIN,
        showlegend=False,
    )
    return fig
