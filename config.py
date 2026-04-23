# Configuracion global: paleta de colores, tema Plotly y constantes de la app

PALETTE = {
    "primary":    "#1B4F8A",
    "secondary":  "#2E86C1",
    "accent":     "#F39C12",
    "danger":     "#C0392B",
    "success":    "#1E8449",
    "background": "#F4F6F9",
    "card":       "#FFFFFF",
    "text":       "#2C3E50",
    "muted":      "#7F8C8D",
    "light":      "#D6EAF8",
}

COLOR_SEQUENCE = [
    "#1B4F8A", "#2E86C1", "#F39C12",
    "#1E8449", "#C0392B", "#8E44AD",
    "#16A085", "#D35400", "#2C3E50",
]

PLOTLY_TEMPLATE = "plotly_white"
MARGIN = dict(l=30, r=30, t=50, b=30)

APP_TITLE      = "Sistema de Analisis de Datos"
APP_SUBTITLE   = "Esteban Narvaez | Analisis de Datos | Universidad Central del Ecuador"
FOOTER_TEXT    = "Desarrollado para la Catedra de Analisis de Datos | FICA - UCE | 2026"

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: #2C3E50;
}
.main { background-color: #F4F6F9; }

h1 { color: #1B4F8A !important; font-weight: 700 !important; }
h2, h3 { color: #1B4F8A !important; font-weight: 600 !important; }

[data-testid="stMetricValue"] {
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: #1B4F8A !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.78rem !important;
    color: #7F8C8D !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
[data-testid="stSidebar"] {
    background-color: #1B4F8A !important;
}
[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stFileUploader label {
    color: #D6EAF8 !important;
}
div[data-baseweb="tab-list"] button[aria-selected="true"] {
    border-bottom: 3px solid #1B4F8A !important;
    color: #1B4F8A !important;
    font-weight: 600;
}
.stAlert { border-radius: 8px; }

.footer {
    position: fixed; left: 0; bottom: 0; width: 100%;
    background-color: #1B4F8A; color: #D6EAF8;
    text-align: center; padding: 8px;
    font-size: 12px; letter-spacing: 0.03em;
    z-index: 999;
}
.metric-card {
    background: #FFFFFF;
    border-left: 4px solid #1B4F8A;
    border-radius: 8px;
    padding: 14px 18px;
    box-shadow: 0 2px 8px rgba(27,79,138,0.08);
}
</style>
"""
