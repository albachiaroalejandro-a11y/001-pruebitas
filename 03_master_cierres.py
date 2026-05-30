import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as patches
import matplotlib.colors as mcolors
import warnings
import os
from datetime import datetime

warnings.simplefilter(action='ignore')

ticker = "GGAL"
print(f"🔄 Procesando Master de Cierres y Mapa Compuesto ({ticker})...")

# ==========================================
# 1. DESCARGA CENTRALIZADA
# ==========================================
print("📥 Descargando historiales diarios y semanales (Últimos 5 años)...")
df_d = yf.download(ticker, period="5y", interval="1d", progress=False)
df_w = yf.download(ticker, period="5y", interval="1wk", progress=False)

for df in [df_d, df_w]:
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

# Filtramos velas válidas
df_d = df_d[df_d['High'] > df_d['Low']].copy()
df_w = df_w[df_w['High'] > df_w['Low']].copy()

# ==========================================
# 2. CÁLCULO DE CLOSE LOCATION VALUE (CLV)
# ==========================================
df_d['CLV_%'] = ((df_d['Close'] - df_d['Low']) / (df_d['High'] - df_d['Low'])) * 100
df_w['CLV_%'] = ((df_w['Close'] - df_w['Low']) / (df_w['High'] - df_w['Low'])) * 100

bins = [0, 20, 40, 60, 80, 100]
etiquetas = [
    "1. Extremo Inf\n(0-20%)", 
    "2. Medio-Bajo\n(20-40%)", 
    "3. Neutral\n(40-60%)", 
    "4. Medio-Alto\n(60-80%)", 
    "5. Extremo Sup\n(80-100%)"
]

df_d['Zona_CLV'] = pd.cut(df_d['CLV_%'], bins=bins, labels=etiquetas, include_lowest=True)
df_w['Zona_CLV'] = pd.cut(df_w['CLV_%'], bins=bins, labels=etiquetas, include_lowest=True)

prob_diaria = (df_d['Zona_CLV'].value_counts(normalize=True).sort_index() * 100)
prob_semanal = (df_w['Zona_CLV'].value_counts(normalize=True).sort_index() * 100)

# ==========================================
# 3. PREPARACIÓN DEL HEATMAP COMPUESTO
# ==========================================
df_bull = df_w[df_w['Close'] >= df_w['Open']].copy()
df_bull['MFE_%'] = ((df_bull['High'] - df_bull['Low']) / df_bull['Low']) * 100

mfe_p25 = df_bull['MFE_%'].quantile(0.25)
mfe_p50 = df_bull['MFE_%'].quantile(0.50)
mfe_p75 = df_bull['MFE_%'].quantile(0.75)
mfe_p90 = df_bull['MFE_%'].quantile(0.90)

# Re-calculamos prob CLV solo para semanas Bull
df_bull['Zona_CLV_num'] = pd.cut(df_bull['CLV_%'], bins=bins, include_lowest=True)
prob_clv_bull = (df_bull['Zona_CLV_num'].value_counts(normalize=True).sort_index() * 100).values

spot = float(df_d['Close'].iloc[-1])

# Extraer caja del Día 1 de la semana actual
df_d['Year'] = df_d.index.isocalendar().year
df_d['Week'] = df_d.index.isocalendar().week
current_year = df_d['Year'].iloc[-1]
current_week = df_d['Week'].iloc[-1]

df_current_week = df_d[(df_d['Year'] == current_year) & (df_d['Week'] == current_week)]

if not df_current_week.empty:
    d1_high, d1_low = float(df_current_week['High'].iloc[0]), float(df_current_week['Low'].iloc[0])
    d1_open, d1_close = float(df_current_week['Open'].iloc[0]), float(df_current_week['Close'].iloc[0])
else:
    d1_high, d1_low, d1_open, d1_close = spot*1.01, spot*0.99, spot, spot

# ==========================================
# 4. IMPRESIÓN EN CONSOLA (CLV)
# ==========================================
print("\n" + "="*55)
print(f" 🎯 PROBABILIDADES DE ZONA DE CIERRE (CLV) - {ticker}")
print("="*55)
print("📊 DISTRIBUCIÓN DIARIA (Dónde cierra el día):")
for zona, prob in prob_diaria.items():
    print(f"   - {str(zona).replace(chr(10), ' ')}: {prob:.2f}%")

print("-" * 55)
print("📅 DISTRIBUCIÓN SEMANAL (Dónde cierra el Viernes):")
for zona, prob in prob_semanal.items():
    print(f"   - {str(zona).replace(chr(10), ' ')}: {prob:.2f}%")
print("="*55)

# ==========================================
# 5. RENDERIZADO DEL DASHBOARD (2x2 Grid)
# ==========================================
plt.style.use('dark_background')
fig = plt.figure(figsize=(16, 12))
gs = gridspec.GridSpec(2, 2, height_ratios=[1, 1.5], wspace=0.2, hspace=0.3)
fig.suptitle(f'Master de Cierres y Probabilidad Compuesta (GGAL ADR)', fontsize=16, fontweight='bold', y=0.97)

colores_clv = ['crimson', 'salmon', 'gray', 'mediumseagreen', 'lime']

# --- PANEL 1: CLV DIARIO (Arriba Izquierda) ---
ax1 = plt.subplot(gs[0, 0])
barras_d = ax1.bar(prob_diaria.index, prob_diaria.values, color=colores_clv, alpha=0.8, edgecolor='white')
ax1.set_title('Comportamiento DIARIO (Vela 1D)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Probabilidad Histórica (%)')
ax1.tick_params(axis='x', rotation=0, labelsize=9)
ax1.grid(axis='y', linestyle=':', alpha=0.4)
for bar in barras_d:
    yval = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2, yval + 0.5, f"{yval:.1f}%", ha='center', fontweight='bold', fontsize=9)

# --- PANEL 2: CLV SEMANAL (Arriba Derecha) ---
ax2 = plt.subplot(gs[0, 1])
barras_w = ax2.bar(prob_semanal.index, prob_semanal.values, color=colores_clv, alpha=0.8, edgecolor='white')
ax2.set_title('Comportamiento SEMANAL (Vela 1W)', fontsize=12, fontweight='bold')
ax2.tick_params(axis='x', rotation=0, labelsize=9)
ax2.grid(axis='y', linestyle=':', alpha=0.4)
for bar in barras_w:
    yval = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2, yval + 0.5, f"{yval:.1f}%", ha='center', fontweight='bold', fontsize=9)

# --- PANEL 3: HEATMAP DE CONFLUENCIA (Abajo Ocupando 2 Columnas) ---
ax3 = plt.subplot(gs[1, :])

# Dibujar caja Día 1
ax3.plot([0, 0], [d1_low, d1_high], color='white', linewidth=2) 
color_caja = 'mediumseagreen' if d1_close >= d1_open else 'crimson'
rect_d1 = patches.Rectangle((-0.2, min(d1_open, d1_close)), 0.4, abs(d1_close - d1_open), 
                            facecolor=color_caja, edgecolor='white', linewidth=1.5)
ax3.add_patch(rect_d1)
ax3.text(0, d1_low - (spot*0.01), "Caja Día 1\n(Riesgo)", ha='center', va='top', color='white', fontsize=10)

ax3.axhline(spot, color='dodgerblue', linestyle='-.', linewidth=1.5, label=f"Spot Actual: ${spot:.2f}")
ax3.axhline(d1_high, color='gray', linestyle=':', linewidth=1)

scenarios = [
    {'name': 'P25 (Corto)', 'mfe': mfe_p25, 'prob_reach': 75, 'x': 2},
    {'name': 'P50 (Medio)', 'mfe': mfe_p50, 'prob_reach': 50, 'x': 4},
    {'name': 'P75 (Óptimo)', 'mfe': mfe_p75, 'prob_reach': 25, 'x': 6},
    {'name': 'P90 (Extremo)', 'mfe': mfe_p90, 'prob_reach': 10, 'x': 8}
]

max_y_plot = spot 
bloques = []

for esc in scenarios:
    techo = d1_high * (1 + esc['mfe']/100)
    rango = techo - d1_high
    max_y_plot = max(max_y_plot, techo)
    ax3.text(esc['x'] + 0.5, techo + (spot*0.01), f"{esc['name']}\nLlegar: {esc['prob_reach']}%",
            ha='center', va='bottom', color='white', fontweight='bold', fontsize=10)
    
    for j in range(5):
        piso_z = d1_high + (j * rango / 5)
        alto_z = rango / 5
        p_clv = prob_clv_bull[j]
        score = (esc['prob_reach'] / 100) * (p_clv / 100) * 100
        
        bloques.append({
            'x': esc['x'], 'piso_z': piso_z, 'alto_z': alto_z,
            'p_clv': p_clv, 'score': score
        })

scores_list = [b['score'] for b in bloques]
min_score, max_score = min(scores_list), max(scores_list)
cmap = mcolors.LinearSegmentedColormap.from_list("escala_score", ['#8b0000', '#cd5c5c', '#808080', '#3cb371', '#00ff00'])
norm = mcolors.Normalize(vmin=min_score, vmax=max_score)

for b in bloques:
    color_bloque = cmap(norm(b['score']))
    rect = patches.Rectangle((b['x'], b['piso_z']), 1, b['alto_z'], 
                             linewidth=1, edgecolor='black', facecolor=color_bloque, alpha=0.9)
    ax3.add_patch(rect)
    txt = f"Cierre: {b['p_clv']:.1f}%\nScore: {b['score']:.1f}"
    ax3.text(b['x'] + 0.5, b['piso_z'] + (b['alto_z']/2), txt, ha='center', va='center', color='white', fontsize=9, fontweight='bold')

ax3.set_ylim(d1_low * 0.95, max_y_plot * 1.08)
ax3.set_title("Rejilla de Confluencia (Heatmap por Score Global)", fontsize=13, fontweight='bold')
ax3.set_xlim(-1, 10)
ax3.set_xticks([]) 
ax3.set_ylabel("Precio Proyectado (USD)")
ax3.grid(axis='y', linestyle=':', alpha=0.3)
ax3.legend(loc='upper left')

plt.tight_layout()

# ==========================================
# 💾 EXPORTACIÓN GRÁFICA ESTÁTICA
# ==========================================
carpeta_actual = os.path.dirname(os.path.abspath(__file__))
nombre_archivo = os.path.join(carpeta_actual, f"GRAFICO_CIERRES_{datetime.now().strftime('%H%M%S')}.png")

plt.savefig(nombre_archivo, dpi=100)
plt.close(fig) 
os.startfile(nombre_archivo)