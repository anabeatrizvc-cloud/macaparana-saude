import argparse
import csv
import hmac
import io
import json
import mimetypes
import secrets
import sqlite3
import threading
import time
from contextlib import closing
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from app.domain import connect, execute, get, log, state, RuleError, require
from app.seed import initialize, password_hash

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT/'data'/'macaparana.db'
SESSIONS = {}
ATTEMPTS = {}
LOCK = threading.Lock()


class Handler(BaseHTTPRequestHandler):
    server_version = 'MacaparanaDemo/1.0'

    def log_message(self, format, *args):
        pass

    def send(self, status, content, mime='application/json; charset=utf-8', extra=None):
        if isinstance(content, (dict, list)):
            content = json.dumps(content, ensure_ascii=False).encode('utf-8')
        elif isinstance(content,str):
            content = content.encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type',mime)
        self.send_header('Content-Length',str(len(content)))
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('X-Frame-Options','DENY')
        self.send_header('Referrer-Policy','same-origin')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'")
        for k,v in (extra or {}).items():
            self.send_header(k,v)
        self.end_headers()
        self.wfile.write(content)

    def user(self, db):
        cookie = SimpleCookie()
        try:
            cookie.load(self.headers.get('Cookie',''))
            token = cookie['session'].value if 'session' in cookie else ''
        except Exception:
            token = ''
        with LOCK:
            entry = SESSIONS.get(token)
            if entry and entry[1] < time.time():
                SESSIONS.pop(token,None)
                entry = None
        if not entry:
            return None
        return get(db,'users',entry[0])

    def do_GET(self):
        path = urlparse(self.path).path
        if path.startswith('/api/'):
            with closing(connect(DB_PATH)) as db:
                user = self.user(db)
                if not user:
                    return self.send(401,{'error':'Entre para continuar.'})
                try:
                    if path == '/api/state':
                        return self.send(200,state(db,user))
                    if path == '/api/production/export':
                        require(user['role'] in ('admin','faturamento','auditor'), 'Perfil sem acesso à produção.')
                        month = parse_qs(urlparse(self.path).query).get('month',[''])[0]
                        from app.domain import day
                        day(month+'-01')
                        rows = db.execute('''SELECT pr.id,o.id,r.id,p.name,p.cns,f.cnes,r.kind,r.specialty,o.date,o.trip_id,o.attendance,o.permanence,o.companion_proof,pr.procedure_code,pr.quantity,pr.destination,pr.status,pr.protocol,pr.note FROM production pr JOIN occurrences o ON o.id=pr.occurrence_id JOIN requests r ON r.id=o.request_id JOIN patients p ON p.id=r.patient_id JOIN facilities f ON f.id=r.facility_id WHERE substr(o.date,1,7)=? ORDER BY o.date,pr.id''',(month,)).fetchall()
                        stream = io.StringIO()
                        writer = csv.writer(stream,delimiter=';')
                        writer.writerow(['Preparacao_ID','Ocorrencia_ID','Solicitacao_ID','Paciente','CNS','CNES_referencia','Modalidade','Especialidade','Data','Viagem_ID','Atendimento_comprovado','Permanencia','Acompanhante_comprovado','Procedimento_informado','Quantidade','Destino_revisao','Situacao','Protocolo_interno','Observacoes'])
                        for row in rows:
                            writer.writerow(["'"+str(v) if str(v).lstrip().startswith(('=','+','-','@')) else v for v in row])
                        log(db,user,'production.export','production',after={'month':month,'rows':len(rows),'format':'preparacao interna, nao oficial'})
                        db.commit()
                        return self.send(200,'\ufeff'+stream.getvalue(),'text/csv; charset=utf-8',{'Content-Disposition':'attachment; filename="preparacao-producao.csv"'})
                    if path.startswith('/api/documents/'):
                        require(user['role'] in ('admin','regulacao','financeiro','faturamento','auditor'), 'Seu perfil não pode acessar documentos.')
                        document = get(db,'documents',int(path.rsplit('/',1)[1]))
                        log(db,user,'document.download','documents',document['id'])
                        db.commit()
                        return self.send(200,document['content'],document['mime'],{'Content-Disposition':f'attachment; filename="documento-{document["id"]}{Path(document["name"]).suffix}"'})
                    if path == '/api/export':
                        require(user['role'] in ('admin','financeiro','auditor'), 'Seu perfil não pode exportar a folha.')
                        rows=db.execute('SELECT b.id,p.name,o.date,b.beneficiary,b.amount_cents,b.status,b.accounting_ref,b.payment_date FROM benefits b JOIN occurrences o ON o.id=b.occurrence_id JOIN requests r ON r.id=o.request_id JOIN patients p ON p.id=r.patient_id ORDER BY o.date,p.name').fetchall()
                        stream=io.StringIO()
                        writer=csv.writer(stream,delimiter=';')
                        writer.writerow(['ID','Paciente fictício','Atendimento','Beneficiário','Valor demonstrativo (R$)','Situação','Referência contábil','Pagamento'])
                        for row in rows:
                            values=list(row)
                            values[4]=f'{values[4]/100:.2f}'.replace('.',',')
                            writer.writerow(["'"+str(v) if str(v).lstrip().startswith(('=','+','-','@')) else v for v in values])
                        log(db,user,'benefit.export','benefits',after={'rows':len(rows)})
                        db.commit()
                        return self.send(200,'\ufeff'+stream.getvalue(),'text/csv; charset=utf-8',{'Content-Disposition':'attachment; filename="folha-demonstrativa.csv"'})
                    return self.send(404,{'error':'Recurso não encontrado.'})
                except (RuleError,ValueError) as error:
                    return self.send(400,{'error':str(error)})
        if path == '/':
            target = ROOT/'static'/'build'/'index.html'
        elif path.startswith('/docs/'):
            target = (ROOT/path.lstrip('/')).resolve()
            if not target.is_relative_to(ROOT/'docs'):
                return self.send(404,'Não encontrado','text/plain')
        else:
            target=(ROOT/'static'/path.lstrip('/')).resolve()
            if not target.is_relative_to(ROOT/'static'):
                return self.send(404,'Não encontrado','text/plain')
        if not target.is_file():
            return self.send(404,'Não encontrado','text/plain')
        mime=mimetypes.guess_type(target)[0] or 'application/octet-stream'
        if target.suffix=='.js':
            mime='text/javascript'
        self.send(200,target.read_bytes(),mime+('; charset=utf-8' if mime.startswith('text/') else ''))

    def do_POST(self):
        path = urlparse(self.path).path
        if self.headers.get('X-App') != 'macaparana':
            return self.send(403,{'error':'Origem da operação não reconhecida.'})
        origin=self.headers.get('Origin')
        if origin and origin not in (f'http://127.0.0.1:{self.server.server_port}',f'http://localhost:{self.server.server_port}'):
            return self.send(403,{'error':'Origem não permitida.'})
        try:
            length=int(self.headers.get('Content-Length','0'))
            require(0<length<=6*1024*1024,'Requisição vazia ou maior que 6 MB.')
            data=json.loads(self.rfile.read(length))
            require(isinstance(data,dict),'Formato inválido.')
        except (RuleError,ValueError) as error:
            return self.send(400,{'error':str(error)})
        with closing(connect(DB_PATH)) as db:
            try:
                if path == '/api/login':
                    key=self.client_address[0]
                    with LOCK:
                        attempts=[t for t in ATTEMPTS.get(key,[]) if t>time.time()-60]
                        require(len(attempts)<15,'Muitas tentativas. Aguarde um minuto.')
                        ATTEMPTS[key]=attempts+[time.time()]
                    row=db.execute('SELECT * FROM users WHERE username=?',(str(data.get('username','')),)).fetchone()
                    require(row and hmac.compare_digest(row['password'],password_hash(str(data.get('password','')),row['salt'])),'Usuário ou senha incorretos.')
                    token=secrets.token_urlsafe(32)
                    with LOCK:
                        SESSIONS[token]=(row['id'],time.time()+8*3600)
                        ATTEMPTS.pop(key,None)
                    log(db,dict(row),'login','users',row['id'])
                    db.commit()
                    return self.send(200,{'message':'Bem-vindo.'},extra={'Set-Cookie':f'session={token}; HttpOnly; SameSite=Strict; Path=/; Max-Age=28800'})
                user=self.user(db)
                if not user:
                    return self.send(401,{'error':'Sessão encerrada. Entre novamente.'})
                if path == '/api/logout':
                    cookie=SimpleCookie(self.headers.get('Cookie',''))
                    with LOCK:
                        SESSIONS.pop(cookie['session'].value,None)
                    return self.send(200,{'message':'Sessão encerrada.'},extra={'Set-Cookie':'session=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0'})
                if path == '/api/action':
                    db.execute('BEGIN IMMEDIATE')
                    result=execute(db,user,str(data.get('action','')),data.get('data',{}))
                    db.commit()
                    return self.send(200,result)
                return self.send(404,{'error':'Operação não encontrada.'})
            except RuleError as error:
                db.rollback()
                return self.send(400,{'error':str(error)})
            except sqlite3.IntegrityError:
                db.rollback()
                return self.send(409,{'error':'Registro duplicado ou vínculo inválido. Verifique os dados.'})
            except (ValueError,TypeError,KeyError) as error:
                db.rollback()
                return self.send(400,{'error':'Dados inválidos. Confira os campos enviados.'})
            except Exception:
                db.rollback()
                import traceback
                traceback.print_exc()
                return self.send(500,{'error':'Erro interno. Consulte o terminal do servidor.'})


def main():
    global DB_PATH
    parser=argparse.ArgumentParser(description='Macaparana Saúde — demonstração acadêmica local')
    parser.add_argument('--port',type=int,default=8000)
    parser.add_argument('--db',type=Path,default=DB_PATH)
    args=parser.parse_args()
    DB_PATH=args.db.resolve()
    DB_PATH.parent.mkdir(parents=True,exist_ok=True)
    with closing(connect(DB_PATH)) as db:
        initialize(db)
    server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
    print(f'\nMacaparana Saúde | http://localhost:{args.port}\nLogin: admin | Senha: demo123\nDados exclusivamente fictícios. Ctrl+C para sair.\n',flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__=='__main__':
    main()
