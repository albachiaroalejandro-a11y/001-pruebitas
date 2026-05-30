import pandas as pd
import yfinance as yf
import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint
from itertools import combinations
import matplotlib.pyplot as plt
import os
import json
import sys  # <--- MAGIA PARA RECIBIR ÓRDENES DEL CONSERJE
from datetime import datetime
import warnings

warnings.simplefilter(action='ignore')

try:
    from universo import universo, tickers
except ImportError:
    print("❌ Error: No se encontró 'universo.py'.")
    sys.exit()

def calcular_hurst(ts):
    try:
        lags = range(2, 20)
        tau = [np.sqrt(np.std(np.subtract(ts[lag:], ts[:-lag]))) for lag in lags]
        poly = np.polyfit(np.log(lags), np.log(tau), 1)
        return poly[0]*2.0
    except:
        return np.nan

# ==========================================
# 🎛️ CAPTURA DE ÓRDENES (CLI vs MANUAL)
# ==========================================
modo = None
exportar_auto = False

# Si el Conserje nos mandó argumentos (ej: python 04_master_screeners.py 1 auto)
if len(sys.argv) > 1:
    modo = sys.argv[1].strip()
    if len(sys.argv) > 2 and sys.argv[2].strip().lower() == 'auto':
        exportar_auto = True
    print(f"\n🤖 [MODO AUTÓNOMO] Ejecutando orden del Conserje: Modo {modo}")
else:
    # Modo Manual (humano)
    print("\n" + "="*60)
    print(" 🎛️ MASTER SCREENER QUANT")
    print("="*60)
    print(" ¿Qué necesitás buscar hoy?")
    print("  [1] 🏗️ CONSTRUCTOR CORE-SATELLITE (Top 2 Satélites ÚNICOS por Core)")
    print("  [2] 🎯 ESCÁNER TÁCTICO (Oportunidades de Entrada HOY con gráficos)")
    print("="*60)
    modo = input("👉 Su orden (1 o 2): ").strip()

# ==========================================
# 📥 DESCARGA GLOBAL DE DATOS
# ==========================================
print(f"\n📥 Descargando historia de 3 años para {len(tickers)} activos...")
df_raw = yf.download(tickers, period="3y", progress=False)

if isinstance(df_raw.columns, pd.MultiIndex):
    nivel_cero = df_raw.columns.get_level_values(0)
    nivel_uno = df_raw.columns.get_level_values(1)
    if 'Close' in nivel_cero: df = df_raw['Close']
    elif 'Close' in nivel_uno: df = df_raw.xs('Close', level=1, axis=1)
    else: df = df_raw.xs('Adj Close', level=1, axis=1) if 'Adj Close' in nivel_uno else df_raw
else:
    df = df_raw

df = df.dropna(axis=1, how='all')

if modo == '1':
    categorias = {
        "🛡️ DIVIDENDOS (Consumo/Defensivas)": {
            "anclas": ["PEP", "PG", "COST"],
            "p_value_max": 0.20,
            "hurst_max": 0.55,
            "ventanas": range(30, 70, 5),
            "umbrales": [1.5, 1.6, 1.7]
        },
        "🚀 GROWTH (Tecnología/Volatilidad)": {
            "anclas": ["SE", "NOK", "INTC"],
            "p_value_max": 0.10,
            "hurst_max": 0.45,
            "ventanas": range(15, 50, 5),
            "umbrales": [1.5, 1.8, 2.0]
        },
        "⚓ COBERTURA (Metales/Agro/Macro)": {
            "anclas": ["DE", "BRK-B", "RIO"],
            "p_value_max": 0.15,
            "hurst_max": 0.50,
            "ventanas": range(20, 60, 5),
            "umbrales": [1.5, 1.6, 1.8]
        }
    }

    resultados = []
    print("\n🚀 Iniciando optimización sectorial (Fuerza Bruta)...")

    for nombre_cat, config in categorias.items():
        print(f"Buscando para: {nombre_cat}...")
        for ancla in config["anclas"]:
            etiquetas_ancla = universo[ancla]
            candidatos = [t for t in tickers if not universo[t].isdisjoint(etiquetas_ancla)]
            
            for satelite in candidatos:
                if ancla == satelite: continue
                if ancla not in df.columns or satelite not in df.columns: continue
                
                df_par = df[[ancla, satelite]].dropna()
                if len(df_par) < 150: continue 
                
                s1, s2 = df_par[ancla], df_par[satelite]
                ratio = s1 / s2
                
                _, p_value, _ = coint(s1, s2)
                hurst = calcular_hurst(ratio.values)
                
                if p_value < config["p_value_max"] and hurst < config["hurst_max"]: 
                    for v in config["ventanas"]:
                        for u in config["umbrales"]:
                            media = ratio.rolling(window=v).mean()
                            std = ratio.rolling(window=v).std()
                            z_score = (ratio - media) / std
                            entradas = (z_score > u) | (z_score < -u)
                            num_entradas = entradas.sum()
                            if num_entradas > 15:
                                resultados.append({
                                    'Categoria': nombre_cat.split(" ")[1],
                                    'Ancla': ancla,
                                    'Par': f"{ancla}/{satelite}", 
                                    'Ventana': v, 'Umbral': u, 'Entradas': num_entradas
                                })

    df_resultados = pd.DataFrame(resultados)
    print("\n" + "="*60)
    print(" 🏆 RESULTADOS CORE-SATELLITE (TOP 2 SATÉLITES POR ANCLA)")
    print("="*60)

    top_final_para_exportar = pd.DataFrame()

    for nombre_cat in categorias.keys():
        nombre_corto = nombre_cat.split(" ")[1]
        print(f"\n{nombre_cat}")
        print("-" * 50)
        
        if not df_resultados.empty:
            df_cat = df_resultados[df_resultados['Categoria'] == nombre_corto]
            if not df_cat.empty:
                df_ordenado = df_cat.sort_values(by='Entradas', ascending=False)
                df_unicos = df_ordenado.drop_duplicates(subset=['Par'], keep='first')
                top_por_ancla = df_unicos.groupby('Ancla').head(2)
                top_final = top_por_ancla.sort_values(by=['Ancla', 'Entradas'], ascending=[True, False])
                print(top_final[['Par', 'Ventana', 'Umbral', 'Entradas']].to_string(index=False))
                top_final_para_exportar = pd.concat([top_final_para_exportar, top_final])
            else:
                print("  ⚠️ Ningún par superó los filtros para esta categoría.")
        else:
            print("  ⚠️ Ningún par superó los filtros.")
            
    # --- AUTOMATIZACIÓN DE WATCHLIST ---
    if not top_final_para_exportar.empty:
        if exportar_auto:
            exportar = 's'
        else:
            exportar = input("\n👉 ¿Querés sobrescribir 'watchlist_ideal.json' con estos pares? (s/n): ").strip().lower()
            
        if exportar == 's':
            nueva_watchlist = []
            for index, row in top_final_para_exportar.iterrows():
                t1, t2 = row['Par'].split('/')
                nueva_watchlist.append({
                    "t1": t1, "t2": t2,
                    "ventana": int(row['Ventana']), "umbral": float(row['Umbral'])
                })
            ruta_watchlist = os.path.join(os.path.dirname(os.path.abspath(__file__)), "watchlist_ideal.json")
            with open(ruta_watchlist, 'w') as f:
                json.dump(nueva_watchlist, f, indent=4)
            print(f"\n✅ ¡Éxito! Watchlist actualizada con {len(nueva_watchlist)} pares.")

elif modo == '2':
    opcion_hl = None
    if len(sys.argv) > 2:
        opcion_hl = sys.argv[2].strip()
    else:
        print("\nSeleccioná el nivel de exigencia (Half-Life máximo):")
        print("  [1] MODO FERRARI (Máx 15 días)")
        print("  [2] MODO NORMAL (Máx 25 días)")
        opcion_hl = input("👉 Opcion: ").strip()
        
    MAX_HALF_LIFE = 15 if opcion_hl == '1' else 25

    VENTANA_MEDIA, DESVIACIONES_BANDA, UMBRAL_ENTRADA = 30, 1.5, 1.5      
    pares_validos = []
    for t1, t2 in combinations(tickers, 2):
        etiquetas_comunes = universo[t1].intersection(universo[t2])
        if len(etiquetas_comunes) > 0:
            pares_validos.append((t1, t2, ", ".join(etiquetas_comunes)))

    print(f"\n⚙️ Analizando Cointegración y Half-Life en {len(pares_validos)} cruces posibles...")
    graficos_a_dibujar = []

    for t1, t2, nexo in pares_validos:
        if t1 not in df.columns or t2 not in df.columns: continue
        df_par = df[[t1, t2]].dropna()
        if len(df_par) < 200: continue
            
        s1, s2 = df_par[t1], df_par[t2]
        try:
            _, p_value, _ = coint(s1, s2)
            if p_value > 0.05: continue
            ratio = s1 / s2
            y_hl = ratio.diff().dropna()
            x_hl = ratio.shift(1).dropna()
            if len(y_hl) < 50: continue
            res = sm.OLS(y_hl, sm.add_constant(x_hl)).fit()
            beta = res.params.iloc[1]
            hl = -np.log(2) / beta if beta < 0 else np.nan
            if pd.isna(hl) or hl > MAX_HALF_LIFE: continue
            hurst = calcular_hurst(ratio.values)
            if pd.isna(hurst): continue
                
            media = ratio.rolling(window=VENTANA_MEDIA).mean()
            desviacion = ratio.rolling(window=VENTANA_MEDIA).std()
            z_score_hist = (ratio - media) / desviacion
            z_actual = z_score_hist.iloc[-1]
            
            if abs(z_actual) >= UMBRAL_ENTRADA:
                banda_sup = media + (desviacion * DESVIACIONES_BANDA)
                banda_inf = media - (desviacion * DESVIACIONES_BANDA)
                estado = f"VENDER {t1} / COMPRAR {t2} 🔴" if z_actual >= UMBRAL_ENTRADA else f"COMPRAR {t1} / VENDER {t2} 🟢"
                graficos_a_dibujar.append({
                    't1': t1, 't2': t2, 'nexo': nexo, 'hl': hl, 'z_actual': z_actual, 'estado': estado, 
                    'ratio': ratio, 'media': media, 'banda_sup': banda_sup, 'banda_inf': banda_inf
                })
        except: continue

    if not graficos_a_dibujar:
        print(f"\nℹ️ Hoy ningún par está dando señal de entrada con Half-Life menor a {MAX_HALF_LIFE} días.")
    else:
        graficos_a_dibujar = sorted(graficos_a_dibujar, key=lambda x: abs(x['z_actual']), reverse=True)
        print("\n" + "="*85)
        print(f" 🚀 RADAR QUANT TÁCTICO: {len(graficos_a_dibujar)} SEÑALES ACTIVAS HOY")
        print("="*85)
        for g in graficos_a_dibujar:
            print(f"🔹 [{g['t1']} vs {g['t2']}] | Nexo: {g['nexo']}")
            print(f"   ➔ Señal: {g['estado']} (Z-Score: {g['z_actual']:.2f})")
        
        plt.style.use('dark_background')
        fig, axes = plt.subplots(len(graficos_a_dibujar), 1, figsize=(14, 5 * len(graficos_a_dibujar)), sharex=False)
        if len(graficos_a_dibujar) == 1: axes = [axes]
            
        for idx, data in enumerate(graficos_a_dibujar):
            ax = axes[idx]
            fechas_plot = data['ratio'].index[-250:]
            ax.plot(fechas_plot, data['ratio'][-250:], color='dodgerblue', linewidth=2, label='Ratio Real')
            ax.plot(fechas_plot, data['media'][-250:], color='white', linestyle='--', linewidth=1.5, label='Media')
            ax.plot(fechas_plot, data['banda_sup'][-250:], color='crimson', linestyle=':', alpha=0.7)
            ax.plot(fechas_plot, data['banda_inf'][-250:], color='mediumseagreen', linestyle=':', alpha=0.7)
            ax.fill_between(fechas_plot, data['banda_sup'][-250:], data['banda_inf'][-250:], color='gray', alpha=0.1)
            
            color_senial = 'red' if data['z_actual'] > 0 else 'lime'
            ax.plot(fechas_plot[-1], data['ratio'].iloc[-1], color=color_senial, marker='o', markersize=8)

            titulo = f"[{data['t1']} / {data['t2']}] Z: {data['z_actual']:.2f} | HL: {data['hl']:.1f}d | Señal: {data['estado']}"
            ax.set_title(titulo, fontweight='bold', fontsize=11)
            ax.grid(True, linestyle=':', alpha=0.3)
            ax.legend(loc='upper left', fontsize=9)

        plt.tight_layout()
        carpeta_actual = os.path.dirname(os.path.abspath(__file__))
        nombre_archivo = os.path.join(carpeta_actual, f"GRAFICO_TACTICO_{datetime.now().strftime('%H%M%S')}.png")
        plt.savefig(nombre_archivo, dpi=100)
        plt.close(fig) 
        os.startfile(nombre_archivo)
else:
    print("⚠️ Opción no válida. Ejecutá el script de nuevo.")