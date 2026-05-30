import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings
import os
from datetime import datetime

warnings.simplefilter(action='ignore', category=FutureWarning)

ticker = "GGAL"
print(f"🔄 Procesando Reporte Cuantitativo Semanal ({ticker}) - Base 1 Año...")

# ==========================================
# 📥 DESCARGA DE DATOS
# ==========================================
df_d = yf.download(ticker, period="5y", interval="1d", progress=False)
df_w = yf.download(ticker, period="5y", interval="1wk", progress=False)

for df in [df_d, df_w]:
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

# ==========================================
# 📊 MÓDULO 1: MACRO VOLATILIDAD
# ==========================================
df_w['Spread_%'] = ((df_w['High'] - df_w['Low']) / df_w['Low']) * 100
df_w_limpio = df_w[(df_w['Spread_%'] > 0) & (df_w['Spread_%'] <= 60.0)].copy()

df_w_limpio['P50_Rodante'] = df_w_limpio['Spread_%'].rolling(window=13).quantile(0.50)
df_w_limpio['Tendencia_P50'] = df_w_limpio['P50_Rodante'].rolling(window=4).mean()
df_w_rodante = df_w_limpio.dropna(subset=['Tendencia_P50'])

df_w_plot = df_w_rodante.iloc[-52:]

m1_p50 = df_w_plot['P50_Rodante'].iloc[-1]
m1_tendencia = df_w_plot['Tendencia_P50'].iloc[-1]
m1_estado = "EXPANSIÓN 📈" if m1_p50 > m1_tendencia else "CONTRACCIÓN 📉"

# ==========================================
# 🎯 MÓDULO 2: PODER PREDICTIVO (DÍA 1)
# ==========================================
df_d['Year'] = df_d.index.isocalendar().year
df_d['Week'] = df_d.index.isocalendar().week

m2_resultados = []
for (year, week), group in df_d.groupby(['Year', 'Week']):
    if len(group) < 3: continue
    group = group.sort_index()
    
    dia1_open, dia1_close = float(group['Open'].iloc[0]), float(group['Close'].iloc[0])
    sem_close = float(group['Close'].iloc[-1])
    
    if dia1_open == dia1_close or dia1_open == sem_close: continue
    
    dia1_alcista = dia1_close > dia1_open
    sem_alcista = sem_close > dia1_open
    
    m2_resultados.append({
        'Fecha': group.index[-1],
        'Dia1_Alcista': dia1_alcista,
        'Acierto': 1 if (dia1_alcista == sem_alcista) else 0
    })

df_m2 = pd.DataFrame(m2_resultados)
df_m2_ult_anio = df_m2.iloc[-52:] 

hit_rate_gral = (df_m2_ult_anio['Acierto'].sum() / len(df_m2_ult_anio)) * 100
dias_verdes = df_m2_ult_anio[df_m2_ult_anio['Dia1_Alcista'] == True]
dias_rojos = df_m2_ult_anio[df_m2_ult_anio['Dia1_Alcista'] == False]

hr_verde = (dias_verdes['Acierto'].sum() / len(dias_verdes)) * 100 if len(dias_verdes)>0 else 0
hr_rojo = (dias_rojos['Acierto'].sum() / len(dias_rojos)) * 100 if len(dias_rojos)>0 else 0

ultimo_dia1_alcista = df_m2['Dia1_Alcista'].iloc[-1]
sesgo_actual = "ALCISTA 🟩" if ultimo_dia1_alcista else "BAJISTA 🟥"
prob_acierto = hr_verde if ultimo_dia1_alcista else hr_rojo

# ==========================================
# 📦 MÓDULO 3: RIESGO Y TARGETS MFE
# ==========================================
m3_riesgos, m3_mfe_datos = [], []

for (year, week), group in df_d.groupby(['Year', 'Week']):
    if len(group) < 3: continue
    group = group.sort_index()
    
    high_d1, low_d1 = float(group['High'].iloc[0]), float(group['Low'].iloc[0])
    m3_riesgos.append(((high_d1 - low_d1) / low_d1) * 100)
    
    resto_semana = group.iloc[1:]
    if resto_semana.empty: continue
    
    max_post, min_post = float(resto_semana['High'].max()), float(resto_semana['Low'].min())
    
    exp_neta = 0.0
    if max_post > high_d1: exp_neta = max(exp_neta, ((max_post - high_d1) / high_d1) * 100)
    if min_post < low_d1:  exp_neta = max(exp_neta, ((low_d1 - min_post) / low_d1) * 100)
    
    if exp_neta > 0.5: 
        m3_mfe_datos.append({'Fecha': group.index[-1], 'Expansion': exp_neta})

df_mfe = pd.DataFrame(m3_mfe_datos).set_index('Fecha')
df_mfe['P50_Rodante'] = df_mfe['Expansion'].rolling(window=26).quantile(0.50)
df_mfe['P75_Rodante'] = df_mfe['Expansion'].rolling(window=26).quantile(0.75)
df_mfe['Tendencia_MFE'] = df_mfe['P50_Rodante'].rolling(window=8).mean()

df_mfe_rodante = df_mfe.dropna(subset=['Tendencia_MFE'])
df_mfe_plot = df_mfe_rodante.iloc[-52:]

riesgo_mediano = pd.Series(m3_riesgos[-52:]).median()
tp1_p50 = df_mfe_plot['P50_Rodante'].iloc[-1]
tp2_p75 = df_mfe_plot['P75_Rodante'].iloc[-1]
mfe_trend = df_mfe_plot['Tendencia_MFE'].iloc[-1]

estado_mfe = "AMPLIÁNDOSE 🚀" if tp1_p50 > mfe_trend else "ACHICÁNDOSE ⚠️"

# ==========================================
# 🖨️ RENDERIZADO DEL REPORTE EJECUTIVO
# ==========================================
print("\n" + "="*60)
print(f" 📑 INFORME CUANTITATIVO SEMANAL - {ticker} ADR")
print("="*60)

print("\n🌍 1. CONTEXTO MACRO (Últimas 52 Semanas)")
print("-" * 60)
print(f"Régimen Actual:       {m1_estado}")
print(f"Amplitud Mediana:     {m1_p50:.2f}% por semana")
print(f"Tendencia (SMA 4w):   {m1_tendencia:.2f}%")

print("\n🔮 2. SESGO DIRECCIONAL (Inercia del Día 1)")
print("-" * 60)
print(f"Dirección Marcada:    {sesgo_actual}")
print(f"Hit Rate Base 1 Año:  {hit_rate_gral:.1f}% de confiabilidad")
print(f"Prob. Específica:     {prob_acierto:.1f}% (Basado en Día 1 {sesgo_actual.split()[0]})")

print("\n🎯 3. HOJA DE RUTA OPERATIVA (Riesgo / Beneficio)")
print("-" * 60)
print(f"Stop Loss Estructural:{riesgo_mediano:.2f}% (Piso/Techo Mediano de la Caja)")
print(f"Target 1 (TP1 - P50): {tp1_p50:.2f}% limpio desde quiebre")
print(f"Target 2 (TP2 - P75): {tp2_p75:.2f}% limpio desde quiebre")
print(f"Momento MFE:          {estado_mfe}")

print("\n" + "="*60)
print(" 🧠 CONCLUSIONES Y LECTURA OPERATIVA")
print("="*60)
if m1_p50 > m1_tendencia:
    print(f"[*] VOLATILIDAD: Mercado despertando. Comprar opciones outright o armar Spreads direccionales agresivos tiene ventaja matemática.")
else:
    print(f"[*] VOLATILIDAD: Entorno contractivo. El factor Theta castiga. Priorizar armado de Spreads ajustados o estrategias de cobro.")

print(f"[*] DIRECCIÓN: El flujo del Lunes dicta posicionamiento {sesgo_actual.split()[0]} con una ventaja del {prob_acierto:.1f}%.")
print(f"[*] ESTRUCTURACIÓN: Si operás Spreads (ej. Bull {sesgo_actual.split()[0]}), buscá que la base vendida caiga a {tp1_p50:.2f}% del precio de quiebre para asegurar el cobro en la zona de mayor confluencia estadística.")
print("="*60 + "\n")

# ==========================================
# 📊 RENDERIZADO VISUAL (DASHBOARD 2x2)
# ==========================================
plt.style.use('dark_background')
fig = plt.figure(figsize=(16, 10))
gs = gridspec.GridSpec(2, 2, height_ratios=[1, 1], wspace=0.2, hspace=0.3)
fig.suptitle(f'Dashboard Cuantitativo Semanal - {ticker} ADR (Últimas 52 Semanas)', fontsize=16, fontweight='bold', y=0.98)

# --- PANEL 1 ---
ax1 = plt.subplot(gs[0, 0])
ax1.plot(df_w_plot.index, df_w_plot['P50_Rodante'], color='yellow', linewidth=2.5, label='P50 (Mediana)')
ax1.plot(df_w_plot.index, df_w_plot['Tendencia_P50'], color='white', linestyle='--', linewidth=1.5, label='Tendencia (4w)')
ax1.fill_between(df_w_plot.index, df_w_plot['P50_Rodante'], df_w_plot['Tendencia_P50'], 
                 where=(df_w_plot['P50_Rodante'] >= df_w_plot['Tendencia_P50']), color='mediumseagreen', alpha=0.4, label='Expansión')
ax1.fill_between(df_w_plot.index, df_w_plot['P50_Rodante'], df_w_plot['Tendencia_P50'], 
                 where=(df_w_plot['P50_Rodante'] < df_w_plot['Tendencia_P50']), color='crimson', alpha=0.4, label='Contracción')
ax1.set_title('Régimen de Volatilidad (Módulo 1)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Spread (%)')
ax1.legend(loc='upper right', fontsize=9)
ax1.grid(True, linestyle=':', alpha=0.4)

# --- PANEL 2 ---
ax2 = plt.subplot(gs[0, 1])
ax2.plot(df_mfe_plot.index, df_mfe_plot['P75_Rodante'], color='orange', linewidth=1.5, label='TP2 (P75)')
ax2.plot(df_mfe_plot.index, df_mfe_plot['P50_Rodante'], color='yellow', linewidth=2.5, label='TP1 (P50)')
ax2.plot(df_mfe_plot.index, df_mfe_plot['Tendencia_MFE'], color='white', linestyle='--', linewidth=1.5, label='Tendencia MFE')
ax2.fill_between(df_mfe_plot.index, df_mfe_plot['P50_Rodante'], df_mfe_plot['Tendencia_MFE'], 
                 where=(df_mfe_plot['P50_Rodante'] >= df_mfe_plot['Tendencia_MFE']), color='mediumseagreen', alpha=0.4)
ax2.fill_between(df_mfe_plot.index, df_mfe_plot['P50_Rodante'], df_mfe_plot['Tendencia_MFE'], 
                 where=(df_mfe_plot['P50_Rodante'] < df_mfe_plot['Tendencia_MFE']), color='crimson', alpha=0.4)
ax2.set_title('Recorrido Neto Post-Quiebre (Módulo 3)', fontsize=12, fontweight='bold')
ax2.set_ylabel('Expansión Neta (%)')
ax2.legend(loc='upper right', fontsize=9)
ax2.grid(True, linestyle=':', alpha=0.4)

# --- PANEL 3 ---
ax3 = plt.subplot(gs[1, 0])
labels = [f'Predice Semana\n({hit_rate_gral:.1f}%)', f'Falso Quiebre\n({100-hit_rate_gral:.1f}%)']
sizes = [df_m2_ult_anio['Acierto'].sum(), len(df_m2_ult_anio) - df_m2_ult_anio['Acierto'].sum()]
colors = ['dodgerblue', 'crimson']
ax3.pie(sizes, explode=(0.05, 0), labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})
ax3.set_title(f'Poder Predictivo General (Día 1)', fontsize=12, fontweight='bold')

# --- PANEL 4 ---
ax4 = plt.subplot(gs[1, 1])
barras = ['Si Día 1 es VERDE', 'Si Día 1 es ROJO']
valores = [hr_verde, hr_rojo]
colores_barras = ['mediumseagreen', 'salmon']
ax4.bar(barras, valores, color=colores_barras, edgecolor='white', alpha=0.9, width=0.5)
ax4.axhline(y=50, color='white', linestyle='--', alpha=0.5)
for i, v in enumerate(valores):
    ax4.text(i, v + 2, f"{v:.1f}%", ha='center', fontweight='bold', fontsize=11)
ax4.set_title('Probabilidad de Acertar por Sesgo', fontsize=12, fontweight='bold')
ax4.set_ylabel('Probabilidad (%)')
ax4.set_ylim(0, 100)

plt.tight_layout()

# ==========================================
# 💾 EXPORTACIÓN GRÁFICA ESTÁTICA
# ==========================================
carpeta_actual = os.path.dirname(os.path.abspath(__file__))
nombre_archivo = os.path.join(carpeta_actual, f"GRAFICO_SEMANAL_{datetime.now().strftime('%H%M%S')}.png")

plt.savefig(nombre_archivo, dpi=100)
plt.close(fig) 
os.startfile(nombre_archivo)