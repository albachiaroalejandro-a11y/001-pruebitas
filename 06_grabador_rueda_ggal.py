import time
import re
import os
import sys
import json
import pandas as pd
import numpy as np
from matplotlib.pyplot import subplots
import matplotlib.pyplot as plt
from pyhomebroker import HomeBroker
from credenciales import DNI, BROKER_ID
import warnings

try:
    import winsound
except ImportError:
    pass

warnings.simplefilter(action='ignore', category=FutureWarning)

# ==========================================
# 🔐 SEGURIDAD: LECTURA DE SESIÓN
# ==========================================
USUARIO_SESION = os.environ.get('HB_USER')
PASSWORD_SESION = os.environ.get('HB_PASS')

if not USUARIO_SESION or not PASSWORD_SESION:
    print("❌ ALERTA DE SEGURIDAD: Credenciales no encontradas en la memoria.")
    print("Por favor, ejecutá este radar a través del 'Conserje' maestro.")
    sys.exit()

# ==========================================
# ⚙️ CONFIGURACIÓN DEL REGISTRO
# ==========================================
ARCHIVO_CSV = "registro_valuacion.csv"
INTERVALO_REGISTRO_SEGUNDOS = 10  
ultima_vez_registrado = 0

# ==========================================
# 🧠 CARGA DEL CEREBRO MATINAL (JSON)
# ==========================================
ruta_json = os.path.join(os.path.dirname(os.path.abspath(__file__)), "parametros_ggal.json")
try:
    with open(ruta_json, "r") as f:
        p_macro = json.load(f)
except Exception as e:
    print(f"⚠️ No se encontró el archivo JSON de calibración o hay un error: {e}")
    p_macro = None

# ==========================================
# 🛰️ VARIABLES GLOBALES
# ==========================================
df_opciones = pd.DataFrame()
precio_subyacente = 0.0
apertura_subyacente = 0.0
maximo_subyacente = 0.0
minimo_subyacente = 0.0

precio_adr = 0.0
ccl_implicito = 0.0
ultima_vez_adr = 0
INTERVALO_ADR = 60  

# ==========================================
# 🔊 MOTORES DE AUDIO
# ==========================================
def sonar_ratio(estado):
    """Emite sonidos distintos según la valuación del spread"""
    try:
        if estado == "BARATO": winsound.Beep(2000, 100) # Oportunidad aguda
    except: pass

def check_and_alert(target, dist, nivel_nombre):
    """Verifica rupturas y emite alertas sonoras"""
    if dist >= target:
        try:
            if "P75" in nivel_nombre: winsound.Beep(2500, 300) 
            elif "P50" in nivel_nombre: winsound.Beep(1500, 200)
            elif "P25" in nivel_nombre: winsound.Beep(1000, 100) 
            elif "Caja" in nivel_nombre: winsound.Beep(800, 400) 
        except: pass
        return "✅ ALCANZADO"
    return f"Falta {target - dist:.2f}%"

# ==========================================
# 🛠️ CALLBACKS DEL BROKER
# ==========================================
def on_options(online, quotes):
    global df_opciones
    thisData = quotes.copy()
    if df_opciones.empty:
        df_opciones = thisData
    else:
        df_opciones.update(thisData)

def on_securities(online, quotes):
    global precio_subyacente, apertura_subyacente, maximo_subyacente, minimo_subyacente
    df = quotes.copy()
    if not df.empty:
        df = df.reset_index()
        c_sym = next((c for c in df.columns if c.lower() in ['symbol', 'ticker', 'index']), 'symbol')
        c_last = next((c for c in df.columns if c.lower() in ['last', 'ultimo', 'close']), 'last')
        c_open = next((c for c in df.columns if c.lower() in ['open', 'apertura']), 'open')
        c_high = next((c for c in df.columns if c.lower() in ['high', 'maximo']), 'high')
        c_low = next((c for c in df.columns if c.lower() in ['low', 'minimo']), 'low')
        
        if c_sym in df.columns and c_last in df.columns:
            ggal_data = df[df[c_sym] == 'GGAL']
            if not ggal_data.empty:
                precio_subyacente = float(ggal_data[c_last].iloc[-1])
                
                if c_open in ggal_data.columns:
                    apertura_subyacente = float(ggal_data[c_open].iloc[-1])
                
                if c_high in ggal_data.columns and not pd.isna(ggal_data[c_high].iloc[-1]):
                    maximo_subyacente = float(ggal_data[c_high].iloc[-1])
                elif precio_subyacente > maximo_subyacente:
                    maximo_subyacente = precio_subyacente
                    
                if c_low in ggal_data.columns and not pd.isna(ggal_data[c_low].iloc[-1]):
                    minimo_subyacente = float(ggal_data[c_low].iloc[-1])
                elif minimo_subyacente == 0 or precio_subyacente < minimo_subyacente:
                    minimo_subyacente = precio_subyacente

# ==========================================
# 🧠 MOTOR DE VALUACIÓN DE SPREADS
# ==========================================
def procesar_spreads(res_df, tipo_opcion):
    ratios_temp, x_regresion_temp, strikes_referencia = [], [], []
    
    for i in range(len(res_df) - 1):
        b_baja, b_alta = res_df.iloc[i], res_df.iloc[i+1]
        dist = b_alta['strike_val'] - b_baja['strike_val']
        
        if tipo_opcion == 'CALL':
            costo = b_baja['ask_val'] - b_alta['bid_val']
            if costo > 0 and dist > 0 and costo <= dist:
                ratios_temp.append(dist / costo)
                x_regresion_temp.append(b_baja['strike_val'] + costo)
                strikes_referencia.append(b_baja['strike_val'])
        else: # PUT
            costo = b_alta['ask_val'] - b_baja['bid_val']
            if costo > 0 and dist > 0 and costo <= dist:
                ratios_temp.append(dist / costo)
                x_regresion_temp.append(b_alta['strike_val'] - costo)
                strikes_referencia.append(b_alta['strike_val'])

    m, b = None, None
    if precio_subyacente > 0 and ratios_temp:
        if tipo_opcion == 'CALL':
            puntos_otm = [(x, y) for x, y, k in zip(x_regresion_temp, ratios_temp, strikes_referencia) if k > precio_subyacente][:6]
        else:
            puntos_otm = [(x, y) for x, y, k in zip(x_regresion_temp, ratios_temp, strikes_referencia) if k < precio_subyacente][-6:]
            
        if len(puntos_otm) >= 2:
            x_m = np.array([p[0] for p in puntos_otm])
            y_m = np.array([p[1] for p in puntos_otm])
            m, b = np.polyfit(x_m, np.log(y_m), 1)

    ratios_armado, ratios_desarme, eje_x_strikes, eje_x_breakevens, tabla = [], [], [], [], []
    
    for i in range(len(res_df) - 1):
        b_baja, b_alta = res_df.iloc[i], res_df.iloc[i+1]
        distancia = b_alta['strike_val'] - b_baja['strike_val']
        
        s_bajo = str(int(b_baja['strike_val'] // 100))
        s_alto = str(int(b_alta['strike_val'] // 100))
        par_nombre = f"{s_bajo}/{s_alto}"
        
        if tipo_opcion == 'CALL':
            costo_real = b_baja['ask_val'] - b_alta['bid_val']
            valor_desarme = b_baja['bid_val'] - b_alta['ask_val']
            punto_equilibrio = b_baja['strike_val'] + costo_real
            strike_grafico = b_baja['strike_val']
            ask_e, bid_e = b_baja['ask_val'], b_alta['bid_val']
        else: # PUT
            costo_real = b_alta['ask_val'] - b_baja['bid_val']
            valor_desarme = b_alta['bid_val'] - b_baja['ask_val']
            punto_equilibrio = b_alta['strike_val'] - costo_real
            strike_grafico = b_alta['strike_val']
            ask_e, bid_e = b_alta['ask_val'], b_baja['bid_val']

        if costo_real > 0 and distancia > 0 and costo_real <= distancia:
            ratio_armado = distancia / costo_real
            ratios_armado.append(ratio_armado)
            eje_x_strikes.append(strike_grafico)
            
            if valor_desarme > 0 and valor_desarme <= distancia:
                ratios_desarme.append(distancia / valor_desarme)
            else:
                ratios_desarme.append(np.nan)
                
            eje_x_breakevens.append(punto_equilibrio)
            
            if m is not None:
                ratio_teorico = np.exp(m * punto_equilibrio + b)
                costo_teorico = distancia / ratio_teorico
                desvio_pesos = costo_real - costo_teorico
                condicion = "CARO" if desvio_pesos > 0 else "BARATO"
                
                tabla.append({
                    'TIPO': tipo_opcion, 'PAR': par_nombre, 'ASK_ENTRA': ask_e,
                    'BID_ENTRA': bid_e, 'C_REAL': costo_real, 'C_TEORICO': costo_teorico,
                    'DIF_PESOS': desvio_pesos, 'ESTADO': condicion
                })
                
    return tabla, ratios_armado, ratios_desarme, eje_x_strikes, eje_x_breakevens, m, b

# ==========================================
# 🚀 CONEXIÓN Y BUCLE PRINCIPAL
# ==========================================
hb = HomeBroker(BROKER_ID, on_options=on_options, on_securities=on_securities)

plt.ion() 
fig, (ax_puts, ax_calls) = plt.subplots(1, 2, figsize=(16, 6), sharey=True)

try:
    hb.auth.login(dni=DNI, user=USUARIO_SESION, password=PASSWORD_SESION)
    print("\n🔌 Conectando al motor de eventos...")
    hb.online.connect()
    time.sleep(2)
    
    with open("bases.txt", "r") as f:
        monitor = [str(line).strip().upper() for line in f if line.strip()]

    hb.online.subscribe_options()
    hb.online.subscribe_securities('bluechips', '24hs')

    print(f"\n🚀 Sistema de Valuación Dual (Calls/Puts) Iniciado...")

    while True:
        ahora = time.time()

        if not df_opciones.empty:
            df = df_opciones.reset_index()
            cols = df.columns
            
            c_sym = next((c for c in cols if c.lower() in ['symbol', 'ticker', 'index']), 'symbol')
            c_bid = next((c for c in cols if c.lower() in ['bid', 'compra']), 'bid')
            c_ask = next((c for c in cols if c.lower() in ['ask', 'venta']), 'ask')

            res = df[df[c_sym].isin(monitor)].copy()

            if not res.empty:
                res['bid_val'] = pd.to_numeric(res[c_bid], errors='coerce').fillna(0)
                res['ask_val'] = pd.to_numeric(res[c_ask], errors='coerce').fillna(0)
                
                res['strike_val'] = res[c_sym].apply(lambda x: float(re.findall(r'\d+', x)[0]) if re.findall(r'\d+', x) else 0)
                res['strike_val'] = res['strike_val'].apply(lambda x: x / 10 if x > 20000 else x)
                
                res_calls = res[res[c_sym].str.contains(r'C\d+')].sort_values('strike_val').reset_index(drop=True)
                res_puts  = res[res[c_sym].str.contains(r'V\d+')].sort_values('strike_val').reset_index(drop=True)
                
                tabla_C, r_arm_C, r_des_C, x_str_C, x_be_C, m_C, b_C = procesar_spreads(res_calls, 'CALL')
                tabla_P, r_arm_P, r_des_P, x_str_P, x_be_P, m_P, b_P = procesar_spreads(res_puts, 'PUT')
                
                tabla_completa = tabla_C + tabla_P

                if tabla_completa:
                    print("\033[H\033[J", end="") 
                    
                    # 1. ACTUALIZACIÓN DEL ADR Y CCL
                    if ahora - ultima_vez_adr >= INTERVALO_ADR:
                        try:
                            df_adr = yf.download("GGAL", period="1d", interval="1m", progress=False)
                            if not df_adr.empty:
                                if isinstance(df_adr.columns, pd.MultiIndex):
                                    df_adr.columns = df_adr.columns.get_level_values(0)
                                precio_adr = float(df_adr['Close'].iloc[-1])
                        except Exception: pass
                        ultima_vez_adr = ahora

                    if precio_adr > 0 and precio_subyacente > 0:
                        ccl_implicito = (precio_subyacente * 10) / precio_adr

                    # EL NUEVO PANEL SUPERIOR
                    print("="*105)
                    print(f" 📊 PANEL DUAL QUANT GGAL | Spot Local: ${precio_subyacente:.2f} | Spot ADR: U$S {precio_adr:.2f} | CCL: ${ccl_implicito:.2f}")
                    print("="*105)
                    
                    # 2. INYECCIÓN DEL ARCHIVO JSON Y MAPA DE PRECIOS
                    if p_macro and minimo_subyacente > 0 and maximo_subyacente > 0:
                        try:
                            c_15, c_30 = p_macro['CAJAS_INTRADIA']['15M'], p_macro['CAJAS_INTRADIA']['30M']
                            c_45, c_60 = p_macro['CAJAS_INTRADIA']['45M'], p_macro['CAJAS_INTRADIA']['60M']
                            
                            t_p25 = float(str(p_macro['TARGETS_INTRADIA']['P25']).replace('np.float64(','').replace(')',''))
                            t_p50 = float(str(p_macro['TARGETS_INTRADIA']['P50']).replace('np.float64(','').replace(')',''))
                            t_p75 = float(str(p_macro['TARGETS_INTRADIA']['P75']).replace('np.float64(','').replace(')',''))

                            dist_up = ((precio_subyacente - minimo_subyacente) / minimo_subyacente) * 100 
                            dist_down = ((maximo_subyacente - precio_subyacente) / maximo_subyacente) * 100 
                            
                            ps_75, ps_50, ps_25 = minimo_subyacente * (1 + t_p75/100), minimo_subyacente * (1 + t_p50/100), minimo_subyacente * (1 + t_p25/100)
                            pi_75, pi_50, pi_25 = maximo_subyacente * (1 - t_p75/100), maximo_subyacente * (1 - t_p50/100), maximo_subyacente * (1 - t_p25/100)
                            
                            op = apertura_subyacente
                            cs_15, cs_30, cs_45, cs_60 = op*(1+c_15/100), op*(1+c_30/100), op*(1+c_45/100), op*(1+c_60/100)
                            ci_15, ci_30, ci_45, ci_60 = op*(1-c_15/100), op*(1-c_30/100), op*(1-c_45/100), op*(1-c_60/100)

                            dist_apertura_up = ((precio_subyacente - op) / op) * 100 if precio_subyacente >= op else 0
                            dist_apertura_down = ((op - precio_subyacente) / op) * 100 if precio_subyacente < op else 0
                            
                            if dist_apertura_up >= c_60 or dist_apertura_down >= c_60:
                                check_and_alert(c_60, max(dist_apertura_up, dist_apertura_down), "Caja")

                            print(f" Proy. Sup. P75: ${ps_75:>8.2f} | {check_and_alert(t_p75, dist_up, 'Sup P75'):<13} |")
                            print(f" Proy. Sup. P50: ${ps_50:>8.2f} | {check_and_alert(t_p50, dist_up, 'Sup P50'):<13} |")
                            print(f" Proy. Sup. P25: ${ps_25:>8.2f} | {check_and_alert(t_p25, dist_up, 'Sup P25'):<13} |")
                            print("")
                            print(f" Sup                    ${cs_15:>8.2f} | ${cs_30:>8.2f} | ${cs_45:>8.2f} | ${cs_60:>8.2f} |")
                            print(f" Temporalidad de caja:     15m     |    30m     |    45m     |    60m     |")
                            print(f" Inf                    ${ci_15:>8.2f} | ${ci_30:>8.2f} | ${ci_45:>8.2f} | ${ci_60:>8.2f} |")
                            print("")
                            print(f" Proy. Inf. P25: ${pi_25:>8.2f} | {check_and_alert(t_p25, dist_down, 'Inf P25'):<13} |")
                            print(f" Proy. Inf. P50: ${pi_50:>8.2f} | {check_and_alert(t_p50, dist_down, 'Inf P50'):<13} |")
                            print(f" Proy. Inf. P75: ${pi_75:>8.2f} | {check_and_alert(t_p75, dist_down, 'Inf P75'):<13} |")
                            print("="*105)

                        except Exception as e:
                            print(f" ⚠️ Error en cálculos de proyección: {e}")

                    # 3. RENDERIZADO DE TABLA LADO A LADO (HUD)
                    df_C = pd.DataFrame(tabla_C) if tabla_C else pd.DataFrame(columns=['PAR', 'ASK_ENTRA', 'BID_ENTRA', 'C_REAL', 'C_TEORICO', 'DIF_PESOS', 'ESTADO'])
                    df_P = pd.DataFrame(tabla_P) if tabla_P else pd.DataFrame(columns=['PAR', 'ASK_ENTRA', 'BID_ENTRA', 'C_REAL', 'C_TEORICO', 'DIF_PESOS', 'ESTADO'])

                    umb = -5.0 
                    if not df_C.empty and df_C['DIF_PESOS'].min() < umb: sonar_ratio("BARATO")
                    if not df_P.empty and df_P['DIF_PESOS'].min() < umb: sonar_ratio("BARATO")

                    if not df_C.empty: df_C['ESTADO'] = df_C['ESTADO'].apply(lambda x: "🔴" if x == "CARO" else "🟢")
                    if not df_P.empty: df_P['ESTADO'] = df_P['ESTADO'].apply(lambda x: "🔴" if x == "CARO" else "🟢")

                    df_merged = pd.merge(df_C, df_P, on='PAR', how='outer', suffixes=('_C', '_P'))
                    df_merged['strike_sort'] = df_merged['PAR'].apply(lambda x: float(x.split('/')[0]))
                    df_merged = df_merged.sort_values('strike_sort').drop('strike_sort', axis=1)

                    df_final = pd.DataFrame()
                    df_final['PAR']    = df_merged['PAR']
                    df_final['A_CALL'] = df_merged['ASK_ENTRA_C']
                    df_final['B_CALL'] = df_merged['BID_ENTRA_C']
                    df_final['R_CALL'] = df_merged['C_REAL_C']
                    df_final['T_CALL'] = df_merged['C_TEORICO_C']
                    df_final['DIF_C']  = df_merged['DIF_PESOS_C']
                    df_final['E_C']    = df_merged['ESTADO_C'].fillna(" ")
                    df_final['|']      = '|'
                    df_final['A_PUT']  = df_merged['ASK_ENTRA_P']
                    df_final['B_PUT']  = df_merged['BID_ENTRA_P']
                    df_final['R_PUT']  = df_merged['C_REAL_P']
                    df_final['T_PUT']  = df_merged['C_TEORICO_P']
                    df_final['DIF_P']  = df_merged['DIF_PESOS_P']
                    df_final['E_P']    = df_merged['ESTADO_P'].fillna(" ")

                    formato_nums = lambda x: f"{x:>7.2f}" if pd.notnull(x) else "   --- "
                    formatters = {col: formato_nums for col in ['A_CALL', 'B_CALL', 'R_CALL', 'T_CALL', 'DIF_C', 'A_PUT', 'B_PUT', 'R_PUT', 'T_PUT', 'DIF_P']}
                    
                    print(df_final.to_string(index=False, formatters=formatters))
                    print("="*105)

                    if ahora - ultima_vez_registrado >= INTERVALO_REGISTRO_SEGUNDOS:
                        df_log = pd.DataFrame(tabla_completa)
                        if not df_log.empty:
                            df_log.insert(0, 'Fecha_Hora', time.strftime('%Y-%m-%d %H:%M:%S'))
                            df_log.insert(1, 'Subyacente', precio_subyacente)
                            df_log.to_csv(ARCHIVO_CSV, mode='a', header=not os.path.exists(ARCHIVO_CSV), index=False)
                        ultima_vez_registrado = ahora

                # --- ACTUALIZACIÓN GRÁFICA DUAL ---
                ax_puts.clear()
                ax_calls.clear()
                
                if r_arm_P:
                    ax_puts.plot(x_str_P, r_des_P, marker='v', linestyle=':', color='crimson', linewidth=1.5, alpha=0.7)
                    ax_puts.plot(x_str_P, r_arm_P, marker='o', linestyle='-', color='dodgerblue', linewidth=2)
                    if m_P is not None:
                        x_teo_be_P = np.array(x_be_P)
                        y_teo_P = np.exp(m_P * x_teo_be_P + b_P)
                        ax_puts.plot(x_teo_be_P, y_teo_P, color='orange', marker='x', linestyle='--', linewidth=2)
                    ax_puts.axvline(x=precio_subyacente, color='mediumseagreen', linestyle='-', linewidth=2, label=f'Spot: {precio_subyacente:.2f}')
                    ax_puts.set_title("BEAR PUTS", fontsize=12, fontweight='bold')
                    ax_puts.set_ylabel("Múltiplo de Retorno (Log)")
                    ax_puts.set_xticks(x_str_P)
                    ax_puts.set_xticklabels([t['PAR'] for t in tabla_P], rotation=45, ha='right', fontsize=8)
                    ax_puts.grid(True, which="both", ls="--", alpha=0.5)

                if r_arm_C:
                    ax_calls.plot(x_str_C, r_des_C, marker='v', linestyle=':', color='crimson', linewidth=1.5, alpha=0.7, label='Salida')
                    ax_calls.plot(x_str_C, r_arm_C, marker='o', linestyle='-', color='dodgerblue', linewidth=2, label='Armado')
                    if m_C is not None:
                        x_teo_be_C = np.array(x_be_C)
                        y_teo_C = np.exp(m_C * x_teo_be_C + b_C)
                        ax_calls.plot(x_teo_be_C, y_teo_C, color='orange', marker='x', linestyle='--', linewidth=2, label='Teórico (BE)')
                    ax_calls.axvline(x=precio_subyacente, color='mediumseagreen', linestyle='-', linewidth=2, label=f'Spot: {precio_subyacente:.2f}')
                    ax_calls.set_title("BULL CALLS", fontsize=12, fontweight='bold')
                    ax_calls.set_xticks(x_str_C)
                    ax_calls.set_xticklabels([t['PAR'] for t in tabla_C], rotation=45, ha='right', fontsize=8)
                    ax_calls.grid(True, which="both", ls="--", alpha=0.5)
                    ax_calls.legend(loc='upper right', fontsize=8)
                
                ax_puts.set_yscale('log')
                ax_calls.set_yscale('log')
                fig.suptitle(f"Radiografía de Liquidez - GGAL ADR", fontsize=14, fontweight='bold')
                fig.tight_layout()

        fig.canvas.draw()
        fig.canvas.flush_events()
        time.sleep(1)

except KeyboardInterrupt:
    print("\n🛑 Deteniendo radar...")
except Exception as e:
    print(f"❌ Error en ejecución: {e}")
finally:
    try:
        hb.online.disconnect()
    except:
        pass
    plt.ioff()
    plt.show()
    print("\n🔌 Desconectado.")