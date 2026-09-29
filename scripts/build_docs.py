"""Gera HTML, diagramas SVG e PDFs. Ferramenta de desenvolvimento."""
import html
import json
from pathlib import Path
import markdown
import pymupdf
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/'docs'
identity=json.loads((DOCS/'identificacao.json').read_text(encoding='utf-8'))
E=html.escape
(DOCS/'mark.svg').write_bytes((ROOT/'static'/'mark.svg').read_bytes())


def wrap(title,subtitle,body):
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(title)} · Macaparana Saúde</title><link rel="stylesheet" href="doc.css"></head><body><nav class="doc-nav"><strong>MACAPARANA SAÚDE</strong><a href="documentacao.html">Documentação</a><a href="prototipo.html">Protótipo</a><a href="roteiro.html">Apresentação</a><a href="/">Sistema local</a></nav><main class="sheet"><section class="cover"><img class="mark" src="../mark.svg" alt="" onerror="this.style.display='none'"><span class="label">Projeto acadêmico · Tecnologia da Informação</span><h1>Macaparana<br>Saúde</h1><h2>{E(title)}</h2><div class="line"></div><p>{E(subtitle)}</p><div class="identity"><strong>{E(identity['instituicao'])}</strong><br>{E(identity['curso'])}<br>{E(identity['disciplina'])}<br>{E(identity['professor'])}<br>{E(identity['integrantes'])}</div><div class="version">{E(identity['local'])}<br>{E(identity['data'])} · Versão 1.0</div><p class="note">Demonstração com dados exclusivamente fictícios. Não representa implantação, validação jurídica ou homologação municipal.</p></section>{body}<footer class="doc-footer">Macaparana Saúde · Entrega acadêmica · Setembro de 2026</footer></main></body></html>'''


def svg_start(width,height):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0 10 5 0 10z" fill="#a0b68d"/></marker></defs><rect width="100%" height="100%" rx="12" fill="#f9fbf6"/>'


def box(x,y,w,h,title,lines=(),fill='#edf3e5'):
    out=f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="{fill}" stroke="#d5e1c9"/><text x="{x+14}" y="{y+25}" font-family="Arial,sans-serif" font-size="14" font-weight="bold" fill="#3e6448">{E(title)}</text>'
    for i,line in enumerate(lines):
        out+=f'<text x="{x+14}" y="{y+46+i*18}" font-family="Arial,sans-serif" font-size="11" fill="#768b68">{E(line)}</text>'
    return out


def arrow(path,label='',x=0,y=0):
    result=f'<path d="{path}" fill="none" stroke="#a0b68d" stroke-width="2" marker-end="url(#arrow)"/>'
    if label:
        result+=f'<text x="{x}" y="{y}" font-family="Arial,sans-serif" font-size="10" fill="#829674">{E(label)}</text>'
    return result


flow=svg_start(900,725)
for x,y,title,lines in [(30,25,'1. Cadastro e solicitação',['Paciente, acompanhante e modalidade']),(330,25,'2. Análise e autorização',['Laudo + decisão com justificativa']),(630,25,'3. Calendário',['Ocorrências avulsas ou recorrentes']),(630,190,'4. Planejamento',['Rota, veículo, motorista, capacidade']),(330,190,'5. Execução',['Confirmação, embarque ou ausência']),(30,190,'6. Comprovação',['Declarações separadas e permanência']),(30,375,'7. Conferência mensal',['Paciente × datas → documentos']),(330,375,'8. Benefício elegível?',['Somente TFD autorizado e comprovado']),(630,375,'9. Cálculo e aprovação',['Regra demonstrativa versionada']),(630,550,'10. Contabilidade e pagamento',['Referência, data e acompanhamento']),(330,550,'Histórico e controle',['Eventos, documentos e auditoria'])]:
    flow+=box(x,y,240,90,title,lines)
for path in ['M270 70H330','M570 70H630','M750 115V190','M630 235H570','M330 235H270','M150 280V375','M270 420H330','M570 420H630','M750 465V550','M630 595H570']:
    flow+=arrow(path)
flow+=arrow('M450 115V150H150V115','Pendência: corrigir documentação',210,142)
flow+=arrow('M450 465V550','Sem benefício: manter histórico',460,510)
flow+='<text x="30" y="690" font-family="Arial,sans-serif" font-size="12" fill="#819271">Fluxograma conceitual. Ausência ou falta de documento não equivale a atendimento comprovado.</text></svg>'
(DOCS/'fluxo.svg').write_text(flow,encoding='utf-8')

arch=svg_start(900,330)
arch+=box(30,55,240,180,'Navegador',['React + JSX + CSS','Componentes, estado e formulários','Desktop e celular','Build local produzido pelo Vite'])
arch+=box(330,55,240,180,'Servidor local Python',['HTTP + sessão + permissões','Regras de negócio','Transações e auditoria','127.0.0.1:8000'])
arch+=box(630,55,240,180,'Arquivo SQLite',['Registros relacionais','Documentos binários e hashes','Valores em centavos','Persistência local'])
arch+=arrow('M270 130H330','JSON',287,118)+arrow('M570 130H630','SQL',589,118)
arch+='<text x="30" y="290" font-family="Arial,sans-serif" font-size="12" fill="#819271">Integrações e infraestrutura de produção são etapas futuras. Nenhum serviço externo é chamado.</text></svg>'
(DOCS/'arquitetura.svg').write_text(arch,encoding='utf-8')

model=svg_start(940,670)
for x,y,w,title,lines in [(30,25,250,'PATIENTS',['PK id · nome · embarque','Acompanhante e dados bancários']),(345,25,250,'FACILITIES',['PK id · CNES · município','Referência reutilizável']),(30,180,250,'REQUESTS',['FK patient_id · facility_id','Modalidade · validade · situação']),(345,180,250,'OCCURRENCES',['FK request_id · trip_id','Data · embarque · comprovações']),(660,180,250,'TRIPS',['FK vehicle_id · driver_id','Rota · horários · km · consumo']),(660,25,250,'VEHICLES / DRIVERS',['Capacidade · acessibilidade','CNH · validade']),(30,365,250,'DOCUMENTS',['FK request_id OU occurrence_id','Arquivo · hash · autoria']),(345,365,250,'BENEFITS',['FK occurrence_id · rule_id','Beneficiário · centavos · etapa']),(660,365,250,'RULES',['PK id · valores em centavos','Identificação da versão']),(30,535,250,'USERS',['Perfil · credenciais derivadas','Motorista vinculado quando aplicável']),(345,535,565,'AUDIT',['FK user_id · entidade/id · ação · data/hora','Antes/depois · motivo · autor'])]:
    model+=box(x,y,w,95,title,lines)
for path,label,x,y in [('M155 120V180','1:N',165,152),('M470 120V145H265V180','1:N',355,139),('M280 225H345','1:N',300,215),('M660 225H595','1:N',610,215),('M785 120V180','1:N',795,152),('M155 275V365','1:N',167,322),('M430 275V320H245V365','1:N',320,312),('M470 275V365','1:N',480,323),('M660 411H595','1:N',611,401),('M280 580H345','1:N',300,570)]:
    model+=arrow(path,label,x,y)
model+='</svg>'
(DOCS/'modelo-dados.svg').write_text(model,encoding='utf-8')

def offline_safe(document):
    return document.replace('../mark.svg','mark.svg').replace(' onerror="this.style.display=\'none\'"','').replace('href="/"','href="http://localhost:8000"').replace('Versão 1.0','Versão 1.1')


for source,title,subtitle in [('documentacao','Documentação do projeto','Sistema integrado de gestão de TFD, transporte sanitário e deslocamentos em saúde.'),('roteiro','Roteiro de apresentação','Guia prático para demonstrar o fluxo, explicar as decisões e responder às principais perguntas.')]:
    text=(DOCS/f'{source}.md').read_text(encoding='utf-8')
    if source=='documentacao':
        text='[TOC]\n\n'+text
    body=markdown.markdown(text,extensions=['tables','fenced_code','toc'])
    (DOCS/f'{source}.html').write_text(offline_safe(wrap(title,subtitle,body)),encoding='utf-8')

screens=[
 ('01-login.png','Acesso e perfis','Entrada por perfil demonstrativo; sessão autenticada. A senha é pública porque a base é fictícia.','Experimente admin para o fluxo completo ou motorista para acesso operacional restrito.'),
 ('02-dashboard.png','Visão geral','Indicadores calculados dos registros, viagens de hoje e solicitações recentes.','Ver todas leva à operação das viagens; Nova solicitação inicia o processo.'),
 ('03-patients.png','Pacientes','Busca e cadastro central de pacientes, acompanhantes, endereço e embarque.','Histórico abre solicitações e ocorrências do paciente, sem duplicar seu cadastro a cada mês.'),
 ('04-requests.png','Solicitações','Modalidade, referência, especialidade e situação do processo.','Abrir permite anexar laudo, decidir e gerar calendário após autorização.'),
 ('05-calendar.png','Calendário de tratamento','Ocorrências por competência, com distinção visual de TFD e transporte sanitário.','Clique na ocorrência para abrir vínculos e documentos. Agendar permite datas avulsas ou recorrências semanais.'),
 ('06-trips.png','Planejamento de viagens','Data, veículo, motorista, ocupação e situação.','O servidor valida conflitos, capacidade com acompanhante e acessibilidade na alocação.'),
 ('07-review.png','Conferência mensal','Matriz compacta de pacientes e datas com indicador de comprovação.','Cada célula abre a origem. Acompanhante possui comprovação independente da declaração do paciente.'),
 ('08-finance.png','Ajudas de custo','Valores por competência, estágios financeiros e regra demonstrativa.','Aprovar, encaminhar e registrar pagamento são etapas distintas. CSV não é leiaute oficial.'),
 ('09-fleet.png','Frota e referências','Recursos reutilizados no planejamento e unidades com CNES manual.','Cadastro local; não há consulta externa ao CNES nem validação institucional dos identificadores fictícios.'),
 ('10-audit.png','Auditoria','Usuário, horário, ação e registro afetado.','Detalhes exibe antes/depois e justificativa. A trilha não é um repositório imutável de produção.'),
 ('11-help.png','Entrega acadêmica','Acesso à documentação, protótipo e roteiro pelo próprio sistema.','Os documentos também podem ser abertos diretamente na pasta docs.'),
 ('12-operacao.png','Operação da viagem','Lista de passageiros, acompanhante, confirmação, embarque e dados de execução.','O motorista visualiza apenas suas viagens. Imprimir lista abre uma versão operacional sem dados clínicos ou bancários.'),
 ('13-mobile.png','Visão responsiva','A interface adapta a navegação e os cartões para telas menores.','Verificada em largura de 390 px. Tabelas amplas têm rolagem dentro do contêiner; não há aplicativo nativo nem modo offline.'),
]
body='<h1>Protótipo de alta fidelidade</h1><p>As telas a seguir são capturas reais do sistema local. O protótipo interativo é a própria aplicação: execute iniciar.bat e acesse localhost:8000. A galeria HTML permite abrir cada imagem em resolução completa. Os dados e estados são demonstrativos.</p>'
for i,(file,title,description,note) in enumerate(screens,1):
    body+=f'<section class="screen {"mobile" if "mobile" in file else ""}"><span class="number">Tela {i:02} / {len(screens):02}</span><h1>{E(title)}</h1><p>{E(description)}</p><a href="telas/{file}"><img src="telas/{file}" alt="Captura de tela: {E(title)}"></a><p class="annotation">{E(note)}</p></section>'
(DOCS/'prototipo.html').write_text(offline_safe(wrap('Protótipo de telas','Interface navegável de alta fidelidade · capturas reais e comportamento esperado.',body)),encoding='utf-8')

exports=[('documentacao','Documentacao-Macaparana.pdf'),('prototipo','Prototipo-de-Telas.pdf'),('roteiro','Roteiro-de-Apresentacao.pdf')]
flow_manifest=DOCS/'fluxos'/'manifesto.json'
if flow_manifest.exists():
    flows=json.loads(flow_manifest.read_text(encoding='utf-8'))
    assert flows['result']=='PASS'
    body=f'<h1>Fluxos integrados em funcionamento</h1><p>{flows["screenshots"]} capturas de uma execução real e automatizada pela interface React, conectada à API Python e ao SQLite. Base temporária com dados fictícios. Cada etapa foi executada, e os resultados relevantes foram verificados na API. Nenhuma integração externa é simulada como ativa.</p><p><a href="fluxos/manifesto.json">Manifesto das verificações</a> · <a href="fluxos/folha-demonstrativa.csv">CSV exportado durante o fluxo</a></p><h2>Cobertura verificada</h2><ul>'+''.join(f'<li>{E(check)}</li>' for check in flows['checks'])+'</ul>'
    for index,capture in enumerate(flows['captures'],1):
        body+=f'<section class="screen"><span class="number">Etapa {index:02} / {flows["screenshots"]:02}</span><h1>{E(capture["title"])}</h1><p>{E(capture["description"])}</p><a href="fluxos/{capture["file"]}"><img src="fluxos/{capture["file"]}" alt="{E(capture["title"])}"></a><p class="annotation">Evidência capturada no navegador após a operação. Resultado da execução: PASS. Dados exclusivamente fictícios.</p></section>'
    body+='<p>Fim das evidências dos fluxos integrados.</p>'
    (DOCS/'fluxos.html').write_text(offline_safe(wrap('Fluxos funcionando e integrados','React → API Python → SQLite · etapas, validações e perfis autenticados.',body)),encoding='utf-8')
    exports.append(('fluxos','Fluxos-Funcionando.pdf'))

with sync_playwright() as p:
    browser=p.chromium.launch(channel='chrome',headless=True)
    page=browser.new_page()
    page.emulate_media(media='print')
    for slug,filename in exports:
        page.goto((DOCS/f'{slug}.html').as_uri(),wait_until='networkidle')
        page.evaluate('document.fonts.ready')
        pdfdata=page.pdf(format='A4',print_background=True,prefer_css_page_size=True,display_header_footer=True,header_template='<span></span>',footer_template='<div style="font-family:Arial;font-size:8px;width:100%;padding:0 45px;display:flex;justify-content:space-between;color:#819074"><span>MACAPARANA SAÚDE · PROJETO ACADÊMICO</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>')
        with pymupdf.open(stream=pdfdata,filetype='pdf') as document:
            extracted=' '.join(p.get_text() for p in document)
            if slug=='documentacao':
                assert len(extracted)>30000 and 'revista quando o sistema evoluir.' in extracted, 'Documentação incompleta no PDF.'
            elif slug=='prototipo':
                assert len(document)>=15 and '390 px' in extracted, 'Protótipo incompleto no PDF.'
            elif slug=='roteiro':
                assert 'Antes de enviar' in extracted, 'Roteiro incompleto no PDF.'
            else:
                assert len(document)>=flows['screenshots'] and 'Fim das' in extracted, 'Evidências incompletas no PDF.'
        (DOCS/filename).write_bytes(pdfdata)
        print(filename,flush=True)
    browser.close()
