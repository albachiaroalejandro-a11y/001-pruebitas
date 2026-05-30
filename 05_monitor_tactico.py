 import os
import json
import time
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
import winsound

warnings.simplefilter(action='ignore')

# ==========================================
# ⚙️ CONFIGURACIÓN DE RUTAS Y TIEMPOS
# ==========================================
CARPETA_ACTUAL = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_CARTERA = os.path.join(CARPETA_ACTUAL, "cartera_hoy.json")
ARCHIVO_WATCHLIST = os.path.join(CARPETA_ACTUAL, "watchlist_ideal.json")

# 1800 segundos = 30 minutos.
INTERVALO_CHEQUEO = 1800 

def cargar_json(ruta):
    if os.path.exists(ruta):
        try:
            with open(ruta, 'r') as f:
                return json.load(f)
        except Exception:
            return {} if "cartera" in ruta else []
    return {} if "cartera" in ruta else []

def inicializar_watchlist():
    if not os.path.exists(ARCHIVO_WATCHLIST):
        ejemplo = [
            {"t1": "PG", "t2": "CL", "ventana": 45, "umbral": 1.5},
            {"t1": "PEP", "t2": "IBM", "ventana": 40, "umbral": 1.5}
        ]
        with open(ARCHIVO_WATCHLIST, 'w') as f:
            json.dump(ejemplo, f, indent=4)
            
# ==========================================
# 🔊 MOTOR DE AUDIO (NUEVO)
# ==========================================
def sonar_alerta(tipo):
    """Emite una secuencia de bips según la importancia"""
    if tipo == 'COMPRAR':
        # Tono ascendente (Frecuencia, Duración ms)
        winsound.Beep(1500, 700)
        winsound.Beep(1500, 700)
        winsound.Beep(1500, 700)
        winsound.Beep(1500, 700)
    elif tipo == 'VENDER':
        # Tono descendente
        winsound.Beep(1000, 200)
        winsound.Beep(1000, 700)
        winsound.Beep(1000, 200)
        winsound.Beep(1000, 700)
        winsound.Beep(1000, 200)
    else:
        # Bip neutro para errores o avisos
        winsound.Beep(800, 200)

# ==========================================
# 📊 MOTOR GRÁFICO (GUARDA Y ABRE ALERTA)
# ==========================================
def plotear_alerta(t1, t2, datos, tipo_alerta, umbral):
    """Genera y guarda un gráfico estático de la alarma, y lo abre en el visor por defecto"""
    sonar_alerta(tipo_alerta)
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(12, 5))
    
    # Tomamos solo las últimas 150 ruedas para hacer un "zoom in" a la acción reciente
    fechas = datos['fechas'][-150:]
    ratio = datos['ratio'][-150:]
    media = datos['media'][-150:]
    
    # Calculamos las bandas exactas del umbral
    std = datos['std'][-150:]
    banda_sup = media + (std * umbral)
    banda_inf = media - (std * umbral)

    # Ploteo de líneas
    ax.plot(fechas, ratio, color='dodgerblue', linewidth=2, label=f'Ratio {t1}/{t2}')
    ax.plot(fechas, media, color='white', linestyle='--', linewidth=1.5, label=f'Media ({len(media)}D)')
    ax.plot(fechas, banda_sup, color='crimson', linestyle=':', alpha=0.7)
    ax.plot(fechas, banda_inf, color='mediumseagreen', linestyle=':', alpha=0.7)
    
    ax.fill_between(fechas, banda_sup, banda_inf, color='gray', alpha=0.1)

    # Resaltar el punto de ruptura (Hoy)
    color_punto = 'lime' if tipo_alerta == 'COMPRAR' else 'red'
    ax.plot(fechas[-1], ratio.iloc[-1], color=color_punto, marker='o', markersize=8)

    # Formato
    z_actual = datos['z_actual']
    titulo = f"🚨 ALERTA DE {tipo_alerta}: {t1} vs {t2} | Z-Score Actual: {z_actual:.2f}"
    ax.set_title(titulo, fontweight='bold', fontsize=14, color=color_punto)
    ax.grid(True, linestyle=':', alpha=0.3)
    ax.legend(loc='upper left')

    plt.tight_layout()
    
    # 1. Guardamos la imagen en la carpeta
    nombre_archivo = os.path.join(CARPETA_ACTUAL, f"ALERTA_{t1}_{t2}_{datetime.now().strftime('%H%M%S')}.png")
    plt.savefig(nombre_archivo)
    plt.close(fig) # Cerramos la figura en memoria para no colgar Python
    
    # 2. Abrimos la imagen con el visor predeterminado de Windows
    os.startfile(nombre_archivo)
    

# ==========================================
# 🧠 MOTOR DE CÁLCULO EN VIVO
# ==========================================
def calcular_zscore_live(t1, t2, ventana):
    """Descarga los últimos ~150 días y devuelve un diccionario con toda la data matemática"""
    try:
        df = yf.download([t1, t2], period="150d", progress=False)
        
        if isinstance(df.columns, pd.MultiIndex):
            df_close = df.xs('Close', level=1, axis=1) if 'Close' in df.columns.get_level_values(1) else df['Close']
        else:
            df_close = df

        if t1 not in df_close.columns or t2 not in df_close.columns:
            return None
            
        df_par = df_close[[t1, t2]].dropna()
        if len(df_par) < ventana + 10:
            return None 
            
        ratio = df_par[t1] / df_par[t2]
        media = ratio.rolling(window=ventana).mean()
        std = ratio.rolling(window=ventana).std()
        z_score = (ratio - media) / std
        
        # Ahora devolvemos el paquete de datos completo para el gráfico
        return {
            "z_actual": z_score.iloc[-1],
            "ratio": ratio,
            "media": media,
            "std": std,
            "fechas": ratio.index
        }
        
    except Exception as e:
        print(f"  ⚠️ Error calculando par {t1}/{t2}: {e}")
        return None

# ==========================================
# 🚀 BUCLE PRINCIPAL DEL CENTINELA
# ==========================================
def iniciar_monitor():
    print("\n" + "="*60)
    print(" 🦅 MONITOR TÁCTICO DE PARES (CORE-SATELLITE) INICIADO")
    print("="*60)
    print(f"⏱️  Chequeos programados cada {INTERVALO_CHEQUEO / 60:.0f} minutos.")
    print("👉 Apretá Ctrl+C para detener el centinela.\n")

    inicializar_watchlist()
    ultimo_chequeo = 0

    try:
        while True:
            ahora = time.time()
            
            if ahora - ultimo_chequeo >= INTERVALO_CHEQUEO:
                hora_actual = datetime.now().strftime('%H:%M:%S')
                print(f"🔍 [ {hora_actual} ] Escaneando el mercado...")
                
                cartera = cargar_json(ARCHIVO_CARTERA)
                watchlist = cargar_json(ARCHIVO_WATCHLIST)
                
                if not watchlist:
                    print("  ⚠️ La watchlist está vacía. Agregá pares en 'watchlist_ideal.json'.")
                
                alertas_generadas = 0

                for candidato in watchlist:
                    t1, t2 = candidato["t1"], candidato["t2"]
                    ventana, umbral = candidato["ventana"], candidato["umbral"]
                    
                    datos_calc = calcular_zscore_live(t1, t2, ventana)
                    
                    if datos_calc is None:
                        continue
                        
                    z_actual = datos_calc["z_actual"]
                    tenencia_t1 = cartera.get(t1, 0)
                    
                    # ALERTA DE VENTA
                    if z_actual >= umbral:
                        if tenencia_t1 > 0:
                            print(f"  🚨 ALERTA GATILLO: ¡VENDER {t1}! Rotar capital a {t2}.")
                            print(f"     ➔ El Z-Score voló a {z_actual:.2f} (Umbral: {umbral})")
                            plotear_alerta(t1, t2, datos_calc, 'VENDER', umbral)
                            alertas_generadas += 1
                            
                    # ALERTA DE COMPRA
                    elif z_actual <= -umbral:
                        if tenencia_t1 == 0:
                            print(f"  🚨 ALERTA GATILLO: ¡COMPRAR {t1}! Oportunidad de entrada frente a {t2}.")
                            print(f"     ➔ El Z-Score cayó a {z_actual:.2f} (Umbral: -{umbral})")
                            plotear_alerta(t1, t2, datos_calc, 'COMPRAR', umbral)
                            alertas_generadas += 1
                            
                if alertas_generadas == 0:
                    print("  ✅ Todo tranquilo. Ningún par rompió los umbrales de cointegración.")
                
                print("-" * 60)
                ultimo_chequeo = ahora
                
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 Monitor Táctico detenido por el usuario.")
    finally:
        # Cierra las ventanas de gráficos si detenemos el script a la fuerza
        plt.close('all') 

if __name__ == "__main__":
    iniciar_monitor()