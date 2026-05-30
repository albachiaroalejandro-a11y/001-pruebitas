"""
═══════════════════════════════════════════════════════════════
⚙️ QUANT_ENGINE.PY - MOTOR DE CÁLCULOS COMUNES
═══════════════════════════════════════════════════════════════
Biblioteca de funciones reutilizables para todos los módulos.
"""

import numpy as np
import pandas as pd
from typing import Tuple, List, Dict, Any
from scipy import stats

from config import ROLLING_WINDOWS, PERCENTILES, Z_SCORE_THRESHOLDS
from logger_quant import log

class QuantEngine:
    """
    Motor cuantitativo centralizado.
    - Cálculos de amplitud, spreads, MFE
    - Z-Score y bandas de Bollinger
    - Cointegración y Hurst
    - Percentiles y estadística
    """
    
    # ════════════════════════════════════════════════════════════
    # 📊 CÁLCULOS DE AMPLITUD Y SPREADS
    # ════════════════════════════════════════════════════════════
    
    @staticmethod
    def calculate_spread(high: float, low: float, reference: float = None) -> float:
        """
        Calcula spread (amplitud) como % del precio.
        
        Args:
            high: Precio máximo
            low: Precio mínimo
            reference: Referencia (default: low)
        
        Returns:
            Spread en %
        """
        ref = reference or low
        if ref == 0:
            return 0.0
        return ((high - low) / ref) * 100
    
    @staticmethod
    def calculate_mfe(entry_price: float, high: float, low: float) -> Tuple[float, float]:
        """
        Calcula Maximum Favorable Excursion (MFE) y Maximum Adverse Excursion (MAE).
        
        Args:
            entry_price: Precio de entrada
            high: Máximo alcanzado
            low: Mínimo alcanzado
        
        Returns:
            Tupla (MFE%, MAE%)
        """
        mfe = ((high - entry_price) / entry_price) * 100 if entry_price > 0 else 0
        mae = ((entry_price - low) / entry_price) * 100 if entry_price > 0 else 0
        return (mfe, mae)
    
    @staticmethod
    def calculate_clv(close: float, high: float, low: float) -> float:
        """
        Calcula Close Location Value (CLV).
        Posición del cierre dentro del rango del día.
        
        Args:
            close: Precio de cierre
            high: Máximo
            low: Mínimo
        
        Returns:
            CLV en % (0-100)
        """
        rango = high - low
        if rango == 0:
            return 50.0
        return ((close - low) / rango) * 100
    
    # ════════════════════════════════════════════════════════════
    # 📈 Z-SCORE Y BANDAS DE BOLLINGER
    # ════════════════════════════════════════════════════════════
    
    @staticmethod
    def calculate_zscore(series: pd.Series, window: int = 30, threshold: str = 'conservative') -> pd.Series:
        """
        Calcula Z-Score con umbral configurable.
        
        Args:
            series: Serie de datos
            window: Ventana de media móvil
            threshold: 'conservative', 'moderate', 'aggressive'
        
        Returns:
            Series de Z-Scores
        """
        media = series.rolling(window=window).mean()
        std = series.rolling(window=window).std()
        zscore = (series - media) / std
        return zscore
    
    @staticmethod
    def calculate_bollinger_bands(series: pd.Series, window: int = 20, num_std: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calcula bandas de Bollinger.
        
        Args:
            series: Serie de precios
            window: Ventana
            num_std: Número de desviaciones estándar
        
        Returns:
            Tupla (SMA, Banda Superior, Banda Inferior)
        """
        sma = series.rolling(window=window).mean()
        std = series.rolling(window=window).std()
        upper = sma + (std * num_std)
        lower = sma - (std * num_std)
        return (sma, upper, lower)
    
    # ════════════════════════════════════════════════════════════
    # 🔗 COINTEGRACIÓN Y HURST
    # ════════════════════════════════════════════════════════════
    
    @staticmethod
    def calculate_hurst(ts: np.ndarray) -> float:
        """
        Calcula Hurst Exponent.
        < 0.5: Mean reversion
        = 0.5: Random walk
        > 0.5: Trending
        """
        try:
            lags = range(2, min(20, len(ts) // 2))
            tau = [np.sqrt(np.std(np.subtract(ts[lag:], ts[:-lag]))) for lag in lags]
            poly = np.polyfit(np.log(lags), np.log(tau), 1)
            return poly[0] * 2.0
        except:
            return np.nan
    
    @staticmethod
    def calculate_ratio(s1: pd.Series, s2: pd.Series) -> pd.Series:
        """
        Calcula ratio entre dos series (para pairs trading).
        """
        return s1 / s2
    
    # ════════════════════════════════════════════════════════════
    # 📊 PERCENTILES Y ESTADÍSTICA
    # ════════════════════════════════════════════════════════════
    
    @staticmethod
    def calculate_rolling_percentiles(series: pd.Series, window: int, percentiles: List[float] = None) -> Dict[str, pd.Series]:
        """
        Calcula percentiles rodantes.
        """
        percentiles = percentiles or [0.25, 0.50, 0.75]
        result = {}
        for p in percentiles:
            result[f'P{int(p*100)}'] = series.rolling(window=window).quantile(p)
        return result
    
    @staticmethod
    def classify_by_percentile(value: float, p25: float, p50: float, p75: float) -> str:
        """
        Clasifica un valor según percentiles.
        """
        if value < p25:
            return "EXTREMO_BAJO"
        elif value < p50:
            return "BAJO"
        elif value < p75:
            return "MEDIO"
        else:
            return "EXTREMO_ALTO"
    
    # ════════════════════════════════════════════════════════════
    # 🎯 ANÁLISIS DE PODER PREDICTIVO
    # ════════════════════════════════════════════════════════════
    
    @staticmethod
    def calculate_hit_rate(predictions: np.ndarray, actuals: np.ndarray) -> float:
        """
        Calcula porcentaje de aciertos.
        """
        if len(predictions) == 0:
            return 0.0
        return (np.sum(predictions == actuals) / len(predictions)) * 100
    
    # ════════════════════════════════════════════════════════════
    # 🔧 UTILIDADES
    # ════════════════════════════════════════════════════════════
    
    @staticmethod
    def clean_multiindex_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Limpia MultiIndex de columnas (común en yfinance).
        """
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    
    @staticmethod
    def filter_valid_bars(df: pd.DataFrame, min_spread: float = 0.0, max_spread: float = 60.0) -> pd.DataFrame:
        """
        Filtra velas válidas (sin gaps, spreads razonables).
        """
        df = df[df['High'] > df['Low']].copy()  # Velas válidas
        df['Spread%'] = QuantEngine.calculate_spread(df['High'], df['Low'], df['Low'])
        df = df[(df['Spread%'] >= min_spread) & (df['Spread%'] <= max_spread)].copy()
        return df

# Instancia global
qe = QuantEngine()

if __name__ == '__main__':
    # Test
    print(QuantEngine.calculate_spread(100, 95))
    print(QuantEngine.calculate_mfe(100, 105, 92))
    print(QuantEngine.calculate_clv(98, 102, 94))
