import base64
import hashlib
import json
import re
import sqlite3
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


class RuleError(Exception):
    pass


def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def require(condition, message):
    if not condition:
        raise RuleError(message)


def required(data, key, limit=300):
    value = str(data.get(key, '')).strip()
    require(bool(value), f'Preencha o campo {key}.')
    require(len(value) <= limit, f'O campo {key} excede {limit} caracteres.')
    return value


def day(value):
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        raise RuleError('Data inválida.')


def number(data, key, minimum=0, maximum=1000000):
    try:
        value = float(data.get(key, 0))
    except (ValueError, TypeError):
        raise RuleError(f'Valor inválido: {key}.')
    require(minimum <= value <= maximum, f'Valor fora do intervalo: {key}.')
    return value


def get(db, table, identifier):
    row = db.execute(f'SELECT * FROM {table} WHERE id=?', (identifier,)).fetchone()
    require(row is not None, 'Registro não encontrado.')
    return dict(row)


def insert(db, table, data):
    keys = list(data)
    cursor = db.execute(f'INSERT INTO {table} ({",".join(keys)}) VALUES ({",".join("?" for _ in keys)})', [data[k] for k in keys])
    return cursor.lastrowid


def update(db, table, identifier, data):
    db.execute(f'UPDATE {table} SET {",".join(k+"=?" for k in data)} WHERE id=?', [*data.values(), identifier])


def log(db, user, action, table, identifier=None, before=None, after=None, reason=''):
    insert(db, 'audit', dict(user_id=user['id'], actor=user['name'], action=action, entity=table, entity_id=identifier,
                            before_json=json.dumps(before, ensure_ascii=False) if before else None,
                            after_json=json.dumps(after, ensure_ascii=False) if after else None,
                            reason=reason, created_at=now()))


PERMISSIONS = {
    'patient.create': {'admin', 'regulacao'}, 'request.create': {'admin', 'regulacao'},
    'request.decide': {'admin', 'regulacao'}, 'schedule.create': {'admin', 'regulacao'},
    'trip.create': {'admin', 'transporte'}, 'trip.allocate': {'admin', 'transporte'},
    'trip.release': {'admin', 'transporte'}, 'trip.close': {'admin', 'transporte', 'motorista'},
    'occurrence.confirm': {'admin', 'transporte', 'motorista'},
    'occurrence.board': {'admin', 'transporte', 'motorista'},
    'occurrence.prove': {'admin', 'regulacao'}, 'document.create': {'admin', 'regulacao'},
    'benefit.calculate': {'admin', 'financeiro'}, 'benefit.advance': {'admin', 'financeiro'},
    'vehicle.create': {'admin', 'transporte'}, 'driver.create': {'admin', 'transporte'},
    'facility.create': {'admin', 'regulacao'}, 'rule.create': {'admin'},
}


def execute(db, user, action, data):
    from app.extensions import PERMISSIONS as EXTRA, execute_extension
    if action in EXTRA:
        return execute_extension(db, user, action, data)
    require(user['role'] in PERMISSIONS.get(action, set()), 'Seu perfil não tem permissão para esta ação.')
    entity = action.split('.')[0]
    identifier = data.get('id')
    before = None
    result = {}
    table = None
    if action == 'patient.create':
        cpf = re.sub(r'\D', '', str(data.get('cpf', '')))
        require(not cpf or len(cpf) == 11, 'CPF deve ter 11 dígitos (dados fictícios nesta demonstração).')
        cns = str(data.get('cns', '')).strip()
        require(not cns or (cns.isdigit() and len(cns) == 15), 'CNS deve ter 15 dígitos.')
        birth = str(data.get('birth', ''))
        if birth:
            require(day(birth) <= date.today(), 'Nascimento não pode estar no futuro.')
        table = 'patients'
        result = dict(name=required(data, 'name'), cpf=cpf or None, cns=cns, birth=birth,
                      phone=str(data.get('phone', ''))[:30], address=required(data, 'address'),
                      boarding=required(data, 'boarding'), accessible=int(bool(data.get('accessible'))),
                      companion=str(data.get('companion', ''))[:150], companion_cpf=str(data.get('companion_cpf', ''))[:14],
                      bank=str(data.get('bank', ''))[:200], created_at=now())
    elif action == 'facility.create':
        table = 'facilities'
        cnes = required(data, 'cnes', 7)
        require(cnes.isdigit() and len(cnes) == 7, 'CNES deve ter 7 dígitos. A validação externa não está integrada.')
        result = dict(name=required(data, 'name'), cnes=cnes, city=required(data, 'city'), address=str(data.get('address', ''))[:300])
    elif action == 'vehicle.create':
        table = 'vehicles'
        result = dict(name=required(data, 'name'), plate=required(data, 'plate', 10).upper(), capacity=int(number(data, 'capacity', 1, 60)), accessible=int(bool(data.get('accessible'))))
    elif action == 'driver.create':
        table = 'drivers'
        result = dict(name=required(data, 'name'), license=required(data, 'license', 30), valid_until=day(data.get('valid_until')).isoformat())
    elif action == 'rule.create':
        table = 'rules'
        result = dict(patient_cents=round(number(data, 'patient_rate', 0, 10000)*100), companion_cents=round(number(data, 'companion_rate', 0, 10000)*100), label=required(data, 'label'), created_at=now())
    elif action == 'request.create':
        patient = get(db, 'patients', data.get('patient_id'))
        facility = get(db, 'facilities', data.get('facility_id'))
        require(facility['active'], 'Referência inativa.')
        require(data.get('kind') in ('TFD', 'Transporte sanitário'), 'Tipo de solicitação inválido.')
        start, end = day(data.get('start_date')), day(data.get('end_date'))
        require(start <= end, 'O fim da validade deve ser posterior ao início.')
        require(not data.get('companion') or patient['companion'], 'Cadastre um acompanhante no paciente.')
        table = 'requests'
        result = dict(patient_id=patient['id'], facility_id=facility['id'], kind=data['kind'], specialty=required(data, 'specialty'), companion=int(bool(data.get('companion'))), start_date=start.isoformat(), end_date=end.isoformat(), created_at=now())
    elif action == 'request.decide':
        table = 'requests'
        before = get(db, table, identifier)
        require(before['status'] in ('Em análise', 'Pendente'), 'Esta solicitação já foi decidida.')
        status = data.get('status')
        require(status in ('Autorizada', 'Pendente', 'Negada'), 'Decisão inválida.')
        reason = required(data, 'reason', 1000)
        if status == 'Autorizada':
            require(db.execute("SELECT 1 FROM documents WHERE request_id=? AND kind='Laudo'", (identifier,)).fetchone(), 'Anexe o laudo antes de autorizar.')
        result = dict(status=status, reason=reason)
    elif action == 'schedule.create':
        request = get(db, 'requests', data.get('request_id'))
        require(request['status'] == 'Autorizada', 'Autorize a solicitação antes de agendar.')
        start, end = day(data.get('start_date')), day(data.get('end_date'))
        require(start <= end and (end-start).days <= 366, 'Informe um período de até 366 dias.')
        require(request['start_date'] <= start.isoformat() <= end.isoformat() <= request['end_date'], 'As datas devem estar dentro da validade da autorização.')
        weekdays = data.get('weekdays', [])
        require(isinstance(weekdays, list), 'Dias da semana inválidos.')
        require(all(isinstance(d, int) and 0 <= d <= 6 for d in weekdays), 'Dia da semana inválido.')
        require(weekdays or start == end, 'Selecione os dias da semana ou use a mesma data para agendamento avulso.')
        count = 0
        for offset in range((end-start).days+1):
            current = start+timedelta(days=offset)
            if not weekdays or current.weekday() in weekdays:
                cursor = db.execute('INSERT OR IGNORE INTO occurrences(request_id,date) VALUES (?,?)', (request['id'], current.isoformat()))
                count += cursor.rowcount
        log(db, user, action, 'requests', request['id'], after=dict(created=count, **data))
        return dict(message=f'{count} agendamento(s) criado(s). Datas existentes foram preservadas.')
    elif action == 'trip.create':
        table = 'trips'
        vehicle = get(db, 'vehicles', data.get('vehicle_id'))
        driver = get(db, 'drivers', data.get('driver_id'))
        travel_date = day(data.get('date')).isoformat()
        require(vehicle['active'] and driver['active'], 'Veículo ou motorista indisponível.')
        require(driver['valid_until'] >= travel_date, 'CNH vencida na data da viagem.')
        departure, arrival = required(data, 'departure'), required(data, 'arrival')
        require(all(re.fullmatch(r'(?:[01]\d|2[0-3]):[0-5]\d', x) for x in (departure, arrival)), 'Horário inválido.')
        require(departure < arrival, 'O retorno deve ser após a saída, no mesmo dia.')
        conflict = db.execute('SELECT id FROM trips WHERE date=? AND departure<? AND arrival>? AND (vehicle_id=? OR driver_id=?)', (travel_date, arrival, departure, vehicle['id'], driver['id'])).fetchone()
        require(not conflict, 'Veículo ou motorista já está alocado nesse horário.')
        result = dict(date=travel_date, departure=departure, arrival=arrival, destination=required(data, 'destination'), route=required(data, 'route'), vehicle_id=vehicle['id'], driver_id=driver['id'], estimated_km=number(data, 'estimated_km', 0, 5000))
    elif action in ('trip.allocate', 'trip.release'):
        trip = get(db, 'trips', data.get('trip_id'))
        require(trip['status'] == 'Planejada', 'A viagem está encerrada.')
        identifier = data.get('occurrence_id')
        table = 'occurrences'
        before = get(db, table, identifier)
        request = get(db, 'requests', before['request_id'])
        patient = get(db, 'patients', request['patient_id'])
        require(before['boarding'] == 'Pendente', 'Não é possível alterar alocação após registrar embarque ou ausência.')
        if action == 'trip.release':
            require(before['trip_id'] == trip['id'], 'O paciente não está nesta viagem.')
            required(data, 'reason', 1000)
            result = dict(trip_id=None, confirmation='Pendente')
        else:
            require(not before['trip_id'], 'Este agendamento já está alocado.')
            require(request['status'] == 'Autorizada' and before['date'] == trip['date'], 'Data da viagem incompatível ou solicitação não autorizada.')
            vehicle = get(db, 'vehicles', trip['vehicle_id'])
            require(not patient['accessible'] or vehicle['accessible'], 'O paciente precisa de veículo acessível.')
            from app.extensions import capacity, stops
            start = int(data.get('segment_start', 0))
            end = int(data.get('segment_end', len(stops(db, trip['id']))-1))
            capacity(db, trip, request, start, end)
            other = db.execute('SELECT o.id FROM occurrences o JOIN requests r ON r.id=o.request_id JOIN trips t ON t.id=o.trip_id WHERE r.patient_id=? AND t.date=? AND t.departure<? AND t.arrival>?', (patient['id'], trip['date'], trip['arrival'], trip['departure'])).fetchone()
            require(not other, 'Paciente já alocado em viagem com horário sobreposto.')
            result = dict(trip_id=trip['id'], segment_start=start, segment_end=end)
    elif action.startswith('occurrence.'):
        table = 'occurrences'
        before = get(db, table, identifier)
        require(before['trip_id'], 'Alocar em uma viagem antes desta etapa.')
        trip = get(db, 'trips', before['trip_id'])
        request = get(db, 'requests', before['request_id'])
        if user['role'] == 'motorista':
            require(trip['driver_id'] == user['driver_id'], 'Viagem de outro motorista.')
        if action == 'occurrence.confirm':
            require(trip['status'] == 'Planejada' and before['boarding'] == 'Pendente', 'A confirmação não pode ser alterada após o embarque ou encerramento.')
            require(data.get('status') in ('Confirmado', 'Recusado'), 'Confirmação inválida.')
            result = dict(confirmation=data['status'], confirmation_channel=str(data.get('channel', 'Assistida'))[:50], confirmation_note=str(data.get('note', 'Registro pela equipe municipal'))[:500])
        elif action == 'occurrence.board':
            require(before['date'] <= date.today().isoformat(), 'Não é possível registrar embarque futuro.')
            require(trip['status'] == 'Planejada' and before['boarding'] == 'Pendente', 'Embarque já registrado ou viagem encerrada.')
            require(data.get('status') in ('Embarcou', 'Ausente'), 'Situação inválida.')
            require(before['confirmation'] == 'Confirmado' or data['status'] == 'Ausente', 'Confirme o passageiro antes do embarque.')
            result = dict(boarding=data['status'])
        else:
            require(before['date'] <= date.today().isoformat(), 'Não é possível comprovar atendimento futuro.')
            require(before['boarding'] == 'Embarcou', 'O embarque deve estar registrado para conciliar o atendimento.')
            require(db.execute("SELECT 1 FROM documents WHERE occurrence_id=? AND kind='Declaração do paciente'", (identifier,)).fetchone(), 'Anexe a declaração do paciente.')
            companion = bool(data.get('companion_proof'))
            if companion:
                require(request['companion'], 'Acompanhante não autorizado.')
                require(db.execute("SELECT 1 FROM documents WHERE occurrence_id=? AND kind='Declaração do acompanhante'", (identifier,)).fetchone(), 'Anexe a declaração separada do acompanhante.')
            require(not before['companion_proof'] or companion, 'Comprovação existente não pode ser removida neste demonstrador.')
            result = dict(attendance=1, companion_proof=int(companion), permanence=required(data, 'permanence', 500))
    elif action == 'trip.close':
        table = 'trips'
        before = get(db, table, identifier)
        require(before['status'] == 'Planejada', 'Viagem já encerrada.')
        require(before['date'] <= date.today().isoformat(), 'Não é possível encerrar viagem futura.')
        if user['role'] == 'motorista':
            require(before['driver_id'] == user['driver_id'], 'Viagem de outro motorista.')
        passengers = db.execute('SELECT boarding FROM occurrences WHERE trip_id=?', (identifier,)).fetchall()
        require(passengers and all(p['boarding'] != 'Pendente' for p in passengers), 'Registre embarque ou ausência de todos os passageiros.')
        result = dict(status='Encerrada', km=number(data, 'km', 0.1, 10000), liters=number(data, 'liters', 0, 2000), cost_cents=round(number(data, 'cost', 0, 100000)*100), notes=str(data.get('notes', ''))[:1000])
    elif action == 'document.create':
        table = 'documents'
        is_request = bool(data.get('request_id'))
        require(is_request != bool(data.get('occurrence_id')), 'Vincule o documento a uma solicitação ou ocorrência.')
        related = get(db, 'requests' if is_request else 'occurrences', data.get('request_id') if is_request else data.get('occurrence_id'))
        kind = required(data, 'kind')
        require(kind in (['Laudo'] if is_request else ['Declaração do paciente', 'Declaração do acompanhante']), 'Tipo de documento incompatível.')
        try:
            content = base64.b64decode(data.get('content', ''), validate=True)
        except (ValueError, TypeError):
            raise RuleError('Arquivo inválido.')
        require(0 < len(content) <= 4*1024*1024, 'Anexe um arquivo de até 4 MB.')
        name = Path(required(data, 'name', 200)).name
        extension = Path(name).suffix.lower()
        mime = {'.pdf':'application/pdf', '.png':'image/png', '.jpg':'image/jpeg', '.jpeg':'image/jpeg', '.txt':'text/plain'}.get(extension)
        require(mime, 'Use PDF, PNG, JPG ou TXT.')
        result = dict(request_id=related['id'] if is_request else None, occurrence_id=None if is_request else related['id'], kind=kind, name=name, mime=mime, content=content, hash=hashlib.sha256(content).hexdigest(), created_at=now(), user_id=user['id'])
    elif action == 'benefit.calculate':
        month = required(data, 'month', 7)
        require(re.fullmatch(r'\d{4}-\d{2}', month), 'Competência inválida.')
        day(month+'-01')
        rule = dict(db.execute('SELECT * FROM rules ORDER BY id DESC LIMIT 1').fetchone())
        rows = db.execute("SELECT o.*,r.companion FROM occurrences o JOIN requests r ON r.id=o.request_id WHERE o.date LIKE ? AND r.kind='TFD' AND r.status='Autorizada' AND o.attendance=1 AND o.boarding='Embarcou'", (month+'%',)).fetchall()
        count = 0
        for row in rows:
            for beneficiary, amount in [('Paciente', rule['patient_cents']), ('Acompanhante', rule['companion_cents'])]:
                if beneficiary == 'Acompanhante' and not (row['companion'] and row['companion_proof']):
                    continue
                cursor = db.execute('INSERT OR IGNORE INTO benefits(occurrence_id,beneficiary,rule_id,amount_cents) VALUES (?,?,?,?)', (row['id'], beneficiary, rule['id'], amount))
                if cursor.rowcount:
                    count += 1
                    log(db, user, action, 'benefits', cursor.lastrowid, after=dict(occurrence_id=row['id'], beneficiary=beneficiary, rule_id=rule['id'], amount_cents=amount))
        return dict(message=f'{count} benefício(s) criado(s). Valores ilustrativos, sem validade para pagamento real.')
    elif action == 'benefit.advance':
        table = 'benefits'
        before = get(db, table, identifier)
        transitions = {'Calculado':'Aprovado', 'Aprovado':'Contabilidade', 'Contabilidade':'Pago'}
        require(before['status'] in transitions, 'Benefício já pago.')
        result = dict(status=transitions[before['status']])
        if result['status'] in ('Contabilidade', 'Pago'):
            result['accounting_ref'] = required(data, 'accounting_ref', 120)
        if result['status'] == 'Pago':
            paid = day(data.get('payment_date'))
            occurrence = get(db, 'occurrences', before['occurrence_id'])
            require(day(occurrence['date']) <= paid <= date.today(), 'Pagamento deve ocorrer entre o atendimento e hoje.')
            result['payment_date'] = paid.isoformat()
    else:
        raise RuleError('Ação desconhecida.')

    if before:
        update(db, table, identifier, result)
    else:
        identifier = insert(db, table, result)
    safe_result = {k:v for k,v in result.items() if k != 'content'}
    log(db, user, action, table, identifier, before, safe_result, str(data.get('reason', '')))
    return dict(id=identifier, message='Registro salvo com sucesso.')


def connect(path):
    db = sqlite3.connect(path, timeout=15)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    return db


def state(db, user):
    result = {}
    for table in ['patients','facilities','vehicles','drivers','requests','trips','occurrences','rules','benefits']:
        result[table] = [dict(row) for row in db.execute(f'SELECT * FROM {table} ORDER BY id DESC')]
    result['documents'] = [dict(row) for row in db.execute('SELECT id,request_id,occurrence_id,kind,name,hash,created_at FROM documents ORDER BY id DESC')]
    result['audit'] = [dict(row) for row in db.execute('SELECT * FROM audit ORDER BY id DESC LIMIT 300')] if user['role'] in ('admin','auditor') else []
    role = user['role']
    if role not in ('admin','financeiro','auditor'):
        result['benefits'] = []
        result['rules'] = []
        for patient in result['patients']:
            patient.pop('bank', None)
    if role == 'motorista':
        result['trips'] = [t for t in result['trips'] if t['driver_id'] == user['driver_id']]
        trip_ids = {t['id'] for t in result['trips']}
        result['occurrences'] = [{k:v for k,v in o.items() if k in ('id','request_id','date','trip_id','confirmation','boarding','segment_start','segment_end','confirmation_channel','confirmation_note')} for o in result['occurrences'] if o['trip_id'] in trip_ids]
        req_ids = {o['request_id'] for o in result['occurrences']}
        result['requests'] = [{k:v for k,v in r.items() if k in ('id','patient_id','facility_id','companion')} for r in result['requests'] if r['id'] in req_ids]
        patient_ids = {r['patient_id'] for r in result['requests']}
        result['patients'] = [{k:v for k,v in p.items() if k in ('id','name','phone','boarding','accessible','companion')} for p in result['patients'] if p['id'] in patient_ids]
        result['documents'] = []
        result['drivers'] = [d for d in result['drivers'] if d['id'] == user['driver_id']]
    elif role == 'transporte':
        result['documents'] = []
        for patient in result['patients']:
            for key in ('cpf','cns','birth','companion_cpf'):
                patient.pop(key, None)
    result['user'] = {k:user[k] for k in ('id','name','role','username')}
    result['today'] = date.today().isoformat()
    from app.extensions import extend_state
    return extend_state(db, user, result)
