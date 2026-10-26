import html
import json
import zipfile
from pathlib import Path
import markdown
import pymupdf
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/'docs'
identity=json.loads((DOCS/'identificacao.json').read_text(encoding='utf-8'))
identity_lines=[v for k,v in identity.items() if k in ('instituicao','curso','disciplina','professor','integrantes') and 'não informad' not in v.lower()]
identity_html='<p class="identity">'+'<br>'.join(html.escape(v) for v in identity_lines)+'</p>' if identity_lines else ''
css='''
@page {size:A4;margin:17mm 16mm 19mm}
*{box-sizing:border-box}body{font-family:Arial,sans-serif;color:#243e37;margin:0;background:#fff}
.page{break-before:page}.page:first-child{break-before:auto}
h1{font-size:23px;line-height:1.2;color:#145544;margin:0 0 16px;border-bottom:3px solid #b8d1a8;padding-bottom:12px}
h2{font-size:19px;color:#275c49}h3{font-size:15px;color:#275c49;margin:16px 0 7px}
p,li{font-size:14px;line-height:1.55}p{margin:9px 0}li{margin:5px 0}
table{width:100%;border-collapse:collapse;margin:12px 0;font-size:12px;line-height:1.4}
th{background:#e8f0e1;text-align:left;color:#27543e}th,td{border:1px solid #dce5d6;padding:7px;vertical-align:top}
tr{break-inside:avoid}thead{display:table-header-group}img{max-width:100%;max-height:104mm;object-fit:contain;display:block;margin:12px auto}
blockquote{margin:13px 0;border-left:4px solid #a3bf8e;background:#f1f5eb;padding:8px 14px}
code{font-family:Consolas,monospace;font-size:10px;overflow-wrap:anywhere}pre{background:#f0f4ed;padding:13px;white-space:pre-wrap}
a{color:#1f6b51;overflow-wrap:anywhere}.cover{padding-top:35mm}.cover h1{font-size:49px;border:0}.cover h2{font-size:25px;max-width:500px}.cover p{font-size:13px}
.eyebrow{letter-spacing:3px;text-transform:uppercase;color:#6d8560;font-size:10px}.identity{margin-top:30px!important;color:#536d48}
.gallery img{max-height:205mm}.gallery p{font-size:10px}.cover img{width:55px;margin:0 0 20px}
'''
source=(DOCS/'Guia-Completo-Apresentacao.md').read_text(encoding='utf-8')
parts=source.split('<!-- PAGE -->')
pages=[]
for index,part in enumerate(parts):
    body=markdown.markdown(part,extensions=['tables','fenced_code'])
    if index==0:
        body='<img src="mark.svg" alt=""><div class="eyebrow">Projeto acadêmico · material de defesa</div>'+body+identity_html
    pages.append(f'<section class="page {"cover" if index==0 else ""}">{body}</section>')
for title,file,caption in [
    ('Evidência visual — alocação por trecho','02-alocacao-confirmacao.png','A ocorrência foi alocada somente no intervalo Carpina → Recife. A lista registra confirmação por telefone. Dados fictícios.'),
    ('Evidência visual — preparação da produção','04-producao-encaminhada.png','Produção preparada e encaminhada internamente com protocolo; não representa transmissão oficial.'),
    ('Evidência visual — indicadores e piloto','05-indicadores-piloto.png','Indicadores locais e formulário de medição. Os valores de teste são artificiais e identificados como simulação.'),
    ('Evidência visual — capacitação e suporte','06-capacitacao-suporte.png','Registro de capacitação demonstrativa concluído para testar o fluxo. Não comprova realização de oficina municipal.')]:
    pages.append(f'<section class="page gallery"><h1>{title}</h1><p>{caption}</p><img src="revisao/{file}" alt="{title}"></section>')
guide='<!doctype html><html lang="pt-BR"><meta charset="utf-8"><title>Macaparana Saúde — Guia completo de apresentação</title><style>'+css+'</style><body>'+''.join(pages)+'</body></html>'
(DOCS/'Guia-Completo-Apresentacao.html').write_text(guide,encoding='utf-8')

slides=[
('Macaparana Saúde','Gestão integrada de TFD, transporte sanitário e ajudas de custo', ['Sistema funcional • documentação • protótipo navegável','Python + React + SQLite','Demonstração acadêmica com dados fictícios'],'', 'Do pedido ao acompanhamento financeiro, com registros relacionados.'),
('O problema que orientou a solução','Acompanhar a pessoa e as etapas do processo', ['Solicitar e autorizar atendimento fora do município','Planejar datas, recursos e capacidade','Conciliar viagem, documentos e benefícios','Consultar origem, pendências e responsáveis'],'','Resultados municipais precisam ser medidos em piloto; não foram presumidos.'),
('O fluxo integrado','Cada etapa mantém vínculo com sua origem', ['Cadastro → solicitação → laudo → autorização','Calendário → viagem → confirmação → embarque','Declaração → conferência → benefício','Contabilidade → registro de pagamento'],'','Deslocamento, atendimento, benefício e pagamento são fatos distintos.'),
('Como foi construído','Interface, regras e persistência', ['React: componentes, formulários e atualização das telas','Python: API, sessão, permissões e regras','SQLite: registros, documentos e auditoria','Vite: frontend compilado para execução local'],'arquitetura.svg','A entrega abre com Python e navegador; não exige Node.js para apresentar.'),
('Autorização e calendário','Documentação e continuidade entre competências', ['Cadastro reutilizável de paciente e referência','Modalidades TFD e transporte sanitário separadas','Autorização exige laudo e justificativa','Agenda semanal ou avulsa, dentro da validade'],'telas/05-calendar.png','A recorrência não duplica a mesma data para a mesma solicitação.'),
('Transporte por data e trecho','Capacidade que considera paciente e acompanhante', ['Veículo, motorista e acessibilidade','Conflitos de horário e validade de CNH','Paradas ordenadas e reserva por segmento','Alterações com justificativa e auditoria'],'telas/06-trips.png','Rotas e trechos amplia o planejamento; não há mapa nem rastreamento GPS.'),
('Operação e comprovação','Confirmar não significa comprovar atendimento', ['Confirmação assistida alimenta a lista do motorista','Embarque ou ausência antes do encerramento','Quilômetros reais, litros e custos registrados','Declaração independente para acompanhante'],'telas/12-operacao.png','O canal WhatsApp apenas registra resposta obtida externamente; não envia mensagens.'),
('Conferência e financeiro','Pendências e etapas visíveis', ['Tabela mensal compacta de pacientes e datas','Documentos e permanência ligados à ocorrência','Benefício demonstrativo sem duplicidade','Calculado → aprovado → contabilidade → pago'],'telas/07-review.png','Valores são ilustrativos. Registrar pagamento não transfere dinheiro.'),
('Preparação da produção','Área própria para o faturamento', ['Ocorrência precisa estar conciliada','Procedimento informado, quantidade e destino','Exportação CSV com identificadores de origem','Encaminhamento interno com protocolo'],'','Preparação interna implementada; transmissão e leiaute oficial dependem de homologação.'),
('Indicadores, proteção e suporte','Ferramentas para acompanhar e aperfeiçoar a rotina', ['Custos, km/l, embarques, ausências e pendências','Medição com base, resultado, fonte e responsável','Perfis, sessão, auditoria e backup consistente','Materiais e registros de capacitação e suporte'],'','O piloto municipal real ainda depende de participação e aceite da prefeitura.'),
('Como validamos','Evidências de execução local', ['27 testes automatizados aprovados','Fluxo até pagamento testado no navegador','Novos fluxos e telas de celular verificados','Pacote extraído e iniciado em base limpa'],'','Teste aprovado não equivale a homologação municipal, certificação ou cobertura total.'),
('Entrega e próximos passos','Base funcional para validação em campo', ['Entregue: sistema, documentação, prints e código','Homologar regras com as equipes municipais','Obter interfaces e permissões das integrações','Capacitar, executar piloto e medir resultados'],'','A contribuição central é integrar o processo e suas evidências.'),
]
slidecss='''
@page{size:320mm 180mm;margin:0}*{box-sizing:border-box}body{margin:0;font-family:Arial,sans-serif;color:#173f34}
.slide{width:320mm;height:180mm;padding:17mm 20mm 15mm;position:relative;break-after:page;background:#f6f8f2;overflow:hidden}
.slide:last-child{break-after:auto}.label{font-size:11px;letter-spacing:3px;text-transform:uppercase;color:#6a825d}
h1{font-size:39px;line-height:1.1;margin:20px 0 9px;max-width:1050px}h2{font-size:21px;font-weight:400;color:#6c835b;margin:0 0 23px}
.cols{display:flex;gap:30px;align-items:flex-start}.text{flex:1}ul{padding-left:25px;margin:6px 0}li{font-size:23px;line-height:1.35;margin-bottom:16px}
.visual{width:49%;max-height:315px;object-fit:contain;border:1px solid #dbe4d4;background:white}
.note{position:absolute;bottom:17mm;left:20mm;right:20mm;border-top:2px solid #cfddc3;padding-top:14px;font-size:16px;line-height:1.4}
.number{position:absolute;right:20mm;top:17mm;font-size:12px;color:#789267}.identity{font-size:14px;color:#607950}
'''
body=''
for index,(title,subtitle,points,img,note) in enumerate(slides,1):
    visual=f'<img class="visual" src="{img}" alt="{html.escape(title)}">' if img else ''
    body+=f'<section class="slide"><div class="label">Macaparana Saúde · projeto acadêmico</div><div class="number">{index:02} / {len(slides)}</div><h1>{title}</h1><h2>{subtitle}</h2><div class="cols"><div class="text"><ul>'+''.join(f'<li>{html.escape(p)}</li>' for p in points)+'</ul>'+(identity_html if index==1 else '')+f'</div>{visual}</div><div class="note">{note}</div></section>'
(DOCS/'Slides-Apresentacao.html').write_text('<!doctype html><html lang="pt-BR"><meta charset="utf-8"><title>Apresentação Macaparana Saúde</title><style>'+slidecss+'</style>'+body+'</html>',encoding='utf-8')

with sync_playwright() as p:
    browser=p.chromium.launch(channel='chrome',headless=True)
    page=browser.new_page()
    page.emulate_media(media='print')
    for slug in ['Guia-Completo-Apresentacao','Slides-Apresentacao']:
        page.goto((DOCS/f'{slug}.html').as_uri(),wait_until='networkidle')
        page.evaluate('document.fonts.ready')
        if slug.startswith('Slides'):
            assert page.locator('.slide').count()==12
            overflow=page.evaluate('() => [...document.querySelectorAll(".slide")].filter(s=>s.scrollHeight>s.clientHeight+1).length')
            assert not overflow, 'Slide com conteúdo além da página'
        pdf=page.pdf(print_background=True,prefer_css_page_size=True,display_header_footer=slug.startswith('Guia'),header_template='<span></span>',footer_template='<div style="font:8px Arial;width:100%;margin:0 50px;color:#67805b;display:flex;justify-content:space-between"><span>MACAPARANA SAÚDE · GUIA DE APRESENTAÇÃO</span><span class="pageNumber"></span></div>')
        (DOCS/f'{slug}.pdf').write_bytes(pdf)
        with pymupdf.open(stream=pdf,filetype='pdf') as doc:
            texts=[page.get_text() for page in doc]
            assert all(len(t.strip())>35 for t in texts), 'Página sem conteúdo'
            if slug.startswith('Slides'):
                assert len(doc)==12,len(doc)
            else:
                assert 'Fim do guia' in '\n'.join(texts)
                assert all(f'{n}.' in '\n'.join(texts) for n in range(1,24))
            preview=ROOT/'data'/'presentation-preview'
            preview.mkdir(parents=True,exist_ok=True)
            for index in [0, min(3,len(doc)-1),len(doc)-1]:
                doc[index].get_pixmap(matrix=pymupdf.Matrix(1,1)).save(preview/f'{slug}-{index+1}.png')
            print(f'{slug}: {len(doc)} paginas; {len(pdf)} bytes',flush=True)
    browser.close()

files=['Guia-Completo-Apresentacao.pdf','Guia-Completo-Apresentacao.md','Slides-Apresentacao.pdf','Documentacao-Macaparana.pdf','verificacao-escopo.pdf','Prototipo-de-Telas.pdf','Fluxos-Funcionando.pdf','Revisao-Fluxos.pdf','operacao.pdf','Roteiro-de-Apresentacao.pdf','resultado-testes.txt','teste-navegador.json','revisao/resultado.json']
out=ROOT/'entrega'/'Material-Apresentacao-Macaparana.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as package:
    for file in files:
        package.write(DOCS/file,'Material-Apresentacao/'+file)
    package.writestr('Material-Apresentacao/LEIA-ME.txt','Comece pelo Guia-Completo-Apresentacao.pdf para estudar. Projete Slides-Apresentacao.pdf durante a fala. Os demais PDFs contêm documentação e evidências. O sistema executável está no pacote separado Macaparana-Saude-Entrega.zip. Dados e testes acadêmicos não equivalem a piloto municipal real.')
print(out,flush=True)
