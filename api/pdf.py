"""Geração do relatório PDF de sustentabilidade via WeasyPrint."""

from datetime import datetime, timezone
from weasyprint import HTML

GRADE_CONFIG = {
    'AAA': {'color': '#16a34a', 'bg': '#dcfce7', 'label': 'Green Software', 'efficiency': 97},
    'AA':  {'color': '#15803d', 'bg': '#d1fae5', 'label': 'Green Software', 'efficiency': 90},
    'A':   {'color': '#0d9488', 'bg': '#ccfbf1', 'label': 'Green Software', 'efficiency': 75},
    'B':   {'color': '#ca8a04', 'bg': '#fef9c3', 'label': 'Em Análise',     'efficiency': 55},
    'C':   {'color': '#dc2626', 'bg': '#fee2e2', 'label': 'Não Sustentável', 'efficiency': 30},
    'D':   {'color': '#9f1239', 'bg': '#ffe4e6', 'label': 'Não Sustentável', 'efficiency': 10},
}

REGION_NAMES = {
    'BR': 'Brasil', 'US': 'Estados Unidos', 'EU': 'Europa', 'DE': 'Alemanha',
    'FR': 'França', 'CN': 'China', 'IN': 'Índia', 'AU': 'Austrália',
    'GB': 'Reino Unido', 'GLOBAL': 'Global',
}

HARDWARE_NAMES = {
    'laptop': 'Notebook', 'desktop': 'Desktop', 'server': 'Servidor', 'cloud_vm': 'VM em Nuvem',
}


def _fmt_float(value, decimals=2) -> str:
    return f'{float(value):,.{decimals}f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


def _fmt_date(iso_str: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_str.replace('Z', '+00:00')).astimezone(
            timezone.utc
        )
        return dt.strftime('%d/%m/%Y %H:%M UTC')
    except Exception:
        return iso_str


def _build_html(analise) -> str:
    p = analise.payload
    m = p.get('metrics', {})
    grade = analise.grade
    cfg = GRADE_CONFIG.get(grade, GRADE_CONFIG['D'])
    efficiency = cfg['efficiency']
    sustainability_label = cfg['label']

    generated_at = datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M UTC')
    analysis_date = _fmt_date(p.get('timestamp', analise.created_at.isoformat()))

    region_code = analise.region.upper()
    region_name = REGION_NAMES.get(region_code, region_code)
    hardware_label = HARDWARE_NAMES.get(analise.hardware_type, analise.hardware_type)

    io_total_mb = float(m.get('io_read_mb', 0)) + float(m.get('io_write_mb', 0))
    duration_s = float(m.get('duration_seconds', 0))
    cpu_avg = float(m.get('cpu_percent_avg', 0))
    cpu_peak = float(m.get('cpu_percent_peak', 0))
    mem_avg = float(m.get('memory_used_mb_avg', 0))
    mem_peak = float(m.get('memory_used_mb_peak', 0))
    threads = int(m.get('threads_count', 0))

    grid_intensity = float(p.get('grid_intensity_gco2_kwh', 0))
    embodied_gco2 = float(p.get('embodied_carbon_gco2', 0))
    functional_unit = float(p.get('functional_unit', 1))

    # Carbon footprint estimados por recurso (proporcional ao consumo energético)
    energy_kwh = analise.energy_kwh
    total_carbon_gco2 = analise.sci_score * functional_unit
    cpu_fraction = cpu_avg / 100.0
    mem_fraction = min(mem_avg / (8 * 1024), 1.0)
    total_fraction = cpu_fraction + mem_fraction + 0.001
    cpu_carbon = total_carbon_gco2 * (cpu_fraction / total_fraction)
    mem_carbon = total_carbon_gco2 * (mem_fraction / total_fraction)
    io_carbon = total_carbon_gco2 - cpu_carbon - mem_carbon

    efficiency_bar_width = efficiency

    metrics_rows = [
        ('CPU', f'{_fmt_float(cpu_avg, 1)}%', f'{_fmt_float(cpu_peak, 1)}%', f'{_fmt_float(cpu_carbon)} gCO₂eq'),
        ('Memória', f'{_fmt_float(mem_avg)} MB', f'{_fmt_float(mem_peak)} MB', f'{_fmt_float(mem_carbon)} gCO₂eq'),
        ('I/O (Disco)', f'{_fmt_float(io_total_mb)} MB total', f'{_fmt_float(float(m.get("io_write_mb",0)))} MB gravados', f'{_fmt_float(io_carbon)} gCO₂eq'),
    ]

    metrics_rows_html = ''
    for resource, avg, peak, carbon in metrics_rows:
        metrics_rows_html += f'''
        <tr>
          <td>{resource}</td>
          <td>{avg}</td>
          <td>{peak}</td>
          <td>{carbon}</td>
        </tr>'''

    return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<style>
  @page {{
    margin: 20mm 18mm 18mm 18mm;
    size: A4;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 11px;
    color: #1a1a1a;
    line-height: 1.5;
  }}

  /* ── Cabeçalho ───────────────────────────────────── */
  .header {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding-bottom: 12px;
    border-bottom: 2.5px solid #16a34a;
    margin-bottom: 18px;
  }}
  .header-brand {{ display: flex; align-items: center; gap: 10px; }}
  .brand-icon {{
    width: 36px; height: 36px;
    background: #16a34a;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    color: white; font-size: 18px; font-weight: 900;
    flex-shrink: 0;
  }}
  .brand-title {{ font-size: 20px; font-weight: 800; color: #16a34a; }}
  .brand-subtitle {{ font-size: 10px; color: #666; margin-top: 1px; }}
  .header-meta {{ text-align: right; font-size: 10px; color: #555; }}
  .header-meta strong {{ display: block; font-size: 12px; color: #111; margin-bottom: 2px; }}

  /* ── Identificação ───────────────────────────────── */
  .identification {{
    background: #f8fafb;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 16px;
  }}
  .identification h2 {{
    font-size: 11px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.06em; color: #555; margin-bottom: 8px;
  }}
  .id-grid {{
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;
  }}
  .id-item label {{ font-size: 9px; color: #888; text-transform: uppercase; letter-spacing: 0.05em; }}
  .id-item span {{ display: block; font-size: 11px; font-weight: 600; color: #111; }}

  /* ── Visão geral (3 cards) ───────────────────────── */
  .overview {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px; }}
  .card {{
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 12px 14px;
    background: #fff;
  }}
  .card-label {{ font-size: 9px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: #888; margin-bottom: 6px; }}
  .card-value {{ font-size: 22px; font-weight: 800; color: #16a34a; }}
  .card-unit {{ font-size: 11px; color: #666; margin-top: 2px; }}
  .card-desc {{ font-size: 9.5px; color: #555; margin-top: 4px; }}

  /* grade badge */
  .grade-badge {{
    display: inline-block;
    font-size: 28px; font-weight: 900;
    padding: 4px 14px;
    border-radius: 8px;
    color: {cfg['color']};
    background: {cfg['bg']};
  }}
  .sustainability-status {{
    font-size: 13px; font-weight: 700;
    color: {cfg['color']};
    margin-top: 4px;
  }}

  /* efficiency bar */
  .eff-bar-bg {{
    height: 8px; background: #e2e8f0; border-radius: 4px; margin-top: 8px; overflow: hidden;
  }}
  .eff-bar-fill {{
    height: 100%; border-radius: 4px;
    width: {efficiency_bar_width}%;
    background: {cfg['color']};
  }}
  .eff-numbers {{ font-size: 10px; color: #555; margin-top: 3px; }}

  /* ── SCI Info ────────────────────────────────────── */
  .sci-info {{
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 16px;
  }}
  .sci-info h2 {{
    font-size: 11px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.06em; color: #16a34a; margin-bottom: 8px;
  }}
  .sci-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }}
  .sci-item label {{ font-size: 9px; color: #555; text-transform: uppercase; letter-spacing: 0.05em; }}
  .sci-item span {{ display: block; font-size: 12px; font-weight: 700; color: #111; margin-top: 2px; }}

  /* ── Métricas de Processamento ───────────────────── */
  .metrics-section {{ margin-bottom: 16px; }}
  .metrics-section h2 {{
    font-size: 12px; font-weight: 700; color: #111;
    margin-bottom: 4px;
  }}
  .metrics-section p {{ font-size: 9.5px; color: #666; margin-bottom: 10px; }}
  table {{
    width: 100%; border-collapse: collapse; font-size: 10px;
  }}
  th {{
    background: #f1f5f9;
    padding: 8px 10px;
    text-align: left;
    font-size: 9px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #555;
    border-bottom: 1px solid #e2e8f0;
  }}
  td {{
    padding: 8px 10px;
    border-bottom: 1px solid #f1f5f9;
    color: #222;
  }}
  tr:last-child td {{ border-bottom: none; }}
  tr:nth-child(even) td {{ background: #fafafa; }}

  /* ── Execução extra ──────────────────────────────── */
  .exec-info {{
    background: #f8fafb;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 16px;
  }}
  .exec-info h2 {{
    font-size: 11px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.06em; color: #555; margin-bottom: 8px;
  }}
  .exec-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }}
  .exec-item label {{ font-size: 9px; color: #888; text-transform: uppercase; letter-spacing: 0.05em; }}
  .exec-item span {{ display: block; font-size: 11px; font-weight: 600; color: #111; }}

  /* ── Rodapé ──────────────────────────────────────── */
  .footer {{
    margin-top: 18px;
    padding-top: 10px;
    border-top: 1px solid #e2e8f0;
    display: flex;
    justify-content: space-between;
    font-size: 9px;
    color: #999;
  }}
</style>
</head>
<body>

<!-- Cabeçalho -->
<header class="header">
  <div class="header-brand">
    <div class="brand-icon">E</div>
    <div>
      <div class="brand-title">EcoDash</div>
      <div class="brand-subtitle">Sistema de Diagnóstico de Green Software</div>
    </div>
  </div>
  <div class="header-meta">
    <strong>Relatório de Sustentabilidade</strong>
    <span>Gerado em: {generated_at}</span>
    <span>Usuário: {analise.user.username}</span>
  </div>
</header>

<!-- Identificação -->
<section class="identification">
  <h2>Identificação da Análise</h2>
  <div class="id-grid">
    <div class="id-item">
      <label>Software</label>
      <span>{analise.software_name}</span>
    </div>
    <div class="id-item">
      <label>Data da Análise</label>
      <span>{analysis_date}</span>
    </div>
    <div class="id-item">
      <label>ID da Análise</label>
      <span>#{analise.id}</span>
    </div>
    <div class="id-item">
      <label>Região</label>
      <span>{region_name} ({region_code})</span>
    </div>
    <div class="id-item">
      <label>Hardware</label>
      <span>{hardware_label}</span>
    </div>
    <div class="id-item">
      <label>Intensidade da Rede Elétrica</label>
      <span>{_fmt_float(grid_intensity)} gCO₂/kWh</span>
    </div>
  </div>
</section>

<!-- Visão Geral -->
<section class="overview">
  <div class="card">
    <div class="card-label">Consumo de Energia</div>
    <div class="card-value">{_fmt_float(energy_kwh, 6)}</div>
    <div class="card-unit">kWh</div>
    <div class="card-desc">Energia total consumida durante a execução</div>
  </div>

  <div class="card">
    <div class="card-label">Índice de Eficiência</div>
    <div class="card-value">{efficiency}%</div>
    <div class="card-unit">de 100%</div>
    <div class="eff-bar-bg"><div class="eff-bar-fill"></div></div>
    <div class="eff-numbers">Grade {grade} — {cfg['label']}</div>
  </div>

  <div class="card">
    <div class="card-label">Status de Sustentabilidade</div>
    <div class="grade-badge">{grade}</div>
    <div class="sustainability-status">{sustainability_label}</div>
    <div class="card-desc">{p.get('label', '')}</div>
  </div>
</section>

<!-- SCI Score -->
<section class="sci-info">
  <h2>Score SCI — Software Carbon Intensity</h2>
  <div class="sci-grid">
    <div class="sci-item">
      <label>SCI Score</label>
      <span>{_fmt_float(analise.sci_score, 6)} gCO₂eq</span>
    </div>
    <div class="sci-item">
      <label>Carbono Operacional</label>
      <span>{_fmt_float(analise.sci_score * functional_unit - embodied_gco2, 6)} gCO₂</span>
    </div>
    <div class="sci-item">
      <label>Carbono Incorporado</label>
      <span>{_fmt_float(embodied_gco2, 6)} gCO₂</span>
    </div>
    <div class="sci-item">
      <label>Unidade Funcional</label>
      <span>{_fmt_float(functional_unit, 0)}</span>
    </div>
  </div>
</section>

<!-- Métricas de Processamento -->
<section class="metrics-section">
  <h2>Métricas de Processamento Bruto</h2>
  <p>Utilização média, picos de demanda e pegada de carbono estimada por recurso do sistema.</p>
  <table>
    <thead>
      <tr>
        <th>Recurso</th>
        <th>Utilização Média</th>
        <th>Pico de Demanda</th>
        <th>Pegada de Carbono Estimada</th>
      </tr>
    </thead>
    <tbody>
      {metrics_rows_html}
    </tbody>
  </table>
</section>

<!-- Detalhes de Execução -->
<section class="exec-info">
  <h2>Detalhes de Execução</h2>
  <div class="exec-grid">
    <div class="exec-item">
      <label>Duração</label>
      <span>{_fmt_float(duration_s, 4)} s</span>
    </div>
    <div class="exec-item">
      <label>Threads (pico)</label>
      <span>{threads}</span>
    </div>
    <div class="exec-item">
      <label>Processo</label>
      <span>{m.get('process_name', '—')}</span>
    </div>
    <div class="exec-item">
      <label>Leitura em Disco</label>
      <span>{_fmt_float(float(m.get('io_read_mb', 0)))} MB</span>
    </div>
    <div class="exec-item">
      <label>Escrita em Disco</label>
      <span>{_fmt_float(float(m.get('io_write_mb', 0)))} MB</span>
    </div>
    <div class="exec-item">
      <label>CPU (pico)</label>
      <span>{_fmt_float(cpu_peak, 1)}%</span>
    </div>
  </div>
</section>

<!-- Rodapé -->
<footer class="footer">
  <span>EcoDash — Sistema de Diagnóstico de Green Software | TCC · Sistemas de Informação</span>
  <span>Relatório #{analise.id} · {generated_at}</span>
</footer>

</body>
</html>'''


def generate_pdf(analise) -> bytes:
    html_content = _build_html(analise)
    return HTML(string=html_content).write_pdf()
