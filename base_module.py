"""
═══════════════════════════════════════════════════════════════
🏗️ BASE_MODULE.PY - CLASE BASE PARA TODOS LOS MÓDULOS
═══════════════════════════════════════════════════════════════
Define estructura común, ciclo de vida e interfaz.
"""

import json
import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional
import pandas as pd

from config import ECOSYSTEM, PATHS, JSON_FILES
from logger_quant import log
from data_provider import data_provider

class QuantModule(ABC):
    """
    Clase base para todos los módulos del ecosistema QUANT.
    
    Estructura garantizada:
    1. __init__: Inicializa config y logger
    2. validate_inputs: Valida datos de entrada
    3. execute: Lógica principal del módulo (abstracto)
    4. export_results: Exporta a JSON/CSV/PNG
    5. cleanup: Limpieza de recursos
    """
    
    def __init__(self, module_name: str, ticker: str = None, debug: bool = False):
        self.module_name = module_name
        self.ticker = ticker or ECOSYSTEM['primary_ticker']
        self.debug = debug
        self.logger = log.get_logger(module_name)
        self.results = {}
        self.dataframes = {}
        self.start_time = datetime.now()
        
        log.section(f"Inicializando {module_name}", module_name)
        log.info(f"Ticker: {self.ticker}", module_name)
    
    @abstractmethod
    def validate_inputs(self) -> bool:
        """
        Valida que existan datos y dependencias necesarias.
        
        Returns:
            bool: True si validación es exitosa
        """
        pass
    
    @abstractmethod
    def execute(self) -> Dict[str, Any]:
        """
        Lógica principal del módulo.
        
        Returns:
            Dict con resultados
        """
        pass
    
    def export_json(self, filename: str, data: Dict[str, Any]):
        """
        Exporta resultados a JSON.
        
        Args:
            filename: Nombre del archivo (sin .json)
            data: Diccionario a exportar
        """
        try:
            filepath = os.path.join(PATHS['outputs'], f"{filename}.json")
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4, default=str)
            log.success(f"JSON exportado: {filename}.json", self.module_name)
            return filepath
        except Exception as e:
            log.error(f"Error exportando JSON: {e}", self.module_name)
            return None
    
    def export_csv(self, filename: str, df: pd.DataFrame):
        """
        Exporta DataFrame a CSV.
        
        Args:
            filename: Nombre del archivo (sin .csv)
            df: DataFrame a exportar
        """
        try:
            filepath = os.path.join(PATHS['outputs'], f"{filename}.csv")
            df.to_csv(filepath)
            log.success(f"CSV exportado: {filename}.csv", self.module_name)
            return filepath
        except Exception as e:
            log.error(f"Error exportando CSV: {e}", self.module_name)
            return None
    
    def export_png(self, filename: str, fig):
        """
        Exporta figura matplotlib a PNG.
        
        Args:
            filename: Nombre del archivo (sin .png)
            fig: Figura matplotlib
        """
        try:
            filepath = os.path.join(PATHS['reports'], f"{filename}.png")
            fig.savefig(filepath, dpi=100, bbox_inches='tight')
            log.success(f"PNG exportado: {filename}.png", self.module_name)
            return filepath
        except Exception as e:
            log.error(f"Error exportando PNG: {e}", self.module_name)
            return None
    
    def load_json(self, filename: str) -> Optional[Dict]:
        """
        Carga datos de archivo JSON.
        
        Args:
            filename: Clave de JSON_FILES o ruta completa
        
        Returns:
            Dict si existe, None si no
        """
        try:
            if filename in JSON_FILES:
                filepath = JSON_FILES[filename]
            else:
                filepath = os.path.join(PATHS['outputs'], f"{filename}.json")
            
            if not os.path.exists(filepath):
                log.warning(f"Archivo JSON no encontrado: {filename}", self.module_name)
                return None
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            return data
        except Exception as e:
            log.error(f"Error cargando JSON: {e}", self.module_name)
            return None
    
    def run(self) -> bool:
        """
        Ejecuta el ciclo completo del módulo.
        
        Returns:
            bool: True si todo fue exitoso
        """
        try:
            # 1. Validar
            if not self.validate_inputs():
                log.error("Validación de inputs fallida", self.module_name)
                return False
            
            # 2. Ejecutar
            self.results = self.execute()
            
            # 3. Reportar
            elapsed = (datetime.now() - self.start_time).total_seconds()
            log.success(f"Módulo completado en {elapsed:.2f}s", self.module_name)
            
            return True
        
        except Exception as e:
            log.error(f"Error en run(): {e}", self.module_name)
            return False
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """
        Limpieza de recursos (override si necesario).
        """
        pass
    
    def print_summary(self):
        """
        Imprime resumen de ejecución.
        """
        log.section("RESUMEN DEL MÓDULO", self.module_name)
        print(json.dumps(self.results, indent=2, default=str))

if __name__ == '__main__':
    # Ejemplo de uso
    class ExampleModule(QuantModule):
        def validate_inputs(self) -> bool:
            return True
        
        def execute(self) -> Dict[str, Any]:
            return {'status': 'ok', 'value': 42}
    
    module = ExampleModule('example_module')
    module.run()
    module.print_summary()
