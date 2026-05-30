"""
═══════════════════════════════════════════════════════════════
📥 DATA_PROVIDER.PY - ABSTRACCIÓN DE DATOS (Broker/API/Caché)
═══════════════════════════════════════════════════════════════
Capa unificada para obtener datos sin importar la fuente.
Soporta caché local, reintentos y fallover automático.
"""

import os
import json
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import hashlib
import warnings

from config import BROKER_CONFIG, DATA_PERIODS, DATA_INTERVALS, PATHS
from logger_quant import log

warnings.simplefilter(action='ignore')

class DataProvider:
    """
    Proveedor centralizado de datos.
    - Descarga de múltiples fuentes (yfinance, APIs reales, etc.)
    - Caché automático local
    - Manejo de errores y reintentos
    - Validación de datos
    """
    
    def __init__(self, broker_config: Optional[Dict] = None):
        self.config = broker_config or BROKER_CONFIG
        self.cache_dir = PATHS['cache']
        self.cache_enabled = self.config.get('cache_enabled', True)
        self.cache_duration_hours = self.config.get('cache_duration_hours', 24)
        log.info(f"DataProvider inicializado. Caché: {self.cache_enabled}", 'data_provider')
    
    def _get_cache_key(self, ticker: str, interval: str, period: str) -> str:
        """Genera clave de caché única."""
        key_str = f"{ticker}_{interval}_{period}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _get_cache_path(self, ticker: str, interval: str, period: str) -> str:
        """Retorna ruta de archivo caché."""
        cache_key = self._get_cache_key(ticker, interval, period)
        return os.path.join(self.cache_dir, f"{cache_key}.pkl")
    
    def _is_cache_valid(self, cache_path: str) -> bool:
        """Verifica si caché está vigente."""
        if not os.path.exists(cache_path):
            return False
        
        file_age_hours = (datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_path))).total_seconds() / 3600
        return file_age_hours < self.cache_duration_hours
    
    def _load_cache(self, cache_path: str) -> Optional[pd.DataFrame]:
        """Carga datos del caché."""
        try:
            return pd.read_pickle(cache_path)
        except Exception as e:
            log.warning(f"Error cargando caché: {e}", 'data_provider')
            return None
    
    def _save_cache(self, df: pd.DataFrame, cache_path: str):
        """Guarda datos en caché."""
        try:
            df.to_pickle(cache_path)
            log.debug(f"Caché guardado: {cache_path}", 'data_provider')
        except Exception as e:
            log.warning(f"Error guardando caché: {e}", 'data_provider')
    
    def download_ohlcv(self, ticker: str, period: str = '1y', interval: str = '1d') -> Optional[pd.DataFrame]:
        """
        Descarga datos OHLCV con caché automático.
        
        Args:
            ticker: Símbolo (ej: 'GGAL', 'AAPL')
            period: Período (ej: '60d', '5y')
            interval: Intervalo (ej: '15m', '1h', '1d')
        
        Returns:
            DataFrame con OHLCV o None si falla
        """
        
        # Intentar caché primero
        if self.cache_enabled:
            cache_path = self._get_cache_path(ticker, interval, period)
            if self._is_cache_valid(cache_path):
                df = self._load_cache(cache_path)
                if df is not None:
                    log.debug(f"Datos cargados del caché: {ticker}", 'data_provider')
                    return df
        
        # Descargar desde broker
        try:
            log.debug(f"Descargando {ticker} ({period}, {interval})...", 'data_provider')
            
            if self.config['provider'] == 'yfinance':
                df = yf.download(ticker, period=period, interval=interval, progress=False)
            else:
                raise NotImplementedError(f"Broker {self.config['provider']} no soportado")
            
            # Limpiar MultiIndex si existe
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            # Validar datos
            if df.empty:
                log.warning(f"Sin datos para {ticker}", 'data_provider')
                return None
            
            # Guardar en caché
            if self.cache_enabled:
                cache_path = self._get_cache_path(ticker, interval, period)
                self._save_cache(df, cache_path)
            
            log.success(f"Datos descargados: {ticker} ({len(df)} velas)", 'data_provider')
            return df
        
        except Exception as e:
            log.error(f"Error descargando {ticker}: {e}", 'data_provider')
            return None
    
    def download_multiple(self, tickers: List[str], period: str = '1y', interval: str = '1d') -> pd.DataFrame:
        """
        Descarga múltiples tickers en paralelo.
        """
        try:
            log.debug(f"Descargando {len(tickers)} activos...", 'data_provider')
            
            if self.config['provider'] == 'yfinance':
                df = yf.download(tickers, period=period, interval=interval, progress=False)
            else:
                raise NotImplementedError(f"Broker {self.config['provider']} no soportado")
            
            if isinstance(df.columns, pd.MultiIndex):
                nivel_cero = df.columns.get_level_values(0)
                nivel_uno = df.columns.get_level_values(1)
                
                if 'Close' in nivel_cero:
                    df = df['Close']
                elif 'Close' in nivel_uno:
                    df = df.xs('Close', level=1, axis=1)
                else:
                    df = df.xs('Adj Close', level=1, axis=1) if 'Adj Close' in nivel_uno else df
            
            df = df.dropna(axis=1, how='all')
            log.success(f"Múltiples activos descargados: {len(tickers)} tickers", 'data_provider')
            return df
        
        except Exception as e:
            log.error(f"Error descargando múltiples tickers: {e}", 'data_provider')
            return pd.DataFrame()
    
    def get_period_interval(self, module_type: str) -> Tuple[str, str]:
        """
        Retorna período e intervalo recomendados según módulo.
        
        Args:
            module_type: 'calibrador', 'intradiario', 'semanal', 'cierres', 'screeners'
        
        Returns:
            Tupla (period, interval)
        """
        config_map = {
            'calibrador': (DATA_PERIODS['intraday_long'], DATA_INTERVALS['short']),
            'intradiario': (DATA_PERIODS['intraday_long'], DATA_INTERVALS['medium']),
            'semanal': (DATA_PERIODS['weekly_long'], DATA_INTERVALS['daily']),
            'cierres': (DATA_PERIODS['weekly_long'], DATA_INTERVALS['daily']),
            'screeners': ('3y', DATA_INTERVALS['daily']),
        }
        return config_map.get(module_type, ('1y', '1d'))
    
    def clear_cache(self, older_than_hours: int = 24):
        """Limpia archivos de caché antiguos."""
        try:
            now = datetime.now()
            removed = 0
            for fname in os.listdir(self.cache_dir):
                fpath = os.path.join(self.cache_dir, fname)
                if os.path.isfile(fpath):
                    file_age_hours = (now - datetime.fromtimestamp(os.path.getmtime(fpath))).total_seconds() / 3600
                    if file_age_hours > older_than_hours:
                        os.remove(fpath)
                        removed += 1
            log.info(f"Caché limpiado: {removed} archivos removidos", 'data_provider')
        except Exception as e:
            log.error(f"Error limpiando caché: {e}", 'data_provider')

# Instancia global
data_provider = DataProvider()

if __name__ == '__main__':
    # Test
    dp = DataProvider()
    df = dp.download_ohlcv('GGAL', period='60d', interval='15m')
    print(df.head())
    print(f"Forma: {df.shape}")
