"""
═══════════════════════════════════════════════════════════════
📋 CONFIG.PY - CONFIGURACIÓN CENTRALIZADA DEL ECOSISTEMA QUANT
═══════════════════════════════════════════════════════════════
Única fuente de verdad para parámetros, credenciales, rutas y timeframes.
Todos los módulos leen de aquí → MANTENIMIENTO CENTRALIZADO
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json

# ════════════════════════════════════════════════════════════
# 🎯 METADATA ECOSISTEMA
# ════════════════════════════════════════════════════════════
ECOSYSTEM = {
    'name': 'QUANT_TRADING_ECOSYSTEM',
    'version': '2.0.0',
    'export_date': datetime.now().isoformat(),
    'primary_ticker': 'GGAL',
    'default_broker': 'yfinance',  # Reemplazar por broker real
}

# ════════════════════════════════════════════════════════════
# 🔐 CREDENCIALES Y CONEXIÓN (Inyectable)
# ════════════════════════════════════════════════════════════
BROKER_CONFIG = {
    'provider': 'yfinance',  # 'yfinance', 'interactive_brokers', 'bybit', etc.
    'timeout': 30,
    'retries': 3,
    'cache_enabled': True,
    'cache_duration_hours': 24,
    # Para brokers reales (ejemplo):
    # 'api_key': os.getenv('BROKER_API_KEY', ''),
    # 'api_secret': os.getenv('BROKER_API_SECRET', ''),
    # 'account_id': os.getenv('BROKER_ACCOUNT_ID', ''),
}

# ════════════════════════════════════════════════════════════
# 📊 PARÁMETROS DE DESCARGA DE DATOS
# ════════════════════════════════════════════════════════════
DATA_PERIODS = {
    'intraday_short': '60d',      # Para cajas (15m, 1h)
    'intraday_long': '730d',      # Para MFE intradiario (2 años)
    'daily_medium': '2y',         # Para análisis diario
    'weekly_long': '5y',          # Para calibración semanal/histórica
}

DATA_INTERVALS = {
    'tick': '1m',
    'micro': '5m',
    'short': '15m',
    'medium': '1h',
    'daily': '1d',
    'weekly': '1wk',
    'monthly': '1mo',
}

# ════════════════════════════════════════════════════════════
# 🎛️ PARÁMETROS ROLLING/VENTANAS (Calibración)
# ════════════════════════════════════════════════════════════
ROLLING_WINDOWS = {
    # Módulo 00 - Calibrador
    'cajas_15m_window': 4,        # 4 velas de 15m = 60m caja
    'mfe_intra_min_samples': 3,
    'mfe_weekly_min_samples': 3,
    
    # Módulo 01 - Master Semanal
    'volatility_rolling_weeks': 13,     # P50 volatilidad
    'volatility_trend_sma': 4,          # Tendencia SMA
    'mfe_weekly_rolling': 26,           # MFE semanal
    'mfe_trend_sma': 8,                 # Tendencia MFE
    'power_prediction_weeks': 52,       # Hit rate último año
    
    # Módulo 02 - Intradiario
    'caja_daily_rolling': 60,           # Rolling cajas 60d
    'mfe_daily_rolling': 40,            # Rolling MFE 40d
    'mfe_trend_daily_sma': 15,          # Tendencia MFE diaria
    
    # Módulo 03 - Cierres (CLV)
    'clv_bins': [0, 20, 40, 60, 80, 100],  # Zonas CLV
    
    # Módulo 04 - Screeners
    'ratio_window_screener': 30,        # Ventana Z-Score
    'half_life_max_ferrari': 15,        # Max half-life modo agresivo
    'half_life_max_normal': 25,         # Max half-life modo normal
}

# ════════════════════════════════════════════════════════════
# 📈 PERCENTILES Y UMBRALES CUANT
# ════════════════════════════════════════════════════════════
PERCENTILES = {
    'p25': 0.25,
    'p50': 0.50,
    'p75': 0.75,
    'p90': 0.90,
}

Z_SCORE_THRESHOLDS = {
    'conservative': 1.5,    # Entrada estándar
    'moderate': 1.8,        # Entrada moderada agresiva
    'aggressive': 2.0,      # Entrada muy agresiva
}

COINTEGRATION_THRESHOLDS = {
    'strict': 0.10,         # p-value < 0.10
    'moderate': 0.15,       # p-value < 0.15
    'loose': 0.20,          # p-value < 0.20
}

HURST_THRESHOLDS = {
    'mean_revert_strict': 0.45,   # Mean reversion fuerte
    'mean_revert': 0.50,          # Mean reversion moderada
    'neutral': 0.55,              # Neutral (sin sesgo)
    'trending': 0.60,             # Tendencial
}

SPREAD_FILTER = {
    'max_spread_pct': 60.0,    # Rechazar spreads > 60%
    'min_mfe_pct': 0.1,        # MFE mínimo 0.1%
}

# ════════════════════════════════════════════════════════════
# 📁 RUTAS DE ARCHIVOS Y DIRECTORIOS
# ════════════════════════════════════════════════════════════
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PATHS = {
    'base': BASE_DIR,
    'data': os.path.join(BASE_DIR, 'data'),
    'cache': os.path.join(BASE_DIR, 'cache'),
    'outputs': os.path.join(BASE_DIR, 'outputs'),
    'reports': os.path.join(BASE_DIR, 'reports'),
    'logs': os.path.join(BASE_DIR, 'logs'),
    'params': os.path.join(BASE_DIR, 'params'),
}

# Crear directorios si no existen
for path in PATHS.values():
    os.makedirs(path, exist_ok=True)

# ════════════════════════════════════════════════════════════
# 📋 ARCHIVOS JSON ESTÁNDAR (Comunicación Inter-Módulos)
# ════════════════════════════════════════════════════════════
JSON_FILES = {
    'calibration': os.path.join(PATHS['params'], f"{ECOSYSTEM['primary_ticker']}_calibration.json"),
    'watchlist': os.path.join(PATHS['params'], 'watchlist_ideal.json'),
    'positions': os.path.join(PATHS['outputs'], 'positions_vivas.json'),
    'intraday_report': os.path.join(PATHS['reports'], 'intraday_report.json'),
    'weekly_report': os.path.join(PATHS['reports'], 'weekly_report.json'),
}

# ════════════════════════════════════════════════════════════
# 🖼️ ARCHIVOS DE SALIDA VISUAL
# ════════════════════════════════════════════════════════════
GRAPHICS_CONFIG = {
    'dpi': 100,
    'figsize_dashboard': (16, 10),
    'figsize_large': (16, 12),
    'style': 'dark_background',
    'font_size_title': 16,
    'font_size_label': 12,
    'alpha_fill': 0.4,
    'alpha_scatter': 0.6,
    'grid_alpha': 0.3,
}

# ════════════════════════════════════════════════════════════
# ⏰ HORARIOS Y SCHEDULING
# ════════════════════════════════════════════════════════════
SCHEDULE = {
    'calibrador_matinal': '06:00',          # UTC-3
    'master_intradiario': '09:00',          # Post apertura
    'master_semanal': '16:00',              # Cierre mercado US
    'master_cierres': '17:00',              # Post cierre
    'screeners': '19:00',                   # Análisis post-mercado
    'monitor_tactico': 'market_hours',      # Durante el mercado
}

# ════════════════════════════════════════════════════════════
# 📊 LOGGING
# ════════════════════════════════════════════════════════════
LOGGING_CONFIG = {
    'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR
    'format': '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S',
    'log_file': os.path.join(PATHS['logs'], f"quant_{datetime.now().strftime('%Y%m%d')}.log"),
}

# ════════════════════════════════════════════════════════════
# 🏷️ UNIVERSO DE ACTIVOS (Metadata)
# ════════════════════════════════════════════════════════════
UNIVERSO_ASSETS = {
    'GGAL': {'tags': {'ADR', 'Argentina', 'Financiero'}},
    'PEP': {'tags': {'USA', 'Dividendo', 'Consumo'}},
    'PG': {'tags': {'USA', 'Dividendo', 'Consumo'}},
    'COST': {'tags': {'USA', 'Dividendo', 'Retail'}},
    'SE': {'tags': {'USA', 'Growth', 'Tech'}},
    'NOK': {'tags': {'USA', 'Growth', 'Tech'}},
    'INTC': {'tags': {'USA', 'Growth', 'Tech'}},
    'DE': {'tags': {'USA', 'Cobertura', 'Industriales'}},
    'BRK-B': {'tags': {'USA', 'Cobertura', 'Financiero'}},
    'RIO': {'tags': {'USA', 'Cobertura', 'Minería'}},
}

# ════════════════════════════════════════════════════════════
# 🎯 MÓDULOS HABILITADOS (Control de ejecución)
# ════════════════════════════════════════════════════════════
MODULES_ENABLED = {
    '00_calibrador': True,
    '01_master_semanal': True,
    '02_master_intradiario': True,
    '03_master_cierres': True,
    '04_master_screeners': True,
    '05_monitor_tactico': True,
}

# ════════════════════════════════════════════════════════════
# 🔧 UTILIDADES
# ════════════════════════════════════════════════════════════
def get_default_ticker() -> str:
    """Obtiene el ticker principal del ecosistema."""
    return ECOSYSTEM['primary_ticker']

def get_broker_config() -> Dict[str, Any]:
    """Retorna configuración del broker (segura para credenciales)."""
    return BROKER_CONFIG.copy()

def is_module_enabled(module_name: str) -> bool:
    """Verifica si un módulo está habilitado."""
    return MODULES_ENABLED.get(module_name, False)

def get_json_path(key: str) -> str:
    """Obtiene la ruta de un archivo JSON por clave."""
    return JSON_FILES.get(key, '')

def print_config_summary():
    """Imprime un resumen de la configuración."""
    print("\n" + "="*70)
    print(f" 📋 CONFIGURACIÓN CENTRALIZADA - {ECOSYSTEM['name']} v{ECOSYSTEM['version']}")
    print("="*70)
    print(f"\nTicker Principal: {ECOSYSTEM['primary_ticker']}")
    print(f"Broker: {BROKER_CONFIG['provider']}")
    print(f"Directorio Base: {PATHS['base']}")
    print(f"\nMódulos Habilitados: {sum(MODULES_ENABLED.values())}/{len(MODULES_ENABLED)}")
    print("="*70 + "\n")

if __name__ == '__main__':
    print_config_summary()
