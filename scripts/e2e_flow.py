"""Fluxo ponta a ponta no navegador, em banco temporário isolado."""
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request
from datetime import date
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
sys.stdout.reconfigure(encoding='utf-8')

with tempfile.TemporaryDirectory() as temporary:
    process=subprocess.Popen([sys.executable,'server.py','--port','8001','--db',str(Path(temporary)/'e2e.db')],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    try:
        for _ in range(60):
            try:
                urllib.request.urlopen('http://127.0.0.1:8001',timeout=1).close()
                break
            except OSError:
                time.sleep(.2)
        with sync_playwright() as p:
            browser=p.chromium.launch(channel='chrome',headless=True)
            page=browser.new_page(viewport={'width':1440,'height':1000})
            page.set_default_timeout(15000)
            errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            def observe(response):
                if '/api/action' in response.url:
                    print('ACTION',response.status,response.text(),flush=True)
            page.on('response',observe)
            page.goto('http://127.0.0.1:8001')
            page.get_by_role('button',name='Entrar no sistema').click()
            page.locator('.sidebar').wait_for()
            page.goto('http://127.0.0.1:8001/#patients')
            page.get_by_role('button',name='Cadastrar paciente',exact=True).click()
            page.locator('[name=name]').fill('Paciente E2E fictício')
            page.locator('[name=address]').fill('Rua de teste, 1')
            page.locator('[name=boarding]').fill('Praça de teste')
            page.locator('dialog button[type=submit]').click()
            page.get_by_text('Paciente E2E fictício',exact=True).wait_for()
            page.goto('http://127.0.0.1:8001/#requests')
            page.get_by_role('button',name='Nova solicitação',exact=True).click()
            page.locator('[name=patient_id]').select_option(label='Paciente E2E fictício')
            page.locator('[name=facility_id]').select_option('1')
            page.locator('[name=specialty]').fill('Cardiologia')
            page.locator('dialog button[type=submit]').click()
            page.locator('[data-act=document-request]').wait_for()
            rid=int(page.locator('[data-act=document-request]').get_attribute('data-id'))
            page.get_by_role('button',name='Anexar laudo',exact=True).click()
            page.locator('[name=file]').set_input_files({'name':'laudo-ficticio.txt','mimeType':'text/plain','buffer':b'Laudo de teste ficticio'})
            page.locator('dialog button[type=submit]').click()
            page.get_by_role('button',name='Analisar solicitação',exact=True).click()
            page.locator('[name=reason]').fill('Teste funcional demonstrativo')
            page.locator('dialog button[type=submit]').click()
            page.get_by_role('button',name='Agendar tratamento',exact=True).click()
            page.locator('dialog button[type=submit]').click()
            page.locator('dialog').wait_for(state='hidden')
            page.goto('http://127.0.0.1:8001/#trips')
            page.get_by_role('button',name='Planejar viagem',exact=True).click()
            page.locator('[name=departure]').fill('18:00')
            page.locator('[name=arrival]').fill('20:00')
            page.locator('dialog button[type=submit]').click()
            page.get_by_role('button',name='Alocar paciente',exact=True).click()
            option=page.locator('[name=occurrence_id] option').filter(has_text='Paciente E2E fictício')
            oid=int(option.get_attribute('value'))
            page.locator('[name=occurrence_id]').select_option(str(oid))
            page.locator('dialog button[type=submit]').click()
            page.get_by_role('button',name='Confirmar',exact=True).click()
            page.get_by_role('button',name='Embarcou',exact=True).click()
            page.get_by_role('button',name='Encerrar viagem',exact=True).click()
            page.locator('[name=km]').fill('220')
            page.locator('[name=liters]').fill('22')
            page.locator('[name=cost]').fill('180')
            page.locator('dialog button[type=submit]').click()
            page.get_by_role('button',name='Fechar',exact=True).click()
            page.goto('http://127.0.0.1:8001/#review')
            page.locator(f'[data-act=occurrence-detail][data-id="{oid}"]').click()
            page.get_by_role('button',name='Anexar declaração',exact=True).click()
            page.locator('[name=file]').set_input_files({'name':'declaracao-ficticia.txt','mimeType':'text/plain','buffer':b'Atendimento comprovado para teste'})
            page.locator('dialog button[type=submit]').click()
            page.get_by_role('button',name='Conciliar atendimento',exact=True).click()
            page.locator('dialog button[type=submit]').click()
            page.get_by_role('button',name='Fechar',exact=True).click()
            page.goto('http://127.0.0.1:8001/#finance')
            page.get_by_role('button',name='Calcular competência',exact=True).click()
            page.locator('dialog button[type=submit]').click()
            row=page.locator('tbody tr').filter(has_text='Paciente E2E fictício')
            row.get_by_role('button',name='Aprovar',exact=True).click()
            page.locator('dialog button[type=submit]').click()
            row.get_by_role('button',name='Encaminhar',exact=True).click()
            page.locator('[name=accounting_ref]').fill('E2E-2026')
            page.locator('dialog button[type=submit]').click()
            row.get_by_role('button',name='Registrar pagamento',exact=True).click()
            page.locator('dialog button[type=submit]').click()
            page.reload()
            row=page.locator('tbody tr').filter(has_text='Paciente E2E fictício')
            row.get_by_text('Pago',exact=True).wait_for()
            assert not errors,errors
            result={'date':date.today().isoformat(),'result':'PASS','flow':'cadastro → solicitação → laudo → autorização → agendamento → viagem → confirmação → embarque → encerramento → declaração → comprovação → cálculo → aprovação → contabilidade → pagamento → recarregamento','request_id':rid,'occurrence_id':oid,'javascript_errors':errors,'database':'temporário isolado'}
            (ROOT/'docs'/'teste-navegador.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
            print(json.dumps(result,ensure_ascii=False))
            browser.close()
    finally:
        process.terminate()
        process.wait(timeout=10)
