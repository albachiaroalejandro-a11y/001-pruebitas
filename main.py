#!/usr/bin/env python3
"""
╔════════════════════════════════════════════════════════════════════════════════════════╗
║  🚀 MAIN.PY - PUNTO DE ENTRADA DEL ECOSISTEMA QUANT                                   ║
╚════════════════════════════════════════════════════════════════════════════════════════╝

Guía de ejecución completa del ecosistema.
"""

import sys
import os
from pathlib import Path

# Agregar directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from logger_quant import log
from config import ECOSYSTEM, PATHS, MODULES_ENABLED
from dashboard import Dashboard, print_ascii_art, Colors


def print_welcome():
    """Imprime pantalla de bienvenida."""
    print_ascii_art()
    print(f"{Colors.GREEN}✅ Todos los módulos importados correctamente{Colors.RESET}\n")
    print(f"{Colors.CYAN}Sistema: {ECOSYSTEM['name']} v{ECOSYSTEM['version']}{Colors.RESET}")
    print(f"{Colors.CYAN}Directorio base: {PATHS['base']}{Colors.RESET}\n")


def print_menu():
    """Imprime menú principal."""
    print(f"{Colors.BOLD}{Colors.YELLOW}\n═══════════════════════════════════════════════════════════════════{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.YELLOW}              📊 MENÚ PRINCIPAL - QUANT TRADING ECOSYSTEM{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.YELLOW}═══════════════════════════════════════════════════════════════════{Colors.RESET}\n")
    
    print(f"{Colors.GREEN}[1]{Colors.RESET} 📊 Mostrar Dashboard Interactivo (TUI)")
    print(f"{Colors.GREEN}[2]{Colors.RESET} 📄 Generar Reporte HTML")
    print(f"{Colors.GREEN}[3]{Colors.RESET} ⚙️  Ejecutar Módulo Individual")
    print(f"{Colors.GREEN}[4]{Colors.RESET} 🔄 Ejecutar Todos los Módulos (Secuencia)")
    print(f"{Colors.GREEN}[5]{Colors.RESET} 📋 Ver Configuración del Sistema")
    print(f"{Colors.GREEN}[6]{Colors.RESET} 📝 Ver Últimos Logs")
    print(f"{Colors.GREEN}[7]{Colors.RESET} 🧹 Limpiar Caché")
    print(f"{Colors.GREEN}[q]{Colors.RESET} ❌ Salir\n")
    
    print(f"{Colors.BOLD}{Colors.YELLOW}═══════════════════════════════════════════════════════════════════{Colors.RESET}\n")


def option_dashboard():
    """Opción 1: Mostrar dashboard."""
    print(f"\n{Colors.CYAN}Iniciando Dashboard...{Colors.RESET}\n")
    dashboard = Dashboard()
    dashboard.show()
    
    while dashboard.running:
        cmd = input(f"{Colors.BOLD}{Colors.YELLOW}>>> {Colors.RESET}").strip().lower()
        
        if cmd == 'q':
            print(f"{Colors.GREEN}✅ Volviendo al menú principal...{Colors.RESET}\n")
            dashboard.running = False
        elif cmd == 'h':
            dashboard.show_help()
        else:
            print(f"{Colors.YELLOW}⚠️  Opción en desarrollo...{Colors.RESET}")
            dashboard.show()


def option_html_report():
    """Opción 2: Generar reporte HTML."""
    print(f"\n{Colors.CYAN}Generando reporte HTML...{Colors.RESET}")
    
    try:
        from visualizer import ReportBuilder
        
        html = ReportBuilder.build_ecosystem_report()
        filepath = ReportBuilder.save_report(html)
        
        print(f"{Colors.GREEN}✅ Reporte generado: {filepath}{Colors.RESET}")
        print(f"{Colors.CYAN}💡 Abre este archivo en tu navegador para verlo{Colors.RESET}\n")
        
        # Intentar abrir en navegador
        import webbrowser
        try:
            webbrowser.open(f'file://{os.path.abspath(filepath)}')
            print(f"{Colors.GREEN}✅ Abriendo en navegador...{Colors.RESET}\n")
        except:
            print(f"{Colors.YELLOW}⚠️  No se pudo abrir automáticamente. Abre manualmente: {filepath}{Colors.RESET}\n")
    
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.RESET}\n")


def option_run_module():
    """Opción 3: Ejecutar módulo individual."""
    print(f"\n{Colors.CYAN}Módulos disponibles:{Colors.RESET}\n")
    
    modules = list(MODULES_ENABLED.keys())
    for i, module in enumerate(modules, 1):
        status = "✓" if MODULES_ENABLED[module] else "✗"
        print(f"  [{i}] {status} {module}")
    
    try:
        choice = input(f"\n{Colors.YELLOW}Selecciona módulo (número): {Colors.RESET}").strip()
        idx = int(choice) - 1
        
        if 0 <= idx < len(modules):
            module_name = modules[idx]
            
            if not MODULES_ENABLED[module_name]:
                print(f"{Colors.RED}❌ Módulo deshabilitado en config.py{Colors.RESET}\n")
                return
            
            print(f"\n{Colors.CYAN}Ejecutando {module_name}...{Colors.RESET}")
            print(f"{Colors.YELLOW}⚠️  (Función en desarrollo - próximamente integrado){Colors.RESET}\n")
        else:
            print(f"{Colors.RED}❌ Selección inválida{Colors.RESET}\n")
    except ValueError:
        print(f"{Colors.RED}❌ Ingresa un número válido{Colors.RESET}\n")


def option_run_all():
    """Opción 4: Ejecutar todos los módulos."""
    print(f"\n{Colors.CYAN}Secuencia de ejecución:{Colors.RESET}\n")
    
    sequence = [
        ('06:00', '00_calibrador_matinal', '⚙️'),
        ('09:00', '02_master_intradiario', '🕒'),
        ('16:00', '01_master_semanal', '📊'),
        ('17:00', '03_master_cierres', '🎯'),
        ('19:00', '04_master_screeners', '🔍'),
        ('24/7', '05_monitor_tactico', '📡'),
    ]
    
    for time, module, emoji in sequence:
        if MODULES_ENABLED.get(module, False):
            status = f"{Colors.GREEN}✓ HABILITADO{Colors.RESET}"
        else:
            status = f"{Colors.RED}✗ DESHABILITADO{Colors.RESET}"
        
        print(f"  {emoji} [{time}] {module:<30} {status}")
    
    print(f"\n{Colors.YELLOW}⚠️  (Orquestación en conserje.py - próximamente){Colors.RESET}\n")


def option_config():
    """Opción 5: Ver configuración del sistema."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}═══════════════════════════════════════════════════════════════{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}         CONFIGURACIÓN DEL ECOSISTEMA{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}═══════════════════════════════════════════════════════════════{Colors.RESET}\n")
    
    print(f"{Colors.BOLD}{Colors.YELLOW}🌐 METADATA{Colors.RESET}")
    print(f"  Nombre: {ECOSYSTEM['name']}")
    print(f"  Versión: {ECOSYSTEM['version']}")
    print(f"  Ticker Principal: {ECOSYSTEM['primary_ticker']}")
    print(f"  Broker Predeterminado: {ECOSYSTEM['default_broker']}")
    
    print(f"\n{Colors.BOLD}{Colors.YELLOW}📁 DIRECTORIOS{Colors.RESET}")
    for key, path in PATHS.items():
        exists = "✓" if os.path.exists(path) else "✗"
        print(f"  {exists} {key:<15}: {path}")
    
    print(f"\n{Colors.BOLD}{Colors.YELLOW}📦 MÓDULOS{Colors.RESET}")
    enabled = sum(1 for v in MODULES_ENABLED.values() if v)
    total = len(MODULES_ENABLED)
    print(f"  Habilitados: {Colors.GREEN}{enabled}/{total}{Colors.RESET}")
    for module, enabled in MODULES_ENABLED.items():
        status = f"{Colors.GREEN}✓{Colors.RESET}" if enabled else f"{Colors.RED}✗{Colors.RESET}"
        print(f"    {status} {module}")
    
    print()


def option_logs():
    """Opción 6: Ver últimos logs."""
    print(f"\n{Colors.CYAN}Últimos logs:{Colors.RESET}\n")
    
    log_file = Path(PATHS['logs']) / f"quant_{log.root_logger.handlers[0].baseFilename.split('/')[-1]}"
    
    try:
        log_path = list(Path(PATHS['logs']).glob('quant_*.log'))
        
        if not log_path:
            print(f"{Colors.YELLOW}⚠️  No hay logs disponibles aún{Colors.RESET}\n")
            return
        
        latest_log = sorted(log_path)[-1]
        
        with open(latest_log, 'r') as f:
            lines = f.readlines()
            last_20 = lines[-20:]
            
            for line in last_20:
                print(f"{Colors.DIM}{line.rstrip()}{Colors.RESET}")
    
    except Exception as e:
        print(f"{Colors.RED}❌ Error leyendo logs: {e}{Colors.RESET}")
    
    print()


def option_clear_cache():
    """Opción 7: Limpiar caché."""
    print(f"\n{Colors.YELLOW}⚠️  Limpiando caché...{Colors.RESET}")
    
    try:
        from data_provider import data_provider
        data_provider.clear_cache()
        print(f"{Colors.GREEN}✅ Caché limpiado exitosamente{Colors.RESET}\n")
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.RESET}\n")


def main():
    """Función principal."""
    log.info("Iniciando ecosistema QUANT", "main")
    
    print_welcome()
    
    while True:
        print_menu()
        cmd = input(f"{Colors.BOLD}{Colors.YELLOW}Tu opción: {Colors.RESET}").strip().lower()
        
        if cmd == '1':
            option_dashboard()
        elif cmd == '2':
            option_html_report()
        elif cmd == '3':
            option_run_module()
        elif cmd == '4':
            option_run_all()
        elif cmd == '5':
            option_config()
        elif cmd == '6':
            option_logs()
        elif cmd == '7':
            option_clear_cache()
        elif cmd == 'q':
            print(f"\n{Colors.GREEN}✅ ¡Hasta pronto!{Colors.RESET}\n")
            log.success("Ecosistema cerrado", "main")
            break
        else:
            if cmd:
                print(f"{Colors.RED}❌ Opción no válida. Intenta de nuevo.{Colors.RESET}\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.GREEN}✅ Programa interrumpido por el usuario{Colors.RESET}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error crítico: {e}{Colors.RESET}\n")
        log.error(f"Error en main: {e}", "main")
        sys.exit(1)
