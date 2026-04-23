import pandas as pd
import numpy as np


def cargar_datos(archivo, separador=";", decimal=","):
    """Carga un CSV y devuelve (df, error_str). Maneja nulos, columnas vacias y espacios."""
    try:
        df = pd.read_csv(
            archivo,
            sep=separador,
            decimal=decimal,
            na_values=["NA", "na", "N/A", "n/a", ""],
            encoding="utf-8",
        )
        # Limpiar nombres de columna
        df.columns = [str(c).strip() for c in df.columns]

        # Renombrar primera columna sin nombre (CSVs de estudiantes)
        sin_nombre = [c for c in df.columns if c == "" or c.startswith("Unnamed")]
        for c in sin_nombre:
            df.rename(columns={c: "ID"}, inplace=True)

        # Eliminar filas completamente vacias
        df.dropna(how="all", inplace=True)
        df.reset_index(drop=True, inplace=True)

        return df, None
    except Exception as exc:
        return None, str(exc)


def cols_numericas(df):
    return df.select_dtypes(include=np.number).columns.tolist()


def cols_categoricas(df):
    return df.select_dtypes(include=["object", "category"]).columns.tolist()


def resumen_estadistico(df):
    """Tabla estadistica completa: media, mediana, moda, std, CV, min/max, Q1/Q3, IQR, asimetria, curtosis."""
    nums = cols_numericas(df)
    if not nums:
        return None

    rows = {}
    for col in nums:
        s = df[col].dropna()
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        media = s.mean()
        rows[col] = {
            "N validos": int(len(s)),
            "Nulos":     int(df[col].isnull().sum()),
            "Media":     round(media, 4),
            "Mediana":   round(s.median(), 4),
            "Moda":      round(s.mode().iloc[0], 4) if not s.mode().empty else None,
            "Desv. Std": round(s.std(), 4),
            "Varianza":  round(s.var(), 4),
            "CV (%)":    round(s.std() / media * 100, 2) if media != 0 else None,
            "Min":       round(s.min(), 4),
            "Q1":        round(q1, 4),
            "Q3":        round(q3, 4),
            "Max":       round(s.max(), 4),
            "IQR":       round(q3 - q1, 4),
            "Asimetria": round(s.skew(), 4),
            "Curtosis":  round(s.kurtosis(), 4),
        }
    return pd.DataFrame(rows).T
