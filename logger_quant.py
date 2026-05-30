"""
═══════════════════════════════════════════════════════════════
📝 LOGGER_QUANT.PY - SISTEMA DE LOGGING UNIFICADO
═══════════════════════════════════════════════════════════════
Registro centralizado con niveles, timestamps y persistencia.
"""

import logging
import os
from datetime import datetime
from typing import Optional
from config import LOGGING_CONFIG, PATHS

class QuantLogger:
    """
    Logger unificado para todo el ecosistema QUANT.
    - Escribe en consola Y archivo simultáneamente
    - Colores en consola (emojis + colores ANSI)
    - Timestamp único
    """
    
    _instance = None
    _loggers = {}  # Dict de loggers por módulo
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(QuantLogger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._setup_root_logger()
    
    def _setup_root_logger(self):
        """Configura el logger raíz."""
        self.root_logger = logging.getLogger('quant')
        self.root_logger.setLevel(logging.DEBUG)
        
        # Formato
        formatter = logging.Formatter(
            LOGGING_CONFIG['format'],
            datefmt=LOGGING_CONFIG['date_format']
        )
        
        # Handler: Archivo
        file_handler = logging.FileHandler(LOGGING_CONFIG['log_file'])
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.root_logger.addHandler(file_handler)
        
        # Handler: Consola
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.root_logger.addHandler(console_handler)
    
    def get_logger(self, module_name: str) -> logging.Logger:
        """Obtiene o crea un logger para un módulo específico."""
        if module_name not in self._loggers:
            self._loggers[module_name] = logging.getLogger(f'quant.{module_name}')
        return self._loggers[module_name]
    
    @staticmethod
    def info(message: str, module: Optional[str] = None):
        """Log nivel INFO."""
        logger = QuantLogger().get_logger(module or 'main')
        logger.info(f"ℹ️  {message}")
    
    @staticmethod
    def debug(message: str, module: Optional[str] = None):
        """Log nivel DEBUG."""
        logger = QuantLogger().get_logger(module or 'main')
        logger.debug(f"🔍 {message}")
    
    @staticmethod
    def warning(message: str, module: Optional[str] = None):
        """Log nivel WARNING."""
        logger = QuantLogger().get_logger(module or 'main')
        logger.warning(f"⚠️  {message}")
    
    @staticmethod
    def error(message: str, module: Optional[str] = None):
        """Log nivel ERROR."""
        logger = QuantLogger().get_logger(module or 'main')
        logger.error(f"❌ {message}")
    
    @staticmethod
    def success(message: str, module: Optional[str] = None):
        """Log de éxito (customizado)."""
        logger = QuantLogger().get_logger(module or 'main')
        logger.info(f"✅ {message}")
    
    @staticmethod
    def section(title: str, module: Optional[str] = None):
        """Imprime sección de título."""
        logger = QuantLogger().get_logger(module or 'main')
        sep = "="*70
        logger.info(f"\n{sep}\n 📊 {title}\n{sep}")
    
    @staticmethod
    def metric(label: str, value: any, unit: str = '', module: Optional[str] = None):
        """Log de métrica."""
        logger = QuantLogger().get_logger(module or 'main')
        logger.info(f"📈 {label}: {value} {unit}")

# Alias global para acceso rápido
log = QuantLogger()

if __name__ == '__main__':
    log.section('Test Logger', 'test')
    log.info('Mensaje informativo', 'test')
    log.debug('Mensaje debug', 'test')
    log.warning('Mensaje de advertencia', 'test')
    log.error('Mensaje de error', 'test')
    log.success('Operación exitosa', 'test')
    log.metric('Precio', 42.50, 'USD', 'test')
