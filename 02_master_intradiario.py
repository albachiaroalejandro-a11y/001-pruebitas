import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings
import os
from datetime import datetime

warnings.simplefilter(action='ignore')

ticker = "GGAL"
print(f"🔄 Procesando Reporte Cuantitativo INTRADIARIO ({ticker})")
print("📥 Descargando historiales de alta frecuencia (15m y 1h)...")

# ==========================================
# 1. DESCARGA Y LIMPIEZA CENTRALIZADA
# ==========================================
# Descargamos 60 días para el micro-régimen y 730 días para el histórico
df_15m = yf.download(ticker, period="60d", interval="15m", progress=False)
df_1h = yf.download(ticker, period="730d", interval="1h", progress=False)

for df in [df_15m, df_1h]:
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.index = pd.to_datetime(df.index)

# Ajuste horario ARG
df_1h.index = df_1h.index.tz_convert('America/Argentina/Buenos_Aires')
df_1h['Hora_ARG'] = df_1h.index.strftime('%H:00')
df_1h['Date'] = df_1h.index.date
df_1h = df_1h[(df_1h['Hora_ARG'] >= '10:00') & (df_1h['Hora_ARG'] <= '18:00')].copy()

df_15m['Date'] = df_15m.index.date

# ==========================================
# 2. PROCESAMIENTO MICRO-RÉGIMEN (15m a 60m)
# ==========================================
res_micro = []
for date, group in df_15m.groupby('Date'):
    if len(group) < 4: continue
    
    h15, l15 = float(group['High'].iloc[0]), float(group['Low'].iloc[0])
    h30, l30 = float(group['High'].iloc[0:2].max()), float(group['Low'].iloc[0:2].min())
    h45, l45 = float(group['High'].iloc[0:3].max()), float(group['Low'].iloc[0:3].min())
    h60, l60 = float(group['High'].iloc[0:4].max()), float(group['Low'].iloc[0:4].min())
    
    res_micro.append({
        '15m': ((h15 - l15) / l15) * 100,
        '30m': ((h30 - l30) / l30) * 100,
        '45m': ((h45 - l45) / l45) * 100,
        '60m': ((h60 - l60) / l60) * 100
    })
df_micro = pd.DataFrame(res_micro)

# ==========================================
# 3. PROCESAMIENTO MACRO-INTRADIARIO (1h)
# ==========================================
res_intra = []
for date, group in df_1h.groupby('Date'):
    if len(group) < 4: continue
    
    # Datos Caja Inicial
    vela_1 = group.iloc[0]
    h_caja, l_caja = float(vela_1['High']), float(vela_1['Low'])
    spread_caja = ((h_caja - l_caja) / l_caja) * 100
    
    # Datos Día Completo
    h_dia, l_dia = float(group['High'].max()), float(group['Low'].min())
    spread_dia = ((h_dia - l_dia) / l_dia) * 100
    
    # Datos MFE (Post-60m)
    resto_dia = group.iloc[1:]
    mfe_neta = 0.0
    if not resto_dia.empty:
        max_post, min_post = float(resto_dia['High'].max()), float(resto_dia['Low'].min())
        if max_post > h_caja: mfe_neta = max(mfe_neta, ((max_post - h_caja) / h_caja) * 100)
        if min_post < l_caja: mfe_neta = max(mfe_neta, ((l_caja - min_post) / l_caja) * 100)
        
    res_intra.append({
        'Fecha': pd.to_datetime(date),
        'Caja_60m': spread_caja,
        'Spread_Dia': spread_dia,
        'MFE': mfe_neta if mfe_neta > 0.1 else np.nan
    })

df_intra = pd.DataFrame(res_intra).set_index('Fecha')

# --- Cálculos Móviles (Rolling) ---
# Rolling Cajas (60 días)
df_intra['Caja_P25'] = df_intra['Caja_60m'].rolling(window=60).quantile(0.25)
df_intra['Caja_P50'] = df_intra['Caja_60m'].rolling(window=60).quantile(0.50)
df_intra['Caja_P75'] = df_intra['Caja_60m'].rolling(window=60).quantile(0.75)

# Rolling MFE (40 días)
df_mfe = df_intra.dropna(subset=['MFE']).copy()
df_mfe['MFE_P50'] = df_mfe['MFE'].rolling(window=40).quantile(0.50)
df_mfe['MFE_P75'] = df_mfe['MFE'].rolling(window=40).quantile(0.75)
df_mfe['MFE_Trend'] = df_mfe['MFE_P50'].rolling(window=15).mean()

# --- Estadística Caja vs Amplitud ---
mediana_historica_caja = df_intra['Caja_60m'].median()
df_intra['Tipo_Caja'] = np.where(df_intra['Caja_60m'] <= mediana_historica_caja, 'Angosta', 'Amplia')
correlacion = df_intra['Caja_60m'].corr(df_intra['Spread_Dia'])

# ==========================================
# 4. EXTRACCIÓN DE DATOS DE HOY
# ==========================================
caja_hoy = df_intra['Caja_60m'].iloc[-1]
p25_caja, p50_caja, p75_caja = df_intra['Caja_P25'].iloc[-1], df_intra['Caja_P50'].iloc[-1], df_intra['Caja_P75'].iloc[-1]

if caja_hoy > p75_caja: estado_caja = "EXTREMA (Fase Expansiva P75+)"
elif caja_hoy > p50_caja: estado_caja = "AMPLIA (Por encima del promedio)"
elif caja_hoy < p25_caja: estado_caja = "MOMIA (Fase Contractiva P25-)"
else: estado_caja = "ANGOSTA (Por debajo del promedio)"

tp1_mfe, tp2_mfe, trend_mfe = df_mfe['MFE_P50'].iloc[-1], df_mfe['MFE_P75'].iloc[-1], df_mfe['MFE_Trend'].iloc[-1]

# ==========================================
# 🖨️ REPORTE EJECUTIVO EN CONSOLA
# ==========================================
print("\n" + "="*60)
print(f" 📑 INFORME CUANTITATIVO INTRADIARIO - {ticker} ADR")
print("="*60)

print("\n🕒 1. MICRO-RÉGIMEN DE APERTURA (Riesgo inicial 60d)")
print("-" * 60)
print(f"Mediana 15m (Riesgo Base):   {df_micro['15m'].median():.2f}%")
print(f"Mediana 30m (Confirmación):  {df_micro['30m'].median():.2f}%")
print(f"Mediana 60m (Caja Total):    {df_micro['60m'].median():.2f}%")

print("\n🎯 2. RÉGIMEN ACTUAL DE LA PRIMERA HORA (60m)")
print("-" * 60)
print(f"Amplitud Hoy:         {caja_hoy:.2f}%")
print(f"Estado del Mercado:   {estado_caja}")
print(f"Umbral de Locura(P75): > {p75_caja:.2f}%")

print("\n🚀 3. TARGETS DE EXPANSIÓN (MFE Post-Quiebre)")
print("-" * 60)
print(f"TP1 (Probable - P50): {tp1_mfe:.2f}% limpio desde la ruptura")
print(f"TP2 (Extremo - P75):  {tp2_mfe:.2f}% limpio desde la ruptura")
momentum_mfe = "CRECIENDO 📈" if tp1_mfe > trend_mfe else "ACHICÁNDOSE 📉"
print(f"Momentum de Targets:  {momentum_mfe}")

print("\n📊 4. IMPACTO DEL TAMAÑO DE CAJA (Efecto Contagio)")
print("-" * 60)
if correlacion > 0.5:
    print(f"Fuerte Correlación ({correlacion:.2f}): El tamaño de la apertura SÍ dicta")
    print("el ritmo. Aperturas violentas garantizan días violentos.")
else:
    print(f"Correlación Débil ({correlacion:.2f}): El mercado es errático. Puede")
    print("dormir en la apertura y explotar después (o viceversa).")
print("="*60 + "\n")

# ==========================================
# 📊 RENDERIZADO VISUAL (DASHBOARD 2x2)
# ==========================================
plt.style.use('dark_background')
fig = plt.figure(figsize=(16, 11))
gs = gridspec.GridSpec(2, 2, height_ratios=[1.2, 1], wspace=0.2, hspace=0.3)
fig.suptitle(f'Dashboard Intradiario de Alta Frecuencia - {ticker} ADR', fontsize=16, fontweight='bold', y=0.98)

# --- PANEL 1: ROLLING CAJAS 60m (Arriba Izquierda) ---
ax1 = plt.subplot(gs[0, 0])
df_plot_1 = df_intra.dropna(subset=['Caja_P50']).iloc[-100:] # Últimos 100 días
ax1.plot(df_plot_1.index, df_plot_1['Caja_P75'], color='orange', alpha=0.6, label='P75 (Techo)')
ax1.plot(df_plot_1.index, df_plot_1['Caja_P50'], color='yellow', linewidth=2, label='P50 (Mediana)')
ax1.plot(df_plot_1.index, df_plot_1['Caja_P25'], color='gray', alpha=0.6, label='P25 (Piso)')
ax1.fill_between(df_plot_1.index, df_plot_1['Caja_P50'], df_plot_1['Caja_P75'], color='mediumseagreen', alpha=0.2)
ax1.fill_between(df_plot_1.index, df_plot_1['Caja_P25'], df_plot_1['Caja_P50'], color='crimson', alpha=0.2)
ax1.scatter(df_plot_1.index, df_plot_1['Caja_60m'], color='dodgerblue', alpha=0.6, s=20)
ax1.scatter(df_plot_1.index[-1], caja_hoy, color='lime', s=100, edgecolors='white', zorder=5) # Punto de hoy
ax1.set_title('Evolución de Cajas Iniciales (Rolling 60d)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Amplitud 1ra Hora (%)')
ax1.legend(loc='upper left', fontsize=9)
ax1.grid(True, linestyle=':', alpha=0.3)

# --- PANEL 2: ROLLING MFE TARGETS (Arriba Derecha) ---
ax2 = plt.subplot(gs[0, 1])
df_plot_2 = df_mfe.dropna(subset=['MFE_Trend']).iloc[-100:]
ax2.plot(df_plot_2.index, df_plot_2['MFE_P75'], color='orange', linewidth=1.5, label='TP2 (P75)')
ax2.plot(df_plot_2.index, df_plot_2['MFE_P50'], color='yellow', linewidth=2.5, label='TP1 (P50)')
ax2.plot(df_plot_2.index, df_plot_2['MFE_Trend'], color='white', linestyle='--', linewidth=1.5, label='Tendencia SMA')
ax2.fill_between(df_plot_2.index, df_plot_2['MFE_P50'], df_plot_2['MFE_Trend'], 
                 where=(df_plot_2['MFE_P50'] >= df_plot_2['MFE_Trend']), color='mediumseagreen', alpha=0.4)
ax2.fill_between(df_plot_2.index, df_plot_2['MFE_P50'], df_plot_2['MFE_Trend'], 
                 where=(df_plot_2['MFE_P50'] < df_plot_2['MFE_Trend']), color='crimson', alpha=0.4)
ax2.set_title('Recorrido Limpio Intradiario Post-Quiebre (MFE)', fontsize=12, fontweight='bold')
ax2.set_ylabel('Expansión Neta (%)')
ax2.legend(loc='upper right', fontsize=9)
ax2.grid(True, linestyle=':', alpha=0.3)

# --- PANEL 3: MICRO-RÉGIMEN BOXPLOT (Abajo Izquierda) ---
ax3 = plt.subplot(gs[1, 0])
bplot3 = ax3.boxplot([df_micro['15m'], df_micro['30m'], df_micro['45m'], df_micro['60m']], 
                     patch_artist=True, tick_labels=['15m', '30m', '45m', '60m'])
colors3 = ['dodgerblue', 'orange', 'mediumseagreen', 'crimson']
for patch, color in zip(bplot3['boxes'], colors3):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
for median in bplot3['medians']: median.set(color='white', linewidth=2)
ax3.set_title('Expansión de la Caja en la Primera Hora (Últimos 60d)', fontsize=12, fontweight='bold')
ax3.set_ylabel('Amplitud (%)')
ax3.grid(axis='y', linestyle='--', alpha=0.3)

# --- PANEL 4: DISPERSIÓN CAJA VS DÍA (Abajo Derecha) ---
ax4 = plt.subplot(gs[1, 1])
ax4.scatter(df_intra['Caja_60m'], df_intra['Spread_Dia'], color='dodgerblue', alpha=0.6, edgecolors='w')
ax4.axvline(mediana_historica_caja, color='white', linestyle='--', linewidth=2, label=f'Mediana ({mediana_historica_caja:.2f}%)')
m, b = np.polyfit(df_intra['Caja_60m'], df_intra['Spread_Dia'], 1)
ax4.plot(df_intra['Caja_60m'], m*df_intra['Caja_60m'] + b, color='orange', linewidth=2, linestyle=':', label='Tendencia')
ax4.set_title(f'Impacto de la Apertura en la Rueda (Correlación: {correlacion:.2f})', fontsize=12, fontweight='bold')
ax4.set_xlabel('Amplitud Caja 60m (%)')
ax4.set_ylabel('Amplitud Total Día (%)')
ax4.grid(True, linestyle=':', alpha=0.3)
ax4.legend(fontsize=9)

plt.tight_layout()

# ==========================================
# 💾 EXPORTACIÓN GRÁFICA ESTÁTICA
# ==========================================
carpeta_actual = os.path.dirname(os.path.abspath(__file__))
nombre_archivo = os.path.join(carpeta_actual, f"GRAFICO_INTRADIA_{datetime.now().strftime('%H%M%S')}.png")

plt.savefig(nombre_archivo, dpi=100)
plt.close(fig) 
os.startfile(nombre_archivo)