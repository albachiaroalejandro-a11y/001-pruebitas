"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  📊 VISUALIZER.PY - GENERADOR DE REPORTES VISUALES (SVG + HTML)              ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Genera reportes HTML interactivos con gráficos en SVG.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import base64
from pathlib import Path

from config import PATHS, ECOSYSTEM
from logger_quant import log

class SVGGenerator:
    """Genera gráficos en SVG."""
    
    @staticmethod
    def create_gauge(value: float, min_val: float = 0, max_val: float = 100, 
                     label: str = "", width: int = 200, height: int = 200) -> str:
        """
        Crea un gráfico tipo "gauge" (velocímetro).
        """
        cx, cy = width // 2, height // 2
        radius = 80
        
        # Calcular ángulo
        angle = -90 + (value - min_val) / (max_val - min_val) * 180
        angle_rad = angle * 3.14159 / 180
        
        # Punto final de la aguja
        x_end = cx + radius * 0.7 * (angle_rad ** 0.5)
        y_end = cy + radius * 0.7 * (angle_rad ** 0.5)
        
        # Color según valor
        if value < max_val * 0.33:
            color = '#FF4444'  # Rojo
        elif value < max_val * 0.66:
            color = '#FFAA00'  # Naranja
        else:
            color = '#44AA44'  # Verde
        
        svg = f"""
        <svg width="{width}" height="{height}" viewBox="0 0 {width} {height}">
            <!-- Fondo -->
            <circle cx="{cx}" cy="{cy}" r="{radius}" fill="#f0f0f0" stroke="#333" stroke-width="2"/>
            
            <!-- Escala -->
            <text x="{width//2}" y="{height - 30}" text-anchor="middle" font-size="12" fill="#666">{label}</text>
            <text x="{width//2}" y="{height - 10}" text-anchor="middle" font-size="16" font-weight="bold" fill="#333">{value:.1f}</text>
            
            <!-- Aguja -->
            <line x1="{cx}" y1="{cy}" x2="{x_end}" y2="{y_end}" stroke="{color}" stroke-width="3" stroke-linecap="round"/>
            <circle cx="{cx}" cy="{cy}" r="5" fill="{color}"/>
        </svg>
        """
        return svg
    
    @staticmethod
    def create_bar_chart(data: Dict[str, float], title: str = "", 
                         width: int = 400, height: int = 250) -> str:
        """
        Crea un gráfico de barras.
        """
        if not data:
            return '<svg></svg>'
        
        margin = 40
        plot_width = width - 2 * margin
        plot_height = height - 2 * margin
        
        max_val = max(data.values())
        num_bars = len(data)
        bar_width = plot_width / num_bars * 0.8
        bar_spacing = plot_width / num_bars
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
        
        svg = f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
        svg += f'<text x="{width//2}" y="20" text-anchor="middle" font-size="16" font-weight="bold" fill="#333">{title}</text>'
        
        # Ejes
        svg += f'<line x1="{margin}" y1="{height - margin}" x2="{width - margin}" y2="{height - margin}" stroke="#333" stroke-width="2"/>'
        svg += f'<line x1="{margin}" y1="{margin}" x2="{margin}" y2="{height - margin}" stroke="#333" stroke-width="2"/>'
        
        # Barras
        for i, (label, value) in enumerate(data.items()):
            x = margin + i * bar_spacing + (bar_spacing - bar_width) / 2
            bar_height = (value / max_val) * plot_height if max_val > 0 else 0
            y = height - margin - bar_height
            
            color = colors[i % len(colors)]
            
            svg += f'<rect x="{x}" y="{y}" width="{bar_width}" height="{bar_height}" fill="{color}" stroke="#333" stroke-width="1"/>'
            svg += f'<text x="{x + bar_width/2}" y="{height - margin + 20}" text-anchor="middle" font-size="12" fill="#333">{label}</text>'
            svg += f'<text x="{x + bar_width/2}" y="{y - 5}" text-anchor="middle" font-size="11" fill="#666">{value:.2f}</text>'
        
        svg += '</svg>'
        return svg
    
    @staticmethod
    def create_line_chart(data: List[float], labels: List[str] = None, 
                          title: str = "", width: int = 600, height: int = 300) -> str:
        """
        Crea un gráfico de línea.
        """
        if not data:
            return '<svg></svg>'
        
        margin = 40
        plot_width = width - 2 * margin
        plot_height = height - 2 * margin
        
        max_val = max(data)
        min_val = min(data)
        range_val = max_val - min_val if max_val != min_val else 1
        
        # Calcular puntos
        points = []
        for i, value in enumerate(data):
            x = margin + (i / (len(data) - 1)) * plot_width if len(data) > 1 else margin + plot_width / 2
            y = height - margin - ((value - min_val) / range_val) * plot_height
            points.append((x, y))
        
        svg = f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
        svg += f'<text x="{width//2}" y="20" text-anchor="middle" font-size="16" font-weight="bold" fill="#333">{title}</text>'
        
        # Ejes
        svg += f'<line x1="{margin}" y1="{height - margin}" x2="{width - margin}" y2="{height - margin}" stroke="#333" stroke-width="2"/>'
        svg += f'<line x1="{margin}" y1="{margin}" x2="{margin}" y2="{height - margin}" stroke="#333" stroke-width="2"/>'
        
        # Línea
        if len(points) > 1:
            path_data = ' '.join([f"{'M' if i == 0 else 'L'} {x} {y}" for i, (x, y) in enumerate(points)])
            svg += f'<path d="{path_data}" stroke="#4ECDC4" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
        
        # Puntos
        for x, y in points:
            svg += f'<circle cx="{x}" cy="{y}" r="4" fill="#FF6B6B" stroke="#333" stroke-width="1"/>'
        
        svg += '</svg>'
        return svg

class HTMLReportGenerator:
    """Genera reportes HTML interactivos."""
    
    def __init__(self, title: str = "QUANT Trading Report"):
        self.title = title
        self.sections = []
    
    def add_section(self, title: str, content: str, icon: str = "📊"):
        """Añade una sección al reporte."""
        self.sections.append({
            'title': title,
            'content': content,
            'icon': icon
        })
    
    def add_metric_card(self, label: str, value: any, unit: str = "", 
                       status: str = "ok", icon: str = "📈") -> str:
        """Crea tarjeta de métrica."""
        status_color = {'ok': '#44AA44', 'warning': '#FFAA00', 'error': '#FF4444'}
        color = status_color.get(status, '#4ECDC4')
        
        html = f"""
        <div class="metric-card" style="border-left: 4px solid {color};">
            <div class="metric-icon">{icon}</div>
            <div class="metric-label">{label}</div>
            <div class="metric-value" style="color: {color};">{value}</div>
            <div class="metric-unit">{unit}</div>
        </div>
        """
        return html
    
    def generate_html(self, output_path: Optional[str] = None) -> str:
        """Genera HTML completo del reporte."""
        
        html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
            color: #ecf0f1;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        
        h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header-meta {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        
        .dashboard {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .metric-card {{
            background: #2d2d44;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0,0,0,0.2);
        }}
        
        .metric-icon {{
            font-size: 2em;
            margin-bottom: 10px;
        }}
        
        .metric-label {{
            font-size: 0.85em;
            color: #b0b0c0;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}
        
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .metric-unit {{
            font-size: 0.8em;
            color: #888;
        }}
        
        .section {{
            background: #2d2d44;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .section-title {{
            font-size: 1.5em;
            margin-bottom: 20px;
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .chart-container {{
            background: #1e1e2e;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            overflow-x: auto;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        th {{
            background: #3d3d54;
            padding: 12px;
            text-align: left;
            border-bottom: 2px solid #667eea;
            color: #667eea;
        }}
        
        td {{
            padding: 10px 12px;
            border-bottom: 1px solid #3d3d54;
        }}
        
        tr:hover {{
            background: #3d3d54;
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
            margin: 2px;
        }}
        
        .badge-success {{
            background: #44aa44;
            color: white;
        }}
        
        .badge-warning {{
            background: #ffaa00;
            color: #333;
        }}
        
        .badge-error {{
            background: #ff4444;
            color: white;
        }}
        
        footer {{
            text-align: center;
            padding: 20px;
            color: #888;
            border-top: 1px solid #3d3d54;
            margin-top: 40px;
        }}
        
        svg {{
            max-width: 100%;
            height: auto;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 {self.title}</h1>
            <div class="header-meta">
                <p>📅 Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>🌍 Ecosistema: {ECOSYSTEM['name']} v{ECOSYSTEM['version']}</p>
            </div>
        </header>
        """
        
        # Añadir secciones
        for section in self.sections:
            html += f"""
        <div class="section">
            <h2 class="section-title">{section['icon']} {section['title']}</h2>
            {section['content']}
        </div>
            """
        
        html += f"""
        <footer>
            <p>© 2026 QUANT Trading Ecosystem | Powered by Python</p>
        </footer>
    </div>
</body>
</html>
        """
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            log.success(f"HTML report generado: {output_path}", 'visualizer')
        
        return html

class ReportBuilder:
    """Constructor de reportes completos."""
    
    @staticmethod
    def build_ecosystem_report(json_data: Dict[str, Any] = None) -> str:
        """Construye reporte del ecosistema."""
        
        gen = HTMLReportGenerator("QUANT Trading Ecosystem Report")
        
        # Dashboard de métricas
        dashboard_html = '<div class="dashboard">'
        dashboard_html += gen.add_metric_card("Módulos Activos", "5/6", "", "ok", "📦")
        dashboard_html += gen.add_metric_card("Tasa de Éxito", "98.5%", "", "ok", "✓")
        dashboard_html += gen.add_metric_card("Última Ejecución", "14:32:45", "UTC", "ok", "⏰")
        dashboard_html += gen.add_metric_card("Caché Disponible", "2.3 GB", "", "ok", "💾")
        dashboard_html += '</div>'
        
        gen.add_section("Dashboard", dashboard_html, "📈")
        
        # Información de módulos
        modules_html = """
        <table>
            <thead>
                <tr>
                    <th>Módulo</th>
                    <th>Status</th>
                    <th>Última Ejecución</th>
                    <th>Duración</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>00_calibrador_matinal</td>
                    <td><span class="badge badge-success">✓ RUNNING</span></td>
                    <td>2026-05-30 06:00:00</td>
                    <td>3.2s</td>
                </tr>
                <tr>
                    <td>01_master_semanal</td>
                    <td><span class="badge badge-success">✓ OK</span></td>
                    <td>2026-05-30 16:00:00</td>
                    <td>5.1s</td>
                </tr>
                <tr>
                    <td>02_master_intradiario</td>
                    <td><span class="badge badge-success">✓ OK</span></td>
                    <td>2026-05-30 09:00:00</td>
                    <td>4.8s</td>
                </tr>
                <tr>
                    <td>03_master_cierres</td>
                    <td><span class="badge badge-success">✓ OK</span></td>
                    <td>2026-05-30 17:00:00</td>
                    <td>6.3s</td>
                </tr>
                <tr>
                    <td>04_master_screeners</td>
                    <td><span class="badge badge-warning">⚠ PENDING</span></td>
                    <td>2026-05-29 19:00:00</td>
                    <td>-</td>
                </tr>
                <tr>
                    <td>05_monitor_tactico</td>
                    <td><span class="badge badge-success">✓ LIVE</span></td>
                    <td>2026-05-30 14:32:45</td>
                    <td>∞</td>
                </tr>
            </tbody>
        </table>
        """
        gen.add_section("Estado de Módulos", modules_html, "📦")
        
        # Flujo de datos
        flow_html = """
        <p><strong>Cadena de Ejecución:</strong></p>
        <pre style="background: #1e1e2e; padding: 15px; border-radius: 5px; overflow-x: auto; color: #44aa44;">
06:00 → 00_calibrador (parametros_ggal.json)
    ↓
09:00 → 02_master_intradiario (intraday_report.json)
    ↓
16:00 → 01_master_semanal (weekly_report.json)
    ↓
17:00 → 03_master_cierres (cierres_report.json)
    ↓
19:00 → 04_master_screeners (watchlist_ideal.json)
    ↓
24/7  → 05_monitor_tactico (positions_vivas.json)
        </pre>
        """
        gen.add_section("Flujo de Datos", flow_html, "🔄")
        
        return gen.generate_html()
    
    @staticmethod
    def save_report(html_content: str, filename: str = "ecosystem_report.html") -> str:
        """Guarda reporte a archivo."""
        filepath = os.path.join(PATHS['reports'], filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        log.success(f"Reporte guardado: {filepath}", 'visualizer')
        return filepath

if __name__ == '__main__':
    # Generar reporte de ejemplo
    html = ReportBuilder.build_ecosystem_report()
    ReportBuilder.save_report(html)
    print("✅ Reporte generado exitosamente")
