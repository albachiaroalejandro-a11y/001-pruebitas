import os
import json
import sys
import subprocess
import shutil
from datetime import datetime
import os
import getpass


# ==========================================
# ⚙️ RUTAS Y CONFIGURACIÓN BASE
# ==========================================
CARPETA_ACTUAL = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_CARTERA = os.path.join(CARPETA_ACTUAL, "cartera_hoy.json")
ARCHIVO_RATIOS = os.path.join(CARPETA_ACTUAL, "ratios_cedear.json")
CARPETA_BKP = os.path.join(CARPETA_ACTUAL, "BKP")

def inicializar_archivos():
    if not os.path.exists(ARCHIVO_RATIOS):
        ratios_base = {
            "AAPL": 20, "KO": 5, "PEP": 6, "PG": 15, 
            "COST": 48, "IBM": 15, "RIO": 8, "CAT": 20
        }
        with open(ARCHIVO_RATIOS, 'w') as f:
            json.dump(ratios_base, f, indent=4)
            
    if not os.path.exists(ARCHIVO_CARTERA):
        with open(ARCHIVO_CARTERA, 'w') as f:
            json.dump({}, f, indent=4)

inicializar_archivos()

# ==========================================
# 💼 MÓDULOS DE GESTIÓN DE CARTERA
# ==========================================
def cargar_json(ruta):
    if os.path.exists(ruta):
        try:
            with open(ruta, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def guardar_json(ruta, datos):
    with open(ruta, 'w') as f:
        json.dump(datos, f, indent=4)

def cargar_operacion(ticker, cantidad, es_cedear=False):
    cartera = cargar_json(ARCHIVO_CARTERA)
    
    if es_cedear:
        ratios = cargar_json(ARCHIVO_RATIOS)
        if ticker not in ratios:
            print(f"\n❌ Error: No tengo el ratio de conversión para {ticker}.")
            print("Agregalo manualmente en 'ratios_cedear.json'.")
            return
            
        ratio = ratios[ticker]
        cantidad_adr = cantidad / ratio
        print(f"🔄 Conversión automática: {cantidad} CEDEARs (Ratio {ratio}:1) = {cantidad_adr:.2f} ADRs")
    else:
        cantidad_adr = cantidad
        
    cartera[ticker] = cartera.get(ticker, 0.0) + cantidad_adr
    
    if abs(cartera[ticker]) < 0.01:
        del cartera[ticker]
        print(f"🧹 Posición de {ticker} cerrada. Eliminada de la vigilancia.")
        
    guardar_json(ARCHIVO_CARTERA, cartera)
    print(f"✅ Cartera actualizada. Posición actual de {ticker}: {cartera.get(ticker, 0):.2f} ADRs\n")

# ==========================================
# 📁 MÓDULOS DE ARCHIVOS Y BACKUPS
# ==========================================
def obtener_todos_los_scripts():
    mi_nombre = os.path.basename(__file__)
    archivos = [f for f in os.listdir(CARPETA_ACTUAL) if f.endswith('.py') and f != mi_nombre]
    return sorted(archivos)

def obtener_scripts_lanzables():
    # Ignoramos módulos pasivos para que no ensucien el lanzador
    archivos = obtener_todos_los_scripts()
    return [f for f in archivos if "credenciales" not in f and "universo" not in f]

def crear_backup(script_name):
    # Verificamos si existe la carpeta BKP y si no, la creamos
    if not os.path.exists(CARPETA_BKP):
        os.makedirs(CARPETA_BKP)

    ruta_original = os.path.join(CARPETA_ACTUAL, script_name)
    nombre_sin_ext = script_name.replace('.py', '')
    fecha_str = datetime.now().strftime('%Y%m%d_%H%M')
    nuevo_nombre = f"{nombre_sin_ext}_BKP_{fecha_str}.py"
    
    # Guardamos directamente en la carpeta BKP
    ruta_backup = os.path.join(CARPETA_BKP, nuevo_nombre)
    
    try:
        shutil.copy2(ruta_original, ruta_backup)
        print(f"\n✅ ¡Copia de seguridad creada con éxito!\n📂 Guardado en: BKP/{nuevo_nombre}")
    except Exception as e:
        print(f"\n❌ Error al crear el backup: {e}")

def renombrar_script(script_name):
    ruta_original = os.path.join(CARPETA_ACTUAL, script_name)
    print(f"\n✏️ Renombrando: {script_name}")
    nuevo_nombre = input("👉 Ingresá el nuevo nombre (ej: mi_script.py): ").strip()
    
    if not nuevo_nombre: 
        print("❌ Operación cancelada. No ingresaste ningún nombre.")
        return
        
    if not nuevo_nombre.endswith('.py'):
        nuevo_nombre += '.py'
        
    ruta_nueva = os.path.join(CARPETA_ACTUAL, nuevo_nombre)
    
    if os.path.exists(ruta_nueva):
        print(f"\n❌ Operación cancelada. Ya existe un archivo llamado '{nuevo_nombre}'.")
        return
        
    try:
        os.rename(ruta_original, ruta_nueva)
        print(f"\n✅ ¡Archivo renombrado con éxito!\n📂 De: {script_name}\n📂 A:   {nuevo_nombre}")
    except Exception as e:
        print(f"\n❌ Error al renombrar: {e}")

# ==========================================
# 🚀 MÓDULO LANZADOR 
# ==========================================
def ejecutar_script(nombre_script):
    ruta_script = os.path.join(CARPETA_ACTUAL, nombre_script)
    print("\n" + "="*60)
    print(f" 🚀 INICIANDO: {nombre_script}")
    print("="*60)
    
    try:
        proceso = subprocess.Popen(
            [sys.executable, ruta_script],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, 
            text=True,
            bufsize=1
        )
        
        for linea in proceso.stdout:
            print(linea, end='')
            
        proceso.wait() 
        
    except KeyboardInterrupt:
        print(f"\n🛑 Ejecución interrumpida por el usuario (Ctrl+C).")
        try:
            proceso.terminate() 
        except:
            pass
    except Exception as e:
        print(f"\n❌ Error al ejecutar el script: {e}")
        
    print("="*60)
    print(f" 🏁 FIN DE EJECUCIÓN - Volviendo al Conserje...")
    print("="*60 + "\n")

def exportar_para_gemini(scripts):
    nombre_salida = os.path.join(CARPETA_ACTUAL, "LLM_Contexto_Quant.txt")
    try:
        with open(nombre_salida, "w", encoding="utf-8") as out_file:
            out_file.write(f"FECHA DE EXPORTACIÓN: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            out_file.write("ESTE ARCHIVO CONTIENE EL ECOSISTEMA QUANT COMPLETO.\n\n")
            for script in scripts:
                out_file.write(f"{'='*60}\n 📁 ARCHIVO: {script}\n{'='*60}\n")
                with open(os.path.join(CARPETA_ACTUAL, script), "r", encoding="utf-8") as in_file:
                    out_file.write(in_file.read())
                out_file.write("\n\n")
        return True, nombre_salida
    except Exception as e:
        return False, str(e)
    
# ==========================================
# 🧠 BUCLE PRINCIPAL E INTERFAZ
# ==========================================
while True:
    print("\n" + "█"*60)
    print(" 🛎️  EL CONSERJE V3.0 - HUB CENTRAL QUANT")
    print("█"*60)

    print("\n 💼 GESTIÓN DE CARTERA:")
    print(" [1] Ver mi cartera actual")
    print(" [2] Cargar operación local (CEDEARs)")
    print(" [3] Cargar operación exterior (ADRs directos)")
    
    print("\n 🚀 LANZADOR DE SCRIPTS:")
    print(" [4] Listar y ejecutar un script")

    print("\n 🛠️  MANTENIMIENTO Y ARCHIVOS:")
    print(" [5] Crear copia de seguridad (Backup) en carpeta BKP")
    print(" [6] Renombrar un archivo")
    print(" [7] Exportar ecosistema para Gemini")
    print(" [0] Salir")
    print("-" * 60)

    opcion = input("👉 Su orden: ").strip()

    # --- BLOQUE CARTERA ---
    if opcion == '1':
        cartera = cargar_json(ARCHIVO_CARTERA)
        print("\n💼 TU CARTERA ACTUAL (Expresada en ADRs):")
        if not cartera:
            print("   La cartera está vacía.")
        else:
            for t, cant in cartera.items():
                print(f"   - {t}: {cant:.2f} nominales reales")
        
    elif opcion == '2':
        print("\n📝 CARGA DE OPERACIÓN LOCAL (CEDEARs)")
        ticker = input("Ticker del CEDEAR (Ej: PEP): ").strip().upper()
        try:
            entrada = input("Cantidad operada (usá - para ventas): ").strip().replace(',', '.')
            cantidad = float(entrada)
            cargar_operacion(ticker, cantidad, es_cedear=True)
        except ValueError:
            print("❌ Cantidad inválida.")
            
    elif opcion == '3':
        print("\n📝 CARGA DE OPERACIÓN EXTERIOR (ADRs directos)")
        ticker = input("Ticker del activo (Ej: SPY): ").strip().upper()
        try:
            entrada = input("Cantidad de nominales operados (usá - para ventas): ").strip().replace(',', '.')
            cantidad = float(entrada)
            cargar_operacion(ticker, cantidad, es_cedear=False)
        except ValueError:
            print("❌ Cantidad inválida.")

    # --- BLOQUE LANZADOR ---
    elif opcion == '4':
        lanzables = obtener_scripts_lanzables()
        print("\n🚀 SCRIPTS DISPONIBLES PARA EJECUTAR:")
        for idx, s in enumerate(lanzables): 
            print(f" [{idx}] {s}")
            
        seleccion = input("\n👉 Número del script a ejecutar (Enter para cancelar): ").strip()
        if seleccion.isdigit() and 0 <= int(seleccion) < len(lanzables):
            ejecutar_script(lanzables[int(seleccion)])
        elif seleccion != "":
            print("❌ Opción no válida.")

    # --- BLOQUE ARCHIVOS ---
    elif opcion == '5':
        todos_los_scripts = obtener_todos_los_scripts()
        print("\n🛡️  CREAR COPIA DE SEGURIDAD (BACKUP)")
        for idx, s in enumerate(todos_los_scripts): 
            print(f" [{idx}] {s}")
            
        seleccion = input("\n👉 Número de archivo a respaldar (Enter para cancelar): ").strip()
        if seleccion.isdigit() and 0 <= int(seleccion) < len(todos_los_scripts):
            crear_backup(todos_los_scripts[int(seleccion)])
        elif seleccion != "":
            print("❌ Opción no válida.")

    elif opcion == '6':
        todos_los_scripts = obtener_todos_los_scripts()
        print("\n✏️  RENOMBRAR ARCHIVO")
        for idx, s in enumerate(todos_los_scripts): 
            print(f" [{idx}] {s}")
            
        seleccion = input("\n👉 Número de archivo a renombrar (Enter para cancelar): ").strip()
        if seleccion.isdigit() and 0 <= int(seleccion) < len(todos_los_scripts):
            renombrar_script(todos_los_scripts[int(seleccion)])
        elif seleccion != "":
            print("❌ Opción no válida.")

    elif opcion == '7':
        todos_los_scripts = obtener_todos_los_scripts()
        print("\n⏳ Empaquetando ecosistema...")
        exito, msg = exportar_para_gemini(todos_los_scripts)
        if exito:
            print(f"✅ ¡Éxito! Se creó el archivo:\n📂 {msg}")
        else:
            print(f"❌ Error al exportar: {msg}")
            
    # --- SALIDA ---
    elif opcion == '0' or opcion == '':
        print("\n👋 ¡Cerrando Hub Central! Buenas inversiones.")
        break
        
    else:
        print("⚠️ Opción no válida. Intentá de nuevo.")