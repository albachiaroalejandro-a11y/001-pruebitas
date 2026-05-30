"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  🖥️ DASHBOARD.PY - INTERFAZ VISUAL DEL ECOSISTEMA QUANT                       ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Dashboard interactivo con:  TUI (Terminal UI), gráficos en tiempo real, estado de módulos
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import curses
import threading
import time
from pathlib import Path

from config import ECOSYSTEM, PATHS, MODULES_ENABLED, SCHEDULE, JSON_FILES
from logger_quant import log

class Colors:
    """Definición de colores ANSI."""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Foreground
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Background
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'

class Dashboard:
    """
    Dashboard TUI para monitoreo de ecosistema QUANT.
    """
    
    def __init__(self):
        self.ecosystem = ECOSYSTEM
        self.module_status = self._init_module_status()
        self.last_update = datetime.now()
        self.running = True
        self.selected_module = 0
        
    def _init_module_status(self) -> Dict[str, Dict[str, Any]]:
        """Inicializa estado de todos los módulos."""
        status = {}
        for module, enabled in MODULES_ENABLED.items():
            status[module] = {
                'enabled': enabled,
                'status': '⏸️ IDLE',
                'last_run': None,
                'duration': 0,
                'result': 'pending',
                'health': '🟢 OK',
            }
        return status
    
    def print_header(self):
        """Imprime encabezado del dashboard."""
        os.system('clear' if os.name == 'posix' else 'cls')
        
        title = f" {self.ecosystem['name']} v{self.ecosystem['version']} "
        border = "═" * 100
        
        print(f"{Colors.BOLD}{Colors.CYAN}╔{border}╗{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}║{Colors.BG_BLUE}{Colors.WHITE}{title:^100}{Colors.RESET}{Colors.CYAN}║{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}╠{border}╣{Colors.RESET}")
        
        # Info rápida
        info_line = f" 🚀 Ticker: {self.ecosystem['primary_ticker']} | 🏢 Broker: {self.ecosystem['default_broker']} | 📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} "
        print(f"{Colors.CYAN}║{info_line:<100}║{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}╚{border}╝{Colors.RESET}\n")
    
    def print_modules_section(self):
        """Imprime sección de módulos con estado."""
        print(f"{Colors.BOLD}{Colors.YELLOW}📦 MÓDULOS DEL ECOSISTEMA{Colors.RESET}\n")
        
        modules_list = [
            ('00_calibrador', '⚙️ Calibración Matinal', 'Inicializa parámetros diarios'),
            ('01_master_semanal', '📊 Master Semanal', 'Análisis estratégico semanal'),
            ('02_master_intradiario', '🕒 Master Intradiario', 'Análisis de alta frecuencia'),
            ('03_master_cierres', '🎯 Master Cierres', 'Mapeo probabilístico CLV'),
            ('04_master_screeners', '🔍 Master Screeners', 'Identificación pares/oportunidades'),
            ('05_monitor_tactico', '📡 Monitor Táctico', 'Monitoreo en tiempo real'),
        ]
        
        for i, (key, emoji_name, desc) in enumerate(modules_list):
            status = self.module_status.get(key, {})
            enabled = status.get('enabled', False)
            health = status.get('health', '🔴 ERROR')
            module_status = status.get('status', '⏸️ IDLE')
            
            selector = "➤" if i == self.selected_module else " "
            enabled_str = f"{Colors.GREEN}✓ HABILITADO{Colors.RESET}" if enabled else f"{Colors.RED}✗ DESHABILITADO{Colors.RESET}"
            
            print(f"  {selector} {emoji_name:<30} {enabled_str:<25} {module_status:<20} {health}")
            print(f"     └─ {Colors.DIM}{desc}{Colors.RESET}")
            print()
    
    def print_status_dashboard(self):
        """Imprime dashboard de estado."""
        print(f"{Colors.BOLD}{Colors.MAGENTA}📈 ESTADO ACTUAL{Colors.RESET}\n")
        
        # Cajas de métricas
        metrics = [
            ('Módulos Activos', f"{sum(1 for m in self.module_status.values() if m['enabled'])}/{len(self.module_status)}", '🟢'),
            ('Ejecuciones Hoy', '0', '📊'),
            ('Tasa de Éxito', '100%', '✓'),
            ('Última Actualización', self.last_update.strftime('%H:%M:%S'), '⏰'),
        ]
        
        for label, value, emoji in metrics:
            print(f"  {emoji} {label:<25}: {Colors.BOLD}{Colors.CYAN}{value}{Colors.RESET}")
        
        print()
    
    def print_schedule(self):
        """Imprime calendario de ejecuciones."""
        print(f"{Colors.BOLD}{Colors.GREEN}📅 CALENDARIO DE EJECUCIONES{Colors.RESET}\n")
        
        for module, time_sched in SCHEDULE.items():
            enabled = MODULES_ENABLED.get(module, False)
            if enabled:
                status_icon = "🟢"
                status_text = f"{Colors.GREEN}PROGRAMADO{Colors.RESET}"
            else:
                status_icon = "🔴"
                status_text = f"{Colors.RED}DESHABILITADO{Colors.RESET}"
            
            print(f"  {status_icon} {module:<30} → {time_sched:<20} {status_text}")
        
        print()
    
    def print_data_flow(self):
        """Imprime flujo de datos entre módulos."""
        print(f"{Colors.BOLD}{Colors.BLUE}🔄 FLUJO DE DATOS (JSON){Colors.RESET}\n")
        
        flow = [
            ("00_calibrador", "parametros_ggal.json", "01, 02, 03"),
            ("01_master_semanal", "weekly_report.json", "conserje"),
            ("02_master_intradiario", "intraday_report.json", "conserje"),
            ("03_master_cierres", "cierres_report.json", "conserje"),
            ("04_master_screeners", "watchlist_ideal.json", "05_monitor"),
            ("05_monitor_tactico", "positions_vivas.json", "conserje"),
        ]
        
        print(f"  {'Origen':<25} {'Output':<30} {'Destino':<20}")
        print(f"  {'-'*75}")
        
        for origen, output, destino in flow:
            print(f"  {origen:<25} ➜ {Colors.CYAN}{output:<28}{Colors.RESET} ➜ {destino}")
        
        print()
    
    def print_file_structure(self):
        """Imprime estructura de directorios."""
        print(f"{Colors.BOLD}{Colors.YELLOW}📁 ESTRUCTURA DE DIRECTORIOS{Colors.RESET}\n")
        
        structure = {
            'BASE': {
                'config.py': '⚙️ Config centralizada',
                'logger_quant.py': '📝 Sistema de logging',
                'data_provider.py': '📥 Proveedor de datos',
                'quant_engine.py': '🔧 Motor de cálculos',
                'base_module.py': '🏗️ Clase base módulos',
                'conserje.py': '🤖 Orquestador maestro',
            },
            'MÓDULOS': {
                '00_calibrador_matinal.py': '⚙️ Calibración',
                '01_master_semanal.py': '📊 Análisis semanal',
                '02_master_intradiario.py': '🕒 Análisis intradia',
                '03_master_cierres.py': '🎯 Cierres',
                '04_master_screeners.py': '🔍 Screeners',
                '05_monitor_tactico.py': '📡 Monitor',
            },
            'DATA': {
                'cache/': '💾 Caché de datos',
                'outputs/': '📤 Salidas procesadas',
                'reports/': '📊 Reportes/Gráficos',
                'logs/': '📝 Logs de ejecución',
                'params/': '⚙️ Parámetros JSON',
            }
        }
        
        for section, files in structure.items():
            print(f"  {Colors.BOLD}{Colors.CYAN}{section}{Colors.RESET}")
            for file, desc in files.items():
                print(f"    ├─ {desc:<40} → {file}")
            print()
    
    def print_quick_commands(self):
        """Imprime comandos disponibles."""
        print(f"{Colors.BOLD}{Colors.GREEN}⌨️ COMANDOS DISPONIBLES{Colors.RESET}\n")
        
        commands = [
            ('r', 'Ejecutar módulo seleccionado'),
            ('a', 'Ejecutar TODOS los módulos'),
            ('↑/↓', 'Navegar módulos'),
            ('c', 'Limpiar caché de datos'),
            ('l', 'Ver últimos logs'),
            ('o', 'Abrir carpeta outputs'),
            ('h', 'Mostrar esta ayuda'),
            ('q', 'Salir'),
        ]
        
        for cmd, desc in commands:
            print(f"  [{Colors.BOLD}{Colors.YELLOW}{cmd}{Colors.RESET}] {desc}")
        
        print()
    
    def print_system_info(self):
        """Imprime información del sistema."""
        print(f"{Colors.BOLD}{Colors.CYAN}ℹ️ INFORMACIÓN DEL SISTEMA{Colors.RESET}\n")
        
        import platform
        
        info = [
            ('OS', platform.system()),
            ('Python', platform.python_version()),
            ('Base Directory', PATHS['base']),
            ('Cache Directory', PATHS['cache']),
            ('Outputs Directory', PATHS['outputs']),
        ]
        
        for label, value in info:
            print(f"  {label:<20}: {Colors.DIM}{value}{Colors.RESET}")
        
        print()
    
    def print_footer(self):
        """Imprime footer del dashboard."""
        border = "═" * 100
        footer_text = f" Presiona [h] para ayuda | [q] para salir "
        
        print(f"{Colors.BOLD}{Colors.CYAN}╠{border}╣{Colors.RESET}")
        print(f"{Colors.CYAN}║{footer_text:^100}║{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}╚{border}╝{Colors.RESET}")
    
    def show(self):
        """Muestra el dashboard completo."""
        self.print_header()
        self.print_modules_section()
        self.print_status_dashboard()
        self.print_schedule()
        self.print_data_flow()
        self.print_file_structure()
        self.print_quick_commands()
        self.print_system_info()
        self.print_footer()
    
    def show_help(self):
        """Muestra pantalla de ayuda."""
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print(f"{Colors.BOLD}{Colors.CYAN}╔{'═'*100}╗{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}║{'AYUDA Y DOCUMENTACIÓN RÁPIDA':^100}║{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}╚{'═'*100}╝{Colors.RESET}\n")
        
        help_sections = {
            '🎯 OBJETIVO DEL ECOSISTEMA': [
                'Sistema modular para trading algorítmico en Argentina (GGAL ADR)',
                'Análisis cuantitativo de múltiples timeframes',
                'Integración de screeners y estrategias de pairs trading',
            ],
            '⚙️ ARQUITECTURA': [
                'config.py: Configuración centralizada (NO repetir parámetros)',
                'data_provider.py: Abstracción de datos con caché automático',
                'quant_engine.py: Funciones reutilizables (Z-Score, MFE, CLV, Hurst)',
                'logger_quant.py: Logging unificado con persistencia',
                'base_module.py: Interfaz común para todos los módulos',
            ],
            '📦 MÓDULOS PRINCIPALES': [
                '00_calibrador_matinal: Parámetros iniciales diarios',
                '01_master_semanal: Volatilidad, poder predictivo, targets',
                '02_master_intradiario: Amplitudes, correlaciones caja/día',
                '03_master_cierres: CLV probabilístico + heatmap',
                '04_master_screeners: Pairs cointegrados + oportunidades',
                '05_monitor_tactico: Tracking de posiciones abiertas',
            ],
            '🔄 FLUJO DE DATOS': [
                'Cada módulo lee de config.py',
                'Descarga con data_provider (con caché)',
                'Calcula con quant_engine (funciones comunes)',
                'Exporta JSON para siguiente módulo',
                'conserje.py orquesta la secuencia',
            ],
            '💡 BUENAS PRÁCTICAS': [
                '❌ NO hardcodear parámetros → USE config.py',
                '❌ NO descargar dos veces → USE data_provider con caché',
                '❌ NO duplicar código → USE quant_engine',
                '❌ NO print() → USE logger_quant.log',
                '✅ Extender QuantModule para nuevos módulos',
            ],
            '🚀 PRÓXIMOS PASOS': [
                'Refactorizar 01_master_semanal.py',
                'Refactorizar 02_master_intradiario.py',
                'Crear conserje.py (orquestador)',
                'Integrar credenciales.py y universo.py',
                'Escribir tests unitarios',
            ],
        }
        
        for section, items in help_sections.items():
            print(f"{Colors.BOLD}{Colors.YELLOW}{section}{Colors.RESET}\n")
            for item in items:
                print(f"  • {item}")
            print()
        
        print(f"{Colors.DIM}Presiona ENTER para volver...{Colors.RESET}")
        input()
        self.show()

def print_ascii_art():
    """Imprime arte ASCII de bienvenida."""
    art = f"""
{Colors.BOLD}{Colors.CYAN}
╔═══════════════════════════════════════════════════════════════════════════════╗
║                      🚀 QUANT TRADING ECOSYSTEM 🚀                            ║
║                                                                               ║
║          Sistema Modular de Análisis Cuantitativo para Trading ADRs          ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  Módulos:  📊 Semanal  |  🕒 Intradiario  |  🎯 Cierres  |  🔍 Screeners    ║
║                                                                               ║
║  Engine:   ⚙️ Config  |  📥 Data  |  🔧 Quant  |  📝 Logger  |  🏗️ Base     ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
{Colors.RESET}
    """
    print(art)

def main():
    """Función principal - Inicia dashboard."""
    dashboard = Dashboard()
    
    print_ascii_art()
    time.sleep(1)
    
    while dashboard.running:
        dashboard.show()
        
        cmd = input(f"{Colors.BOLD}{Colors.YELLOW}>>> {Colors.RESET}").strip().lower()
        
        if cmd == 'q':
            print(f"{Colors.GREEN}✅ ¡Hasta pronto!{Colors.RESET}")
            dashboard.running = False
        elif cmd == 'h':
            dashboard.show_help()
        elif cmd == 'r':
            print(f"{Colors.YELLOW}⚠️ Ejecutando módulo (función no implementada){Colors.RESET}")
            time.sleep(1)
        elif cmd == 'a':
            print(f"{Colors.YELLOW}⚠️ Ejecutando todos los módulos (función no implementada){Colors.RESET}")
            time.sleep(1)
        elif cmd == 'c':
            print(f"{Colors.YELLOW}⚠️ Limpiando caché (función no implementada){Colors.RESET}")
            time.sleep(1)
        elif cmd == 'l':
            print(f"{Colors.YELLOW}⚠️ Ver logs (función no implementada){Colors.RESET}")
            time.sleep(1)
        elif cmd == 'o':
            print(f"{Colors.YELLOW}⚠️ Abriendo outputs (función no implementada){Colors.RESET}")
            time.sleep(1)
        elif cmd == '↑':
            dashboard.selected_module = max(0, dashboard.selected_module - 1)
        elif cmd == '↓':
            dashboard.selected_module = min(5, dashboard.selected_module + 1)
        else:
            if cmd:
                print(f"{Colors.RED}❌ Comando desconocido. Presiona [h] para ayuda{Colors.RESET}")
            time.sleep(0.5)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.GREEN}✅ Programa interrumpido{Colors.RESET}")
        sys.exit(0)
