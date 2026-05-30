import yfinance as yf
import pandas as pd
import json
import os
import warnings

warnings.simplefilter(action='ignore')

ticker = "GGAL"
print(f"⚙️ Iniciando Calibración Matinal para {ticker}...")
parametros = {}

# ==========================================
# 1. CALIBRACIÓN INTRADIARIA (Últimos 60 días para Cajas, 2 años para MFE)
# ==========================================
print("📥 Descargando data intradiaria (15m y 1h)...")
df_15m = yf.download(ticker, period="60d", interval="15m", progress=False)
df_1h = yf.download(ticker, period="730d", interval="1h", progress=False)

if isinstance(df_15m.columns, pd.MultiIndex):
    df_15m.columns = df_15m.columns.get_level_values(0)
    df_1h.columns = df_1h.columns.get_level_values(0)

# --- A. Cajas de 15, 30, 45 y 60m ---
df_15m.index = pd.to_datetime(df_15m.index)
df_15m['Date'] = df_15m.index.date
cajas_resultados = []

for date, group in df_15m.groupby('Date'):
    if len(group) < 4: continue
    high_15, low_15 = float(group['High'].iloc[0]), float(group['Low'].iloc[0])
    high_30, low_30 = float(group['High'].iloc[0:2].max()), float(group['Low'].iloc[0:2].min())
    high_45, low_45 = float(group['High'].iloc[0:3].max()), float(group['Low'].iloc[0:3].min())
    high_60, low_60 = float(group['High'].iloc[0:4].max()), float(group['Low'].iloc[0:4].min())
    
    cajas_resultados.append({
        '15m': ((high_15 - low_15) / low_15) * 100,
        '30m': ((high_30 - low_30) / low_30) * 100,
        '45m': ((high_45 - low_45) / low_45) * 100,
        '60m': ((high_60 - low_60) / low_60) * 100
    })

df_cajas = pd.DataFrame(cajas_resultados)
parametros['CAJAS_INTRADIA'] = {
    '15M': round(df_cajas['15m'].median(), 2),
    '30M': round(df_cajas['30m'].median(), 2),
    '45M': round(df_cajas['45m'].median(), 2),
    '60M': round(df_cajas['60m'].median(), 2)
}

# --- B. MFE Intradiario (Amplitud Total Diaria) ---
df_1h.index = pd.to_datetime(df_1h.index)
df_1h['Date'] = df_1h.index.date
mfe_intra = []

for date, group in df_1h.groupby('Date'):
    if len(group) < 3: continue
    
    h_dia = float(group['High'].max())
    l_dia = float(group['Low'].min())
    
    # Amplitud total del día respecto a su mínimo
    amp_total = ((h_dia - l_dia) / l_dia) * 100
    
    if amp_total > 0.1: 
        mfe_intra.append(amp_total)

df_mfe_intra = pd.Series(mfe_intra)
parametros['TARGETS_INTRADIA'] = {
    'P25': round(df_mfe_intra.quantile(0.25), 2),
    'P50': round(df_mfe_intra.quantile(0.50), 2),
    'P75': round(df_mfe_intra.quantile(0.75), 2)
}

# ==========================================
# 2. CALIBRACIÓN SEMANAL (Últimos 5 Años)
# ==========================================
print("📥 Descargando data diaria para MFE Semanal...")
df_d = yf.download(ticker, period="5y", interval="1d", progress=False)
if isinstance(df_d.columns, pd.MultiIndex): df_d.columns = df_d.columns.get_level_values(0)

df_d['Year'] = df_d.index.isocalendar().year
df_d['Week'] = df_d.index.isocalendar().week
mfe_sem = []
cajas_sem = []

for (year, week), group in df_d.groupby(['Year', 'Week']):
    if len(group) < 3: continue
    group = group.sort_index()
    
    high_d1, low_d1 = float(group['High'].iloc[0]), float(group['Low'].iloc[0])
    cajas_sem.append(((high_d1 - low_d1) / low_d1) * 100)
    
    resto_sem = group.iloc[1:]
    if resto_sem.empty: continue
    
    max_post, min_post = float(resto_sem['High'].max()), float(resto_sem['Low'].min())
    
    exp_neta = 0.0
    if max_post > high_d1: exp_neta = max(exp_neta, ((max_post - high_d1) / high_d1) * 100)
    if min_post < low_d1:  exp_neta = max(exp_neta, ((low_d1 - min_post) / low_d1) * 100)
    if exp_neta > 0.5: mfe_sem.append(exp_neta)

df_mfe_sem = pd.Series(mfe_sem)
parametros['CAJA_SEMANAL_DIA1'] = round(pd.Series(cajas_sem).median(), 2)
parametros['TARGETS_SEMANALES'] = {
    'P25': round(df_mfe_sem.quantile(0.25), 2),
    'P50': round(df_mfe_sem.quantile(0.50), 2),
    'P75': round(df_mfe_sem.quantile(0.75), 2)
}

# ==========================================
# 3. EXPORTACIÓN A JSON
# ==========================================
ruta_json = os.path.join(os.path.dirname(os.path.abspath(__file__)), "parametros_ggal.json")
with open(ruta_json, "w") as f:
    json.dump(parametros, f, indent=4)

print(f"✅ ¡Calibración exitosa! Parámetros guardados en: parametros_ggal.json")
for k, v in parametros.items():
    print(f"  - {k}: {v}")