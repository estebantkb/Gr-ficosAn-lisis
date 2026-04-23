import sys
sys.path.insert(0, 'c:/Users/Estebxn/Desktop/SIU/S6/ANALISIS/Tarea1')
from data_loader import cargar_datos, cols_numericas, cols_categoricas
from charts import univariado, bivariado, categorico, multivariado
import numpy as np

base = 'c:/Users/Estebxn/Desktop/SIU/S6/ANALISIS/Tarea1/'

with open(base + 'EjemploClientes.csv', 'rb') as f:
    df_c, _ = cargar_datos(f, ';', ',')
nums_c = cols_numericas(df_c)
cats_c = cols_categoricas(df_c)

with open(base + 'EjemploEstudiantes - categorico.csv', 'rb') as f:
    df_k, _ = cargar_datos(f, ';', ',')
nums_k = cols_numericas(df_k)
cats_k = cols_categoricas(df_k)

with open(base + 'EjemploEstudiantesAtipicos.csv', 'rb') as f:
    df_at, _ = cargar_datos(f, ';', ',')
nums_at = cols_numericas(df_at)

errores = []

def check(nombre, cond, detalle=''):
    estado = 'OK' if cond else 'FALLO'
    print(f'  [{estado}] {nombre}' + (f' -> {detalle}' if detalle else ''))
    if not cond:
        errores.append(nombre)

print('=== HISTOGRAMA ===')
fig = univariado.histograma_kde(df_c, 'Edad')
check('tiene histograma', any(t.type == 'histogram' for t in fig.data))
check('histnorm=probability density', fig.data[0].histnorm == 'probability density')
check('tiene curva normal', any(getattr(t,'name','') == 'Normal teorica' for t in fig.data))
check('x correcto (variable en eje X)', fig.layout.xaxis.title.text == 'Edad')

print('=== BOXPLOT ===')
fig = univariado.boxplot(df_c, 'Edad')
b = fig.data[0]
check('horizontal (x=datos, y=None)', b.x is not None and b.y is None)
check('notched=True', b.notched)
check('boxmean=sd', b.boxmean == 'sd')
check('boxpoints=outliers', b.boxpoints == 'outliers')
check('height fijo', fig.layout.height == 320)
# Verificar que la anotacion tiene los 5 estadisticos
ann = fig.layout.annotations[0].text if fig.layout.annotations else ''
check('anotacion con Min/Q1/Med/Q3/Max', all(k in ann for k in ['Min=','Q1=','Med=','Q3=','Max=','IQR=']))

print('=== BOXPLOT con n pequeno (Estudiantes, n=10) ===')
fig2 = univariado.boxplot(df_k, 'Matematicas')
b2 = fig2.data[0]
datos_mat = df_k['Matematicas'].dropna()
q1, q3 = datos_mat.quantile(0.25), datos_mat.quantile(0.75)
iqr = q3 - q1
n = len(datos_mat)
notch_hw = 1.57 * iqr / np.sqrt(n)
med = datos_mat.median()
fuera = med - notch_hw < q1 or med + notch_hw > q3
print(f'  n={n}, notch fuera de caja: {fuera}')
check('notch NO fuera de caja o notched=False para n pequeno',
      not fuera or not b2.notched,
      f'notch_hw={notch_hw:.3f}, IQR/2={iqr/2:.3f}')

print('=== VIOLIN ===')
fig = univariado.violin(df_c, 'Edad')
check('tipo violin', fig.data[0].type == 'violin')
check('box interno visible', fig.data[0].box.visible == True)
check('points=outliers', fig.data[0].points == 'outliers')

print('=== DENSIDAD ===')
fig = univariado.densidad(df_c, 'Edad')
check('tiene traza de densidad', len(fig.data) >= 1)
check('fill=tozeroy', fig.data[0].fill == 'tozeroy')
check('tiene vlines de media y mediana', len(fig.layout.shapes) >= 2 or len(fig.layout.annotations) >= 2)

print('=== Q-Q PLOT ===')
fig = univariado.qq_plot(df_c, 'Edad')
check('tiene 2 trazas (puntos + linea ref)', len(fig.data) >= 2)
check('xaxis=Cuantiles Teoricos', 'Teorico' in fig.layout.xaxis.title.text)
check('yaxis=Cuantiles Observados', 'Observado' in fig.layout.yaxis.title.text)
# Verificar que los puntos esten ordenados correctamente
x_pts = list(fig.data[0].x)
check('puntos Q-Q ordenados', x_pts == sorted(x_pts))

print('=== TALLO Y HOJA ===')
txt = univariado.tallo_hoja(df_c, 'Edad')
lineas = [l for l in txt.split('\n') if l.strip()]
datos_ord = sorted(df_c['Edad'].dropna())
check('tiene encabezado', 'Tallo' in lineas[0])
check('rango min cubierto', str(int(np.floor(datos_ord[0]))) in txt)
check('rango max cubierto', str(int(np.floor(datos_ord[-1]))) in txt)

print('=== SCATTER REGRESION ===')
fig = bivariado.scatter_regresion(df_c, 'Edad', 'Antiguedad')
tipos = [t.type for t in fig.data]
check('tiene scatter', 'scatter' in tipos)
check('tiene linea de regresion (2 trazas)', len(fig.data) == 2)
ann = fig.layout.annotations[0].text if fig.layout.annotations else ''
check('anotacion con y=', 'y =' in ann)
check('anotacion con R=', 'R =' in ann)
check('anotacion con R2=', 'R2 =' in ann)

print('=== SCATTER ELIPSE ===')
fig = bivariado.scatter_elipse(df_c, 'Edad', 'Antiguedad')
check('tiene scatter', any(t.type == 'scatter' for t in fig.data))
print(f'  trazas: {len(fig.data)} (1=solo puntos si sin scipy, 2=puntos+elipse si scipy)')

print('=== BUBBLE CHART ===')
fig = bivariado.bubble_chart(df_c, 'Edad', 'Antiguedad', 'Espacios Parqueo')
check('tiene scatter', fig.data[0].type == 'scatter')
check('marker sizemode=area', fig.data[0].marker.sizemode == 'area')
print(f'  sizemin={fig.data[0].marker.sizemin}  (bubble chart OK)')

print('=== PAIRS PLOT (SPLOM) ===')
fig = bivariado.pairs_plot(df_c, nums_c[:4])
check('tipo splom', fig.data[0].type == 'splom')
check('4 dimensiones', len(fig.data[0].dimensions) == 4)
check('showupperhalf=False', fig.data[0].showupperhalf == False)

print('=== BARRAS FRECUENCIA ===')
fig = categorico.barras_frecuencia(df_k, 'Provincia')
check('tipo bar', fig.data[0].type == 'bar')
check('texto de porcentaje', fig.data[0].texttemplate is not None)

print('=== PIE DONA ===')
fig = categorico.pie_dona(df_k, 'Provincia')
check('tipo pie', fig.data[0].type == 'pie')
check('hole=0.38 (dona)', abs(fig.data[0].hole - 0.38) < 0.01)
check('textinfo incluye percent', 'percent' in fig.data[0].textinfo)

print('=== TREEMAP ===')
fig = categorico.treemap_frecuencias(df_k, 'Provincia')
check('tipo treemap', fig.data[0].type == 'treemap')

print('=== TABLA FRECUENCIAS ===')
tbl = categorico.tabla_frecuencias(df_k, 'Provincia')
check('columnas correctas', list(tbl.columns) == ['Provincia', 'Fi', 'hi', 'hi (%)', 'Fi acum.', 'hi% acum.'])
check('fila TOTAL al final', tbl.iloc[-1]['Provincia'] == 'TOTAL')
check('hi% acum. ultimo=100', tbl.iloc[-1]['hi% acum.'] == 100.0)

print('=== HEATMAP CORRELACION ===')
fig, corr = multivariado.heatmap_correlacion(df_c, nums_c[:5])
diag_ok = all(abs(corr.values[i,i] - 1.0) < 1e-9 for i in range(5))
check('diagonal=1.0', diag_ok)
check('zmid=0', fig.data[0].zmid == 0)
check('zmin=-1 zmax=1', fig.data[0].zmin == -1 and fig.data[0].zmax == 1)
check('texto anotado en celdas', fig.data[0].texttemplate == '%{text}')

print('=== COORDENADAS PARALELAS ===')
fig = multivariado.coordenadas_paralelas(df_c, nums_c[:5])
check('tipo parcoords', fig.data[0].type == 'parcoords')
check('5 dimensiones', len(fig.data[0].dimensions) == 5)

print('=== RADAR ===')
fig = multivariado.radar(df_c, nums_c[:5])
r = list(fig.data[0].r)
theta = list(fig.data[0].theta)
check('tipo scatterpolar', fig.data[0].type == 'scatterpolar')
check('cierra poligono (r[0]==r[-1])', abs(r[0]-r[-1]) < 1e-9)
check('n_puntos=n_vars+1', len(r) == 6)

print('=== HEATMAP DATOS ===')
fig = multivariado.heatmap_datos(df_c, nums_c[:5])
z = fig.data[0].z
vals_planos = [v for fila in z for v in fila]
check('37 filas (todos los registros)', len(z) == 37)
check('5 columnas', len(z[0]) == 5)
check('valores normalizados en [0,1]', min(vals_planos) >= -1e-9 and max(vals_planos) <= 1+1e-9)

print()
print(f'=== RESUMEN: {len(errores)} FALLOS ===')
for e in errores:
    print(f'  - {e}')
if not errores:
    print('  Todos los graficos pasaron la verificacion.')
