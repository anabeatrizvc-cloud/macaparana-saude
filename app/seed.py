import hashlib
import secrets
from datetime import date, timedelta
from pathlib import Path
from app.domain import insert, now, log


def password_hash(password, salt):
    return hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), 160000).hex()


def initialize(db):
    db.executescript(Path(__file__).with_name('schema.sql').read_text(encoding='utf-8'))
    from app.extensions import migrate
    migrate(db)
    if db.execute('SELECT 1 FROM users').fetchone():
        if not db.execute("SELECT 1 FROM users WHERE username='faturamento'").fetchone():
            salt = secrets.token_hex(16)
            insert(db, 'users', dict(username='faturamento', name='Faturamento', role='faturamento', salt=salt, password=password_hash('demo123', salt)))
            db.commit()
        return
    for username, name, role in [('admin','Gestão municipal','admin'), ('regulacao','Equipe de regulação','regulacao'), ('transporte','Equipe de transporte','transporte'), ('motorista','Carlos · motorista','motorista'), ('financeiro','Equipe financeira','financeiro'), ('auditor','Controle interno','auditor'), ('faturamento','Faturamento','faturamento')]:
        salt = secrets.token_hex(16)
        insert(db, 'users', dict(username=username, name=name, role=role, salt=salt, password=password_hash('demo123', salt), driver_id=1 if role=='motorista' else None))
    today = date.today()
    start = today.replace(day=1)
    end = today+timedelta(days=100)
    for name, cnes, city in [('Centro de Referência Recife · fictício','0000001','Recife'),('Policlínica Regional · fictícia','0000002','Carpina'),('Unidade Especializada · fictícia','0000003','Limoeiro')]:
        insert(db,'facilities',dict(name=name,cnes=cnes,city=city,address='Endereço ilustrativo — validar com a unidade'))
    for name,plate,capacity,accessible in [('Van acessível','DEMO-001',8,1),('Micro-ônibus','DEMO-002',20,0),('Van executiva','DEMO-003',12,0)]:
        insert(db,'vehicles',dict(name=name,plate=plate,capacity=capacity,accessible=accessible))
    for name in ['Carlos Oliveira · fictício','Marcos Ferreira · fictício','Ana Souza · fictícia']:
        insert(db,'drivers',dict(name=name,license='DEMONSTRAÇÃO',valid_until=(today+timedelta(days=365)).isoformat()))
    names = ['Maria de Lourdes','José Antônio','Ana Beatriz','Francisco Silva','Rosa Maria','Pedro Henrique','Lúcia Helena','Antônio Pereira']
    specialties = ['Oncologia','Cardiologia','Fisioterapia','Nefrologia','Oftalmologia','Ortopedia','Neurologia','Cardiologia']
    for i,name in enumerate(names,1):
        insert(db,'patients',dict(name=name+' · fictício',cpf=None,cns='',birth=f'{1955+i*4}-03-12',phone='(81) 00000-0000',address=f'Rua demonstrativa, {i*10} · Macaparana/PE',boarding=['Praça central','UBS Centro','Praça São José'][i%3],accessible=int(i==3),companion='Acompanhante demonstrativo' if i in (1,3,4) else '',companion_cpf='',bank='Dados bancários não cadastrados',created_at=now()))
        insert(db,'requests',dict(patient_id=i,facility_id=1 if i<5 else 2,kind='TFD' if i<5 else 'Transporte sanitário',specialty=specialties[i-1],companion=int(i in (1,3,4)),start_date=start.isoformat(),end_date=end.isoformat(),status='Em análise' if i>6 else 'Autorizada',reason='Cenário fictício para apresentação',created_at=now()))
        content=f'LAUDO FICTÍCIO\nPaciente demonstrativo {i}\nDocumento sem validade clínica. Uso exclusivo acadêmico.'.encode()
        insert(db,'documents',dict(request_id=i,kind='Laudo',name=f'laudo-demo-{i}.txt',mime='text/plain',hash=hashlib.sha256(content).hexdigest(),content=content,created_at=now(),user_id=1))
    yesterday = today-timedelta(days=1)
    for travel_date,vehicle,driver,city,status in [(today,1,1,'Recife','Planejada'),(today,2,2,'Carpina','Planejada'),(today+timedelta(days=1),3,3,'Recife','Planejada'),(yesterday,1,1,'Recife','Encerrada')]:
        insert(db,'trips',dict(date=travel_date.isoformat(),departure='05:00',arrival='17:00',destination=city,route=f'Macaparana → {city} → Macaparana',vehicle_id=vehicle,driver_id=driver,estimated_km=220 if city=='Recife' else 90,status=status,km=224 if status=='Encerrada' else 0,liters=24 if status=='Encerrada' else 0,cost_cents=18000 if status=='Encerrada' else 0))
    for request_id in range(1,7):
        insert(db,'occurrences',dict(request_id=request_id,date=today.isoformat(),trip_id=1 if request_id<4 else (2 if request_id>=5 else None),confirmation='Confirmado' if request_id in (1,2,5) else 'Pendente'))
    for request_id in (1,2,4):
        occ = insert(db,'occurrences',dict(request_id=request_id,date=yesterday.isoformat(),trip_id=4,confirmation='Confirmado',boarding='Embarcou',attendance=1,companion_proof=int(request_id==1),permanence='Atendimento ambulatorial no mesmo dia · exemplo'))
        for kind in ['Declaração do paciente']+(['Declaração do acompanhante'] if request_id==1 else []):
            content=f'{kind.upper()}\nOcorrência {occ}\nCOMPROVANTE FICTÍCIO SEM VALIDADE.\nData: {yesterday}'.encode()
            insert(db,'documents',dict(occurrence_id=occ,kind=kind,name=f'comprovante-demo-{occ}.txt',mime='text/plain',hash=hashlib.sha256(content).hexdigest(),content=content,created_at=now(),user_id=1))
    for offset in (7,14,21,28):
        insert(db,'occurrences',dict(request_id=1,date=(today+timedelta(days=offset)).isoformat()))
    insert(db,'rules',dict(patient_cents=3500,companion_cents=2500,label='Exemplo acadêmico v1 — por ocorrência, sem validade normativa',created_at=now()))
    for occ,beneficiary,amount,status in [(7,'Paciente',3500,'Pago'),(7,'Acompanhante',2500,'Contabilidade'),(8,'Paciente',3500,'Calculado')]:
        insert(db,'benefits',dict(occurrence_id=occ,beneficiary=beneficiary,rule_id=1,amount_cents=amount,status=status,accounting_ref='DEMO-2026' if status!='Calculado' else None,payment_date=today.isoformat() if status=='Pago' else None))
    user = dict(db.execute('SELECT * FROM users WHERE id=1').fetchone())
    log(db,user,'demo.initialize','system',after={'description':'Base inicial fictícia. Eventos históricos simulados, sem representar atos municipais reais.'})
    db.commit()
