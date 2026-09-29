"""Demonstra os fluxos pela interface React, fotografa estados e verifica a API.

Banco temporário isolado; não altera a base de apresentação. Requer Chrome/Playwright.
"""
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request
from datetime import date, timedelta
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs'/'fluxos'
OUT.mkdir(parents=True,exist_ok=True)
sys.stdout.reconfigure(encoding='utf-8')
today=date.today()
captures=[]

with tempfile.TemporaryDirectory() as temporary:
    process=subprocess.Popen([sys.executable,'server.py','--port','8004','--db',str(Path(temporary)/'flows.db')],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    try:
        for _ in range(80):
            try:
                urllib.request.urlopen('http://127.0.0.1:8004',timeout=1).close()
                break
            except OSError:
                time.sleep(.2)
        with sync_playwright() as playwright:
            browser=playwright.chromium.launch(channel='chrome',headless=True)
            page=browser.new_page(viewport={'width':1440,'height':1050})
            page.set_default_timeout(25000)
            errors=[]
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.goto('http://127.0.0.1:8004')

            def state():
                response=page.request.get('http://127.0.0.1:8004/api/state')
                assert response.status==200
                return response.json()

            def go(route):
                page.goto('http://127.0.0.1:8004/#'+route)
                page.locator('#content').wait_for()

            def click(action,id=None):
                locator=page.locator(f'[data-act="{action}"]'+(f'[data-id="{id}"]' if id is not None else ''))
                locator.first.click()

            def submit():
                page.locator('dialog button[type=submit]').click()
                page.wait_for_function('() => !document.querySelector("fieldset:disabled")')

            def close():
                page.get_by_role('button',name='Fechar',exact=True).click()

            def capture(slug,title,description,target=None):
                target=target or page
                target.wait_for_function('() => !document.querySelector("fieldset:disabled")')
                target.screenshot(path=str(OUT/f'{len(captures)+1:02}-{slug}.png'),full_page=True)
                captures.append({'file':f'{len(captures)+1:02}-{slug}.png','title':title,'description':description})
                print(f'CAPTURA {len(captures):02}: {title}',flush=True)

            def login(role='admin'):
                page.locator('#login-form').wait_for()
                page.locator('[name=username]').select_option(role)
                page.get_by_role('button',name='Entrar no sistema').click()
                page.locator('.sidebar').wait_for()

            def attach(action,id,filename,kind=None):
                click(action,id)
                if kind:page.locator('[name=kind]').select_option(kind)
                page.locator('[name=file]').set_input_files(str(ROOT/'exemplos'/filename))
                submit()
                page.locator('dialog .doc-item').first.wait_for()

            login()
            capture('painel','Visão geral integrada','Dados fictícios carregados da API Python e persistidos no SQLite.')
            go('patients');click('patient-new')
            for name,value in [('name','Paciente do fluxo React'),('address','Rua de demonstração, 100'),('boarding','Praça de demonstração'),('companion','Acompanhante do fluxo React'),('phone','(81) 00000-0000')]:
                page.locator(f'[name={name}]').fill(value)
            page.locator('[name=accessible]').check()
            capture('cadastro','Cadastro de paciente e acompanhante','Formulário preenchido com acessibilidade, endereço e ponto de embarque.')
            submit();page.locator('dialog').wait_for(state='hidden')
            pid=max(p['id'] for p in state()['patients'])
            click('patient-detail',pid)
            capture('historico','Cadastro persistido','Histórico recuperado da API após salvar o paciente.')
            close();go('fleet');click('facility-new')
            for name,value in [('name','Referência do fluxo React'),('cnes','0000999'),('city','Recife'),('address','Endereço fictício de referência')]:page.locator(f'[name={name}]').fill(value)
            submit();page.locator('dialog').wait_for(state='hidden')
            fid=max(f['id'] for f in state()['facilities'])
            click('driver-new')
            for name,value in [('name','Motorista do fluxo React'),('license','FICTICIA-123'),('valid_until','2099-12-31')]:page.locator(f'[name={name}]').fill(value)
            submit();page.locator('dialog').wait_for(state='hidden')
            did=max(d['id'] for d in state()['drivers'])
            click('vehicle-new')
            for name,value in [('name','Veículo do fluxo React'),('plate','FLOW-001'),('capacity','2')]:page.locator(f'[name={name}]').fill(value)
            page.locator('[name=accessible]').check();submit();page.locator('dialog').wait_for(state='hidden')
            vid=max(v['id'] for v in state()['vehicles'])
            capture('recursos','Frota, motorista e referência cadastrados','Recursos reutilizados nos próximos passos de solicitação e planejamento.')

            def create_request(kind,companion=False):
                go('requests');click('request-new')
                page.locator('[name=patient_id]').select_option(str(pid))
                page.locator('[name=facility_id]').select_option(str(fid))
                page.locator('[name=kind]').select_option(kind)
                page.locator('[name=specialty]').fill('Cardiologia demonstrativa')
                page.locator('[name=end_date]').fill((today+timedelta(days=40)).isoformat())
                if companion:page.locator('[name=companion]').check()
                submit();page.locator('[data-act=document-request]').wait_for()
                return max(r['id'] for r in state()['requests'])

            rid=create_request('TFD',True)
            capture('solicitacao','Solicitação TFD em análise','Paciente e acompanhante vinculados à unidade de referência.')
            click('request-decide',rid);page.locator('[name=reason]').fill('Conferência acadêmica')
            submit();expect(page.locator('.form-error')).to_contain_text('laudo')
            capture('bloqueio-laudo','Bloqueio de autorização sem laudo','A API rejeitou a autorização; a interface apresentou a pendência.')
            page.locator('[name=status]').select_option('Pendente');page.locator('[name=reason]').fill('Laudo fictício ainda não apresentado');submit()
            capture('pendencia','Pendência documental registrada','Decisão e justificativa preservadas no processo.')
            attach('document-request',rid,'laudo-ficticio.txt')
            capture('laudo','Laudo anexado ao processo','Documento disponível para download e vinculado à solicitação.')
            click('request-decide',rid);page.locator('[name=reason]').fill('Laudo fictício conferido para demonstração');submit()
            capture('autorizacao','Solicitação autorizada','Calendário disponível após decisão registrada no Python.')
            click('schedule-new',rid);submit();page.locator('dialog').wait_for(state='hidden')
            oid=next(o['id'] for o in state()['occurrences'] if o['request_id']==rid and o['date']==today.isoformat())
            go('calendar');click('schedule-new')
            page.locator('[name=request_id]').select_option(str(rid))
            page.locator('[name=start_date]').fill((today+timedelta(days=1)).isoformat())
            page.locator('[name=end_date]').fill((today+timedelta(days=35)).isoformat())
            page.locator('[name=weekday][value="1"]').check();page.locator('[name=weekday][value="3"]').check()
            capture('recorrencia','Configuração de recorrência semanal','Terças e quintas, respeitando a validade da autorização.')
            submit();page.locator('dialog').wait_for(state='hidden')
            capture('calendario','Agendamento avulso e calendário','Ocorrência de hoje e recorrências vinculadas ao mesmo processo.')
            next_month=(today.replace(day=1)+timedelta(days=32)).replace(day=1).strftime('%Y-%m')
            page.locator('#month').fill(next_month)
            capture('competencia','Continuidade entre competências','O mesmo paciente e processo aparecem no mês seguinte, sem novo cadastro.')

            def create_trip(start='18:00',end='20:00'):
                go('trips');click('trip-new')
                page.locator('[name=vehicle_id]').select_option(str(vid));page.locator('[name=driver_id]').select_option(str(did))
                page.locator('[name=departure]').fill(start);page.locator('[name=arrival]').fill(end)
                submit();page.locator('[data-act=trip-allocate]').wait_for()
                return max(t['id'] for t in state()['trips'])

            tid=create_trip();capture('viagem','Viagem planejada','Veículo acessível, motorista, rota e horários persistidos.')
            click('trip-allocate',tid);page.locator('[name=occurrence_id]').select_option(str(oid));submit()
            capture('alocacao','Paciente e acompanhante alocados','Dois lugares reservados no veículo de dois passageiros.')
            click('trip-allocate',tid);page.locator('[name=occurrence_id]').select_option('4');submit()
            expect(page.locator('.form-error')).to_contain_text('Capacidade')
            capture('lotacao','Bloqueio por capacidade','Tentativa de incluir mais passageiros rejeitada pelo backend.')
            close();click('trip-detail',tid);click('confirm',oid)
            capture('confirmacao','Confirmação assistida','Confirmação alimenta a mesma lista operacional do motorista.')
            click('board',oid);capture('embarque','Embarque registrado','Deslocamento registrado sem transformar automaticamente em atendimento.')
            click('trip-close',tid)
            for name,value in [('km','220'),('liters','22'),('cost','180')]:page.locator(f'[name={name}]').fill(value)
            submit();capture('encerramento','Viagem encerrada','Quilometragem, consumo e custo real ligados à viagem.')
            close();go('review');page.locator('#month').fill(today.strftime('%Y-%m'));click('occurrence-detail',oid)
            click('occurrence-prove',oid);submit();expect(page.locator('.form-error')).to_contain_text('declaração')
            capture('bloqueio-comprovacao','Bloqueio sem declaração','Embarque isolado não é aceito como comprovação do atendimento.')
            close();click('occurrence-detail',oid);attach('document-occurrence',oid,'declaracao-paciente.txt','Declaração do paciente')
            click('occurrence-prove',oid);submit()
            capture('prova-paciente','Atendimento do paciente comprovado','Acompanhante permanece pendente, apesar da comprovação do paciente.')
            attach('document-occurrence',oid,'declaracao-acompanhante.txt','Declaração do acompanhante')
            click('occurrence-prove',oid);page.locator('[name=companion_proof]').check();submit()
            capture('prova-acompanhante','Acompanhante comprovado separadamente','Duas declarações ligadas à mesma ocorrência, com estados independentes.')
            close();capture('conferencia','Conferência mensal atualizada','A matriz apresenta o resultado da comprovação e abre seus documentos.')
            go('finance');page.locator('#month').fill(today.strftime('%Y-%m'));click('benefit-calculate');submit();page.locator('dialog').wait_for(state='hidden')
            capture('calculo','Benefícios calculados','Itens separados para paciente e acompanhante; valores demonstrativos.')
            benefits=[b for b in state()['benefits'] if b['occurrence_id']==oid]
            assert len(benefits)==2
            bid=next(b['id'] for b in benefits if b['beneficiary']=='Paciente')
            click('benefit-advance',bid);submit();page.locator('dialog').wait_for(state='hidden')
            capture('aprovacao','Benefício aprovado','Etapa de aprovação distinta do cálculo e do pagamento.')
            click('benefit-advance',bid);page.locator('[name=accounting_ref]').fill('DEMO-REACT-2026');submit();page.locator('dialog').wait_for(state='hidden')
            capture('contabilidade','Encaminhamento à contabilidade registrado','Referência contábil fictícia salva; nenhum envio externo é efetuado.')
            click('benefit-advance',bid);submit();page.locator('dialog').wait_for(state='hidden');page.reload();page.locator('#content').wait_for()
            assert next(b for b in state()['benefits'] if b['id']==bid)['status']=='Pago'
            capture('pagamento','Pagamento registrado e persistido','Situação recuperada após recarregar a aplicação React.')
            with page.expect_download() as download:
                page.get_by_role('link',name='Exportar folha').click()
            download.value.save_as(str(OUT/'folha-demonstrativa.csv'))
            assert 'DEMO-REACT-2026' in (OUT/'folha-demonstrativa.csv').read_text(encoding='utf-8-sig')
            capture('exportacao','Folha CSV exportada','Arquivo baixado e conferido automaticamente; acompanha esta galeria.')
            click('rule-new');page.locator('[name=patient_rate]').fill('40');page.locator('[name=companion_rate]').fill('30');submit();page.locator('dialog').wait_for(state='hidden')
            click('benefit-calculate');submit();page.locator('dialog').wait_for(state='hidden')
            assert next(b for b in state()['benefits'] if b['id']==bid)['amount_cents']==3500
            assert len([b for b in state()['benefits'] if b['occurrence_id']==oid])==2
            capture('regra','Regra versionada e recálculo sem duplicidade','Nova regra não alterou o benefício já calculado nem duplicou os itens.')

            transport_rid=create_request('Transporte sanitário')
            attach('document-request',transport_rid,'laudo-ficticio.txt')
            click('request-decide',transport_rid);page.locator('[name=reason]').fill('Consulta com transporte sanitário, sem enquadramento TFD');submit()
            capture('transporte-autorizado','Transporte sanitário autorizado','Modalidade própria, sem converter consulta em TFD.')
            click('schedule-new',transport_rid);submit();page.locator('dialog').wait_for(state='hidden')
            transport_oid=next(o['id'] for o in state()['occurrences'] if o['request_id']==transport_rid)
            transport_tid=create_trip('20:30','21:30')
            click('trip-allocate',transport_tid);page.locator('[name=occurrence_id]').select_option(str(transport_oid));submit();click('confirm',transport_oid);click('board',transport_oid)
            click('trip-close',transport_tid)
            for name,value in [('km','220'),('liters','20'),('cost','170')]:page.locator(f'[name={name}]').fill(value)
            submit();close();go('review');click('occurrence-detail',transport_oid)
            attach('document-occurrence',transport_oid,'declaracao-paciente.txt','Declaração do paciente');click('occurrence-prove',transport_oid);submit()
            capture('transporte-comprovado','Transporte sanitário realizado e comprovado','O atendimento foi comprovado sem criar benefício de TFD.')
            close();go('finance');click('benefit-calculate');submit();page.locator('dialog').wait_for(state='hidden')
            assert not any(b['occurrence_id']==transport_oid for b in state()['benefits'])
            capture('transporte-sem-beneficio','Transporte sanitário excluído do cálculo TFD','Verificação da API confirmou ausência de benefício para a ocorrência de transporte sanitário.')
            denied=create_request('Transporte sanitário');click('request-decide',denied);page.locator('[name=status]').select_option('Negada');page.locator('[name=reason]').fill('Cenário fictício: solicitação duplicada');submit()
            capture('negativa','Solicitação negada com justificativa','Decisão preservada para consulta e auditoria; não permite agendamento.')
            close();go('audit');click('audit-detail',state()['audit'][0]['id'])
            capture('auditoria','Auditoria com antes e depois','Última decisão vinculada ao autor, registro, motivo e horário.')
            close();click('logout');login('motorista');go('trips')
            driver_state=state()
            assert all(t['driver_id']==1 for t in driver_state['trips'])
            assert all('bank' not in p and 'cpf' not in p for p in driver_state['patients'])
            assert driver_state['documents']==[]
            capture('motorista','Perfil motorista com acesso restrito','A API retornou apenas suas viagens e campos operacionais, sem arquivos ou dados bancários.')
            click('trip-detail',1);capture('lista-motorista','Lista operacional do motorista','Pacientes, acompanhantes, embarque e confirmação; sem diagnóstico nem dados financeiros.')
            close()
            for role,route,title in [('regulacao','requests','Perfil regulação'),('transporte','fleet','Perfil transporte'),('financeiro','finance','Perfil financeiro'),('auditor','audit','Perfil controle interno')]:
                click('logout');login(role);go(route);capture(role,title,'Interface e operações disponíveis conforme o perfil autenticado no backend.')
            click('logout');login();go('trips');click('trip-detail',2);click('trip-release',6)
            page.locator('[name=reason]').fill('Reorganização demonstrativa do embarque');submit()
            capture('retirada','Retirada de passageiro com justificativa','Agendamento preservado; alteração de alocação registrada na auditoria.')
            click('trip-allocate',2);page.locator('[name=occurrence_id]').select_option('6');submit()
            capture('realocacao','Realocação de passageiro','O mesmo agendamento volta à viagem sem duplicar cadastro ou atendimento.')
            click('absent',6);capture('ausencia','Ausência registrada','Ausência distinta de embarque e de atendimento comprovado.')
            click('trip-close',2)
            for name,value in [('km','90'),('liters','9'),('cost','80')]:page.locator(f'[name={name}]').fill(value)
            submit();expect(page.locator('.form-error')).to_contain_text('Registre')
            capture('bloqueio-encerramento','Encerramento bloqueado por passageiro pendente','A viagem só encerra quando todos possuem embarque ou ausência registrados.')
            close();click('trip-detail',2);click('board',5)
            with page.expect_popup() as popup:
                click('trip-print',2)
            popup.value.wait_for_load_state()
            capture('lista-impressao','Lista operacional para impressão','Versão imprimível gerada pelo React com os passageiros e seus estados.',popup.value)
            popup.value.close();close();click('trip-new')
            page.locator('[name=vehicle_id]').select_option('1');page.locator('[name=driver_id]').select_option('1')
            submit();expect(page.locator('.form-error')).to_contain_text('alocado')
            capture('conflito-horario','Conflito de veículo ou motorista bloqueado','A API rejeita horários sobrepostos aos recursos já alocados.')
            close();go('fleet');click('driver-new')
            for name,value in [('name','Motorista CNH vencida fictício'),('license','TESTE-VENCIDA'),('valid_until','2000-01-01')]:page.locator(f'[name={name}]').fill(value)
            submit();page.locator('dialog').wait_for(state='hidden')
            expired=max(d['id'] for d in state()['drivers'])
            go('trips');click('trip-new');page.locator('[name=driver_id]').select_option(str(expired));submit()
            expect(page.locator('.form-error')).to_contain_text('CNH')
            capture('cnh-vencida','CNH vencida impede planejamento','Validade verificada na data da viagem antes da criação do registro.')
            close();click('trip-detail',1);click('trip-release',3)
            page.locator('[name=reason]').fill('Teste controlado de acessibilidade');submit();close();click('trip-new')
            page.locator('[name=vehicle_id]').select_option('3');page.locator('[name=driver_id]').select_option('3')
            page.locator('[name=departure]').fill('18:00');page.locator('[name=arrival]').fill('20:00');submit()
            inaccessible=max(t['id'] for t in state()['trips'])
            click('trip-allocate',inaccessible);page.locator('[name=occurrence_id]').select_option('3');submit()
            expect(page.locator('.form-error')).to_contain_text('acessível')
            capture('acessibilidade','Veículo incompatível com acessibilidade bloqueado','Passageiro com necessidade de acessibilidade não é alocado em veículo comum.')
            close();go('calendar');page.locator('#month').fill(today.strftime('%Y-%m'));click('schedule-new')
            page.locator('[name=request_id]').select_option(str(rid))
            page.locator('[name=start_date]').fill((today+timedelta(days=1)).isoformat());page.locator('[name=end_date]').fill((today+timedelta(days=35)).isoformat())
            page.locator('[name=weekday][value="1"]').check();page.locator('[name=weekday][value="3"]').check()
            count_before=len(state()['occurrences']);submit();page.locator('dialog').wait_for(state='hidden')
            assert len(state()['occurrences'])==count_before
            capture('agenda-sem-duplicidade','Recorrência repetida sem duplicar datas','Geração repetida verificada por contagem da API: nenhuma ocorrência adicional.')
            go('requests');click('request-detail',rid)
            with page.expect_download() as download:
                page.locator('dialog').get_by_role('link',name='Baixar').first.click()
            download.value.save_as(str(OUT/'laudo-baixado.txt'))
            assert 'SEM VALIDADE' in (OUT/'laudo-baixado.txt').read_text(encoding='utf-8')
            capture('documento-download','Download autenticado do laudo','Conteúdo baixado e conferido; acesso registrado na auditoria.')
            assert not errors,errors
            report={'result':'PASS','date':today.isoformat(),'frontend':'React','backend':'Python/SQLite','database':'temporário isolado','screenshots':len(captures),'javascript_errors':errors,'checks':['fluxo TFD completo','acompanhante separado','recorrência entre competências e sem duplicação','bloqueio sem laudo','capacidade com acompanhante','bloqueio sem declaração','pagamento persistente','CSV exportado','regra versionada','recálculo sem duplicidade','transporte sanitário sem benefício','negativa com motivo','auditoria','seis perfis autenticados','retirada e realocação','ausência e bloqueio de encerramento','lista imprimível','conflito de horário','CNH vencida','acessibilidade','download autenticado'],'captures':captures}
            (OUT/'manifesto.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
            print(json.dumps({k:v for k,v in report.items() if k!='captures'},ensure_ascii=False),flush=True)
            browser.close()
    finally:
        process.terminate()
        process.wait(timeout=10)
