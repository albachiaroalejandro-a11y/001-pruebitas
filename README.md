#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════════════╗
║  📖 README.md - GUÍA DE INSTALACIÓN Y USO DEL ECOSISTEMA QUANT                      ║
╚═══════════════════════════════════════════════════════════════════════════════════════╝
"""

# 🚀 QUANT Trading Ecosystem - Guía Completa

## 📋 Índice

1. [Instalación](#instalación)
2. [Ejecución Rápida](#ejecución-rápida)
3. [Estructura del Proyecto](#estructura-del-proyecto)
4. [Componentes Principales](#componentes-principales)
5. [Guía de Uso](#guía-de-uso)
6. [Troubleshooting](#troubleshooting)

---

## ⚡ Instalación

### **Requisitos Previos**
- Python 3.8+
- pip (gestor de paquetes)
- Terminal/Consola

### **Paso 1: Clonar el Repositorio**

```bash
cd /ruta/donde/quieras
git clone https://github.com/albachiaroalejandro-a11y/001-pruebitas.git
cd 001-pruebitas
```

### **Paso 2: Crear Entorno Virtual (RECOMENDADO)**

```bash
# En macOS / Linux
python3 -m venv venv
source venv/bin/activate

# En Windows
python -m venv venv
venv\Scripts\activate
```

### **Paso 3: Instalar Dependencias**

```bash
pip install -r requirements.txt
```

**Contenido de `requirements.txt`:**
```
pandas>=1.5.0
numpy>=1.24.0
yfinance>=0.2.0
matplotlib>=3.7.0
scipy>=1.10.0
statsmodels>=0.14.0
```

### **Paso 4: Verificar Instalación**

```bash
python3 -c "from config import ECOSYSTEM; print(f'✅ Instalación exitosa: {ECOSYSTEM[\"name\"]} v{ECOSYSTEM[\"version\"]}')"
```

Deberías ver:
```
✅ Instalación exitosa: QUANT_TRADING_ECOSYSTEM v2.0.0
```

---

## 🎯 Ejecución Rápida

### **Opción 1: Menú Principal (RECOMENDADO)**

```bash
python3 main.py
```

Verás el menú:
```
═══════════════════════════════════════════════════════════════════
              📊 MENÚ PRINCIPAL - QUANT TRADING ECOSYSTEM
═���═════════════════════════════════════════════════════════════════

[1] 📊 Mostrar Dashboard Interactivo (TUI)
[2] 📄 Generar Reporte HTML
[3] ⚙️  Ejecutar Módulo Individual
[4] 🔄 Ejecutar Todos los Módulos (Secuencia)
[5] 📋 Ver Configuración del Sistema
[6] 📝 Ver Últimos Logs
[7] 🧹 Limpiar Caché
[q] ❌ Salir
```

### **Opción 2: Dashboard Directo**

```bash
python3 dashboard.py
```

### **Opción 3: Generar Reporte HTML**

```bash
python3 visualizer.py
```

Se crea: `reports/ecosystem_report.html`

---

## 📂 Estructura del Proyecto

```
001-pruebitas/
│
├── 📄 main.py                    ← PUNTO DE ENTRADA (EJECUTAR ESTO)
├── 📄 README.md                  ← Esta guía
├── 📄 requirements.txt           ← Dependencias Python
│
├── 🏗️ CORE FRAMEWORK
│   ├── config.py                 ← Configuración centralizada
│   ├── logger_quant.py           ← Sistema de logging unificado
│   ├── data_provider.py          ← Abstracción de datos (API + caché)
│   ├── quant_engine.py           ← Funciones cuantitativas comunes
│   └── base_module.py            ← Clase base para módulos
│
├── 🎨 INTERFACES VISUALES
│   ├── dashboard.py              ← Terminal UI interactivo
│   └── visualizer.py             ← Generador reportes HTML + SVG
│
├── 📦 MÓDULOS ANÁLISIS (Próximamente refactorizados)
│   ├── 00_calibrador_matinal.py  ← Calibración diaria
│   ├── 01_master_semanal.py      ← Análisis semanal
│   ├── 02_master_intradiario.py  ← Análisis intradia
│   ├── 03_master_cierres.py      ← Mapeo probabilístico
│   ├── 04_master_screeners.py    ← Pares cointegrados
│   └── 05_monitor_tactico.py     ← Monitoreo en tiempo real
│
├── 🤖 ORQUESTACIÓN
│   └── conserje.py               ← Coordinador de módulos (próximamente)
│
├── 📁 data/
│   ├── cache/                    ← Datos cacheados (auto-limpieza)
│   ├── outputs/                  ← Resultados procesados
│   ├── reports/                  ← Reportes HTML + PNG
│   ├── logs/                     ← Logs de ejecución
│   └── params/                   ← Parámetros JSON inter-módulos
│
└── 📚 DOCUMENTACIÓN
    └── LLM_Contexto_Quant.txt    ← Código original concatenado
```

---

## 🔧 Componentes Principales

### **1. `config.py` - Configuración Centralizada**

```python
# NO hardcodees parámetros aquí, úsalo en config.py

from config import (
    ECOSYSTEM,           # Metadata global
    BROKER_CONFIG,      # Config broker (yfinance, ByBit, etc.)
    DATA_PERIODS,       # Períodos ('60d', '5y', etc.)
    ROLLING_WINDOWS,    # Ventanas móviles (13 semanas, 60 días, etc.)
    Z_SCORE_THRESHOLDS, # Umbrales Z-Score
    PATHS,              # Directorios (auto-creados)
    JSON_FILES,         # Ubicación de archivos JSON
)
```

### **2. `logger_quant.py` - Logging Unificado**

```python
from logger_quant import log

# Úsalo en lugar de print()
log.info("Mensaje informativo", "nombre_modulo")
log.success("Operación exitosa", "nombre_modulo")
log.warning("Advertencia", "nombre_modulo")
log.error("Error", "nombre_modulo")
log.metric("Etiqueta", valor, "unidad", "nombre_modulo")
```

### **3. `data_provider.py` - Abstracción de Datos**

```python
from data_provider import data_provider

# Descarga con caché automático
df = data_provider.download_ohlcv(
    ticker='GGAL',
    period='60d',
    interval='15m'
)

# Descarga múltiples tickers
df_multi = data_provider.download_multiple(
    tickers=['GGAL', 'AAPL', 'MSFT'],
    period='1y',
    interval='1d'
)
```

### **4. `quant_engine.py` - Motor de Cálculos**

```python
from quant_engine import qe

# Funciones reutilizables
spread = qe.calculate_spread(high=100, low=95)
mfe, mae = qe.calculate_mfe(entry=100, high=105, low=92)
clv = qe.calculate_clv(close=98, high=102, low=94)
zscore = qe.calculate_zscore(series, window=30)
hurst = qe.calculate_hurst(time_series)
```

### **5. `base_module.py` - Clase Base**

```python
from base_module import QuantModule

class MiModulo(QuantModule):
    def validate_inputs(self) -> bool:
        # Validar datos
        return True
    
    def execute(self) -> Dict[str, Any]:
        # Lógica principal
        return {'resultado': valor}

# Usar
modulo = MiModulo('mi_modulo')
if modulo.run():
    modulo.print_summary()
    modulo.export_json('salida', modulo.results)
```

---

## 📖 Guía de Uso

### **Caso 1: Quiero Ver el Dashboard**

```bash
python3 main.py
# Presiona [1]
```

Navega con flechas, presiona [h] para ayuda.

### **Caso 2: Quiero Generar un Reporte HTML**

```bash
python3 main.py
# Presiona [2]
```

Se abre automáticamente en navegador.

### **Caso 3: Quiero Refactorizar un Módulo Existente**

```python
# 1. Crear archivo nuevo: 01_master_semanal_v2.py
# 2. Heredar de QuantModule
# 3. Implementar validate_inputs() y execute()
# 4. Reutilizar data_provider + quant_engine
# 5. Exportar resultados con export_json()

from base_module import QuantModule
from data_provider import data_provider
from quant_engine import qe

class MasterSemanal(QuantModule):
    def validate_inputs(self) -> bool:
        return True
    
    def execute(self):
        # Usar data_provider
        df = data_provider.download_ohlcv('GGAL', '5y', '1d')
        
        # Usar quant_engine
        spreads = qe.calculate_spread(df['High'], df['Low'])
        
        # Exportar
        self.export_json('weekly_report', {...})
        
        return {...}

# Ejecutar
modulo = MasterSemanal()
modulo.run()
```

### **Caso 4: Quiero Ver Configuración**

```bash
python3 main.py
# Presiona [5]
```

Ve todos los parámetros, módulos habilitados, directorios.

### **Caso 5: Quiero Cambiar Parámetros Globales**

```python
# Abre config.py
# Cambia valores (ej: ROLLING_WINDOWS)
# Se propaga a TODO el sistema

# Ejemplo: cambiar ventana de volatilidad
ROLLING_WINDOWS['volatility_rolling_weeks'] = 20  # Era 13
```

Todo se actualiza automáticamente.

---

## 🆘 Troubleshooting

### **Problema: "ModuleNotFoundError: No module named 'pandas'"**

**Solución:**
```bash
pip install -r requirements.txt
# O instalar directamente:
pip install pandas numpy yfinance matplotlib scipy statsmodels
```

### **Problema: "Permission denied" al ejecutar main.py**

**Solución:**
```bash
chmod +x main.py
python3 main.py  # Usa python3 explícitamente
```

### **Problema: Dashboard no se ve bien en terminal**

**Solución:**
- Terminal debe soportar colores ANSI (la mayoría lo hace)
- En Windows, usa Windows Terminal (mejor que cmd.exe)
- Aumenta tamaño de terminal

### **Problema: HTML no abre en navegador**

**Solución:**
```bash
# Abre manualmente
open reports/ecosystem_report.html  # macOS
xdg-open reports/ecosystem_report.html  # Linux
start reports/ecosystem_report.html  # Windows
```

### **Problema: Caché de datos no se actualiza**

**Solución:**
```bash
python3 main.py
# Presiona [7] para limpiar caché
# O borrar carpeta: rm -rf data/cache/
```

### **Problema: Logs no se generan**

**Solución:**
- Verificar que directorio `logs/` existe (se crea automáticamente)
- Verificar permisos de escritura: `chmod 755 logs/`

---

## 🎯 Próximos Pasos

1. **Refactorizar módulos**: 00 → 06 heredando de `QuantModule`
2. **Crear `conserje.py`**: Orquestador que ejecuta secuencia
3. **Integrar credenciales.py**: Gestión segura de credenciales
4. **Agregar tests**: Unittest para cada módulo
5. **Webhook/Alerts**: Notificaciones de errores
6. **API REST**: Exponer como servicio web

---

## 📞 Soporte

Si encuentras problemas:

1. Revisa los logs: `python3 main.py` → [6]
2. Verifica configuración: `python3 main.py` → [5]
3. Limpia caché: `python3 main.py` → [7]
4. Abre un issue en GitHub

---

## 📜 Licencia

Proyecto personal - Uso libre

---

**¡Feliz trading! 🚀📊**
