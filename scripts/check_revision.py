import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request
from datetime import date, timedelta
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs'/'revisao'
OUT.mkdir(exist_ok=True)
BASE='http://127.0.0.1:8006'
with tempfile.TemporaryDirectory() as tmp:
    process=subprocess.Popen([sys.executable,'server.py','--port','8006','--db',str(Path(tmp)/'revision.db')],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    try:
        for _ in range(80):
            try:
                urllib.request.urlopen(BASE,timeout=1).close();break
            except OSError:
                time.sleep(.2)
        with sync_playwright() as p:
            browser=p.chromium.launch(channel='chrome',headless=True)
            page=browser.new_page(viewport={'width':1440,'height':1000})
            errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(BASE)
            page.get_by_role('button',name='Entrar no sistema').click()
            page.locator('.sidebar').wait_for()
            def go(slug):
                page.goto(BASE+'/#'+slug)
                page.locator('#content h1').wait_for()
            def form(action):
                return page.locator('form').filter(has=page.locator(f'button')).filter(has=page.locator('input,select,textarea'))
            def submit(section):
                with page.expect_response(lambda r:r.url.endswith('/api/action')) as response:
                    section.locator('button[type=submit]').click()
                assert response.value.status==200,response.value.text()
                page.wait_for_function('() => !document.querySelector("fieldset[disabled]")')
            def shot(name):
                page.screenshot(path=str(OUT/name),full_page=True)
            go('segments')
            page.locator('#content > label select').select_option('3')
            section=page.locator('section').filter(has=page.get_by_role('heading',name='Definir paradas'))
            section.locator('[name=stops]').fill('Macaparana\nCarpina\nRecife\nMacaparana')
            section.locator('[name=reason]').fill('Teste acadêmico de planejamento por trecho')
            submit(section)
            shot('01-rota-trechos.png')
            result=page.request.post(BASE+'/api/action',headers={'X-App':'macaparana'},data={'action':'schedule.create','data':{'request_id':4,'start_date':(date.today()+timedelta(days=1)).isoformat(),'end_date':(date.today()+timedelta(days=1)).isoformat(),'weekdays':[]}})
            assert result.status==200,result.text()
            page.reload();page.locator('#content h1').wait_for()
            page.locator('#content > label select').select_option('3')
            section=page.locator('section').filter(has=page.get_by_role('heading',name='Alocar por trecho'))
            section.locator('[name=segment_start]').select_option('1')
            section.locator('[name=segment_end]').select_option('2')
            submit(section)
            section=page.locator('section').filter(has=page.get_by_role('heading',name='Confirmação assistida'))
            section.locator('[name=channel]').select_option('Telefone')
            section.locator('[name=note]').fill('Confirmação fictícia com apoio da equipe')
            submit(section)
            shot('02-alocacao-confirmacao.png')
            go('production')
            page.locator('#month').fill((date.today()-timedelta(days=1)).isoformat()[:7])
            section=page.locator('section').filter(has=page.get_by_role('heading',name='Preparar ou corrigir registro'))
            section.locator('[name=occurrence_id]').select_option('7')
            section.locator('[name=procedure_code]').fill('0000000001')
            section.locator('[name=destination]').fill('Faturamento municipal — revisão demonstrativa')
            section.locator('[name=note]').fill('Código fictício. Validar CNS, catálogo, elegibilidade e leiaute.')
            submit(section)
            shot('03-producao-preparada.png')
            section=page.locator('section').filter(has=page.get_by_role('heading',name='Registros preparados'))
            section.locator('[name=protocol]').fill('REVISAO-DEMO-001')
            submit(section)
            with page.expect_download() as download:
                page.get_by_text('Exportar preparação CSV',exact=True).click()
            download.value.save_as(OUT/'preparacao-producao.csv')
            assert '0000000001' in (OUT/'preparacao-producao.csv').read_text(encoding='utf-8-sig')
            shot('04-producao-encaminhada.png')
            go('pilot')
            section=page.locator('section').filter(has=page.get_by_role('heading',name='Registrar medição do piloto'))
            for name,value in {'indicator':'Tempo de conferência — exemplo','unit':'minutos','baseline':'20','measured':'12','start_date':date.today().isoformat(),'end_date':date.today().isoformat(),'responsible':'Equipe acadêmica fictícia','source':'Valores artificiais para testar o formulário; não representam medição municipal.'}.items():
                section.locator(f'[name={name}]').fill(value)
            submit(section)
            shot('05-indicadores-piloto.png')
            go('support')
            section=page.locator('section').filter(has=page.get_by_role('heading',name='Abrir registro'))
            section.locator('[name=kind]').select_option('Capacitação')
            section.locator('[name=title]').fill('Oficina acadêmica demonstrativa')
            section.locator('[name=owner]').fill('Equipe de teste')
            section.locator('[name=notes]').fill('Exercício fictício de regulação, transporte e conferência.')
            submit(section)
            section=page.locator('section').filter(has=page.get_by_role('heading',name='Concluir registro'))
            section.locator('[name=notes]').fill('Fluxo executado em laboratório; sem capacitação municipal real.')
            submit(section)
            shot('06-capacitacao-suporte.png')
            data=page.request.get(BASE+'/api/state').json()
            assert data['production'][0]['protocol']=='REVISAO-DEMO-001'
            assert data['pilot_measurements'][0]['scenario']=='Simulação acadêmica'
            assert data['service_records'][0]['status']=='Concluído'
            assert any(o['segment_start']==1 and o['segment_end']==2 and o['confirmation_channel']=='Telefone' for o in data['occurrences'])
            page.reload();page.locator('#content h1').wait_for()
            assert page.get_by_text('Concluído',exact=True).is_visible()
            page.set_viewport_size({'width':390,'height':844})
            for slug in ['segments','production','pilot','support']:
                go(slug)
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),slug
            shot('07-mobile.png')
            assert not errors,errors
            browser.close()
            (OUT/'resultado.json').write_text(json.dumps({'result':'PASS','screenshots':7,'javascript_errors':errors,'date':date.today().isoformat(),'checks':['rota por trechos','alocação por intervalo','confirmação assistida','produção e exportação','encaminhamento com protocolo','medição simulada identificada','capacitação concluída','persistência após recarga','quatro telas em 390px']},ensure_ascii=False,indent=2),encoding='utf-8')
    finally:
        process.terminate();process.wait(timeout=10)
