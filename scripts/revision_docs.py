"""Atualiza documentação da revisão e gera anexos consultáveis/PDF."""
from pathlib import Path
import markdown
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
docs=ROOT/'docs'
path=docs/'documentacao.md'
text=path.read_text(encoding='utf-8')
text=text.replace('| Trechos | Reserva de capacidade durante toda a ida e volta | Assentos liberados e ocupados por trecho, ida e retorno independentes |','| Trechos | Paradas ordenadas, reserva por intervalo e capacidade por segmento | Viagens distintas para retornos em outros dias |')
text=text.replace('| RF09 | Alocar por data e trecho | P — data e rota de ida/volta; reserva integral, sem liberação intermediária |','| RF09 | Alocar por data e trecho | I — paradas ordenadas e capacidade por intervalo de alocação |')
text=text.replace('| RF19 | Preparar produção para sistemas oficiais | F — falta definição e homologação de leiautes |','| RF19 | Preparar produção para sistemas oficiais | P — preparação interna, revisão, protocolo e CSV; leiaute oficial depende de homologação |')
marker='\n# 18. Complemento da revisão de escopo — 04/10/2026\n'
if marker not in text:
    text+=marker+'\nA revisão acrescenta rotas por trecho, perfil de faturamento, preparação de produção, indicadores, registro de medições do piloto, capacitação, suporte e backup consistente. Consulte [Verificação completa do escopo](verificacao-escopo.html) e [Manual de operação](operacao.html). As limitações históricas desta documentação relativas à reserva integral e ausência de preparação interna são substituídas pelo complemento. Integrações oficiais, implantação e piloto real continuam condicionados à prefeitura.\n'
path.write_text(text,encoding='utf-8')
with sync_playwright() as p:
    browser=p.chromium.launch(channel='chrome',headless=True)
    page=browser.new_page()
    for slug in ['verificacao-escopo','operacao']:
        body=markdown.markdown((docs/f'{slug}.md').read_text(encoding='utf-8'),extensions=['tables','fenced_code'])
        html='<!doctype html><html lang="pt-BR"><meta charset="utf-8"><title>'+slug+'</title><link rel="stylesheet" href="doc.css"><body><main class="sheet">'+body+'</main></body></html>'
        (docs/f'{slug}.html').write_text(html,encoding='utf-8')
        page.goto((docs/f'{slug}.html').as_uri(),wait_until='networkidle')
        page.pdf(path=str(docs/f'{slug}.pdf'),format='A4',print_background=True,margin={'top':'15mm','bottom':'15mm','left':'12mm','right':'12mm'})
    captures=list((docs/'revisao').glob('*.png'))
    if captures:
        body='<h1>Complementos do escopo em funcionamento</h1><p>Execução de 04/10/2026 em base temporária fictícia. Fluxos na interface React com API Python e persistência SQLite. Consulte revisao/resultado.json para as verificações.</p>'
        for capture in sorted(captures):
            body+=f'<section class="screen"><h2>{capture.stem}</h2><a href="revisao/{capture.name}"><img src="revisao/{capture.name}" alt="{capture.stem}"></a></section>'
        (docs/'revisao.html').write_text('<!doctype html><html lang="pt-BR"><meta charset="utf-8"><title>Evidências da revisão</title><link rel="stylesheet" href="doc.css"><main class="sheet">'+body+'</main></html>',encoding='utf-8')
        page.goto((docs/'revisao.html').as_uri(),wait_until='networkidle')
        page.pdf(path=str(docs/'Revisao-Fluxos.pdf'),format='A4',print_background=True)
    browser.close()
