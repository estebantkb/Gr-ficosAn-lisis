import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from config import PALETTE, COLOR_SEQUENCE, PLOTLY_TEMPLATE, MARGIN


def barras_frecuencia(df, columna):
    """Barras de frecuencias absolutas con etiquetas de porcentaje."""
    freq = df[columna].value_counts().reset_index()
    freq.columns = [columna, "Frecuencia"]
    freq["Pct"] = (freq["Frecuencia"] / freq["Frecuencia"].sum() * 100).round(2)
    freq.sort_values("Frecuencia", ascending=False, inplace=True)

    fig = px.bar(
        freq, x=columna, y="Frecuencia", text="Pct",
        color=columna, color_discrete_sequence=COLOR_SEQUENCE,
        title=f"Frecuencias - {columna}",
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(
        template=PLOTLY_TEMPLATE, margin=MARGIN, showlegend=False,
        xaxis_title=columna, yaxis_title="Frecuencia Absoluta",
    )
    return fig


def pie_dona(df, columna):
    """Grafico de dona con frecuencias de variable categorica."""
    freq = df[columna].value_counts().reset_index()
    freq.columns = [columna, "Frecuencia"]

    fig = px.pie(
        freq, names=columna, values="Frecuencia", hole=0.38,
        color_discrete_sequence=COLOR_SEQUENCE,
        title=f"Proporcion - {columna}",
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(template=PLOTLY_TEMPLATE, margin=MARGIN)
    return fig


def treemap_frecuencias(df, columna):
    """Treemap de frecuencias de variable categorica."""
    freq = df[columna].value_counts().reset_index()
    freq.columns = [columna, "Frecuencia"]

    fig = px.treemap(
        freq, path=[columna], values="Frecuencia",
        color="Frecuencia",
        color_continuous_scale=[[0, PALETTE["light"]], [0.5, PALETTE["secondary"]], [1, PALETTE["primary"]]],
        title=f"Treemap de Frecuencias - {columna}",
    )
    fig.update_layout(template=PLOTLY_TEMPLATE, margin=MARGIN)
    return fig


def tabla_frecuencias(df, columna):
    """Tabla completa: Fi, hi, hi%, Fi acumulada, hi% acumulada."""
    freq = df[columna].value_counts().sort_index().reset_index()
    freq.columns = [columna, "Fi"]
    total = freq["Fi"].sum()
    freq["hi"]         = (freq["Fi"] / total).round(4)
    freq["hi (%)"]     = (freq["hi"] * 100).round(2)
    freq["Fi acum."]   = freq["Fi"].cumsum()
    freq["hi% acum."]  = (freq["Fi acum."] / total * 100).round(2)

    total_row = pd.DataFrame(
        [[f"TOTAL", total, 1.0, 100.0, total, 100.0]],
        columns=freq.columns,
    )
    return pd.concat([freq, total_row], ignore_index=True)
