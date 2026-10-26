import re
from app.domain import get, insert, update, require, required, number, day, now, log


def migrate(db):
    columns = {r['name'] for r in db.execute('PRAGMA table_info(occurrences)')}
    for name, definition in [('segment_start', 'INTEGER NOT NULL DEFAULT 0'), ('segment_end', 'INTEGER NOT NULL DEFAULT 1'), ('confirmation_channel', "TEXT NOT NULL DEFAULT 'Assistida'"), ('confirmation_note', "TEXT NOT NULL DEFAULT ''")]:
        if name not in columns:
            db.execute(f'ALTER TABLE occurrences ADD COLUMN {name} {definition}')
    db.executescript('''
    CREATE TABLE IF NOT EXISTS route_stops(id INTEGER PRIMARY KEY, trip_id INTEGER NOT NULL REFERENCES trips(id), position INTEGER NOT NULL, name TEXT NOT NULL, UNIQUE(trip_id,position));
    CREATE TABLE IF NOT EXISTS production(id INTEGER PRIMARY KEY, occurrence_id INTEGER NOT NULL UNIQUE REFERENCES occurrences(id), procedure_code TEXT NOT NULL, quantity INTEGER NOT NULL, destination TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Preparada', protocol TEXT, note TEXT NOT NULL, updated_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS service_records(id INTEGER PRIMARY KEY, kind TEXT NOT NULL, title TEXT NOT NULL, owner TEXT NOT NULL, status TEXT NOT NULL, notes TEXT NOT NULL, created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS pilot_measurements(id INTEGER PRIMARY KEY, indicator TEXT NOT NULL, unit TEXT NOT NULL, baseline REAL NOT NULL, measured REAL NOT NULL, start_date TEXT NOT NULL, end_date TEXT NOT NULL, source TEXT NOT NULL, responsible TEXT NOT NULL, scenario TEXT NOT NULL, created_at TEXT NOT NULL);
    ''')
    db.commit()


def stops(db, trip_id):
    values = [dict(r) for r in db.execute('SELECT * FROM route_stops WHERE trip_id=? ORDER BY position', (trip_id,))]
    return values or [dict(position=0, name='Origem'), dict(position=1, name='Destino / retorno')]


def capacity(db, trip, request, start, end):
    last = len(stops(db, trip['id'])) - 1
    require(0 <= start < end <= last, 'Trecho inválido: selecione paradas em ordem.')
    vehicle = get(db, 'vehicles', trip['vehicle_id'])
    rows = db.execute('SELECT o.segment_start,o.segment_end,r.companion FROM occurrences o JOIN requests r ON r.id=o.request_id WHERE o.trip_id=?', (trip['id'],)).fetchall()
    for segment in range(start, end):
        used = sum(1+r['companion'] for r in rows if r['segment_start'] <= segment < r['segment_end'])
        require(used+1+request['companion'] <= vehicle['capacity'], f'Capacidade excedida no trecho {segment+1}, incluindo acompanhante.')


PERMISSIONS = {
    'route.save': {'admin', 'transporte'},
    'production.save': {'admin', 'faturamento'},
    'production.submit': {'admin', 'faturamento'},
    'service.create': {'admin', 'regulacao', 'transporte', 'financeiro', 'faturamento', 'auditor'},
    'service.close': {'admin'},
    'pilot.create': {'admin', 'auditor'},
}


def execute_extension(db, user, action, data):
    require(user['role'] in PERMISSIONS.get(action, set()), 'Seu perfil não tem permissão para esta ação.')
    identifier = data.get('id')
    before = None
    if action == 'route.save':
        trip = get(db, 'trips', data.get('trip_id'))
        require(trip['status'] == 'Planejada', 'Viagem encerrada.')
        require(not db.execute('SELECT 1 FROM occurrences WHERE trip_id=?', (trip['id'],)).fetchone(), 'Retire as alocações antes de alterar as paradas.')
        names = [s.strip() for s in required(data, 'stops', 3000).splitlines() if s.strip()]
        require(2 <= len(names) <= 30 and all(len(n) <= 100 for n in names), 'Informe de 2 a 30 paradas, até 100 caracteres cada.')
        reason = required(data, 'reason', 1000)
        before = stops(db, trip['id'])
        db.execute('DELETE FROM route_stops WHERE trip_id=?', (trip['id'],))
        for position, name in enumerate(names):
            insert(db, 'route_stops', dict(trip_id=trip['id'], position=position, name=name))
        update(db, 'trips', trip['id'], dict(route=' → '.join(names)))
        log(db,user,action,'trips',trip['id'],before,stops(db,trip['id']),reason)
        return dict(message='Paradas e trechos salvos.', id=trip['id'])
    if action.startswith('production.'):
        table = 'production'
        if action == 'production.save':
            occurrence = get(db, 'occurrences', data.get('occurrence_id'))
            require(occurrence['attendance'] and occurrence['boarding'] == 'Embarcou', 'Concilie atendimento e deslocamento antes de preparar produção.')
            code = required(data, 'procedure_code', 10)
            require(re.fullmatch(r'\d{10}', code), 'Código de procedimento deve ter 10 dígitos; validar no catálogo oficial aplicável.')
            existing = db.execute('SELECT * FROM production WHERE occurrence_id=?', (occurrence['id'],)).fetchone()
            before = dict(existing) if existing else None
            require(not before or before['status'] == 'Preparada', 'Produção encaminhada não pode ser sobrescrita.')
            identifier = before['id'] if before else None
            quantity = number(data, 'quantity', 1, 999)
            require(quantity.is_integer(), 'Quantidade deve ser inteira.')
            values = dict(occurrence_id=occurrence['id'], procedure_code=code, quantity=int(quantity), destination=required(data,'destination'), note=required(data,'note',1000), updated_at=now())
        else:
            before = get(db, table, identifier)
            require(before['status'] == 'Preparada', 'Produção já encaminhada.')
            values = dict(status='Encaminhada para revisão', protocol=required(data,'protocol'), updated_at=now())
    elif action.startswith('service.'):
        table = 'service_records'
        if action == 'service.create':
            require(data.get('kind') in ('Suporte','Capacitação'), 'Tipo inválido.')
            values = dict(kind=data['kind'], title=required(data,'title'), owner=required(data,'owner'), status='Aberto', notes=required(data,'notes',2000), created_at=now())
        else:
            before = get(db, table, identifier)
            require(before['status'] == 'Aberto', 'Registro já concluído.')
            values = dict(status='Concluído', notes=before['notes']+'\nConclusão: '+required(data,'notes',2000))
    else:
        table = 'pilot_measurements'
        start, end = day(data.get('start_date')), day(data.get('end_date'))
        require(start <= end, 'Período inválido.')
        require(data.get('scenario') in ('Simulação acadêmica','Rotina municipal'), 'Identifique a origem da medição.')
        values = dict(indicator=required(data,'indicator'), unit=required(data,'unit'), baseline=number(data,'baseline'), measured=number(data,'measured'), start_date=start.isoformat(), end_date=end.isoformat(), source=required(data,'source',1500), responsible=required(data,'responsible'), scenario=data['scenario'], created_at=now())
    if before:
        update(db,table,identifier,values)
    else:
        identifier = insert(db,table,values)
    log(db,user,action,table,identifier,before,values)
    return dict(id=identifier,message='Registro salvo com rastreabilidade.')


def extend_state(db, user, result):
    trip_ids = {t['id'] for t in result['trips']}
    result['route_stops'] = [dict(r) for r in db.execute('SELECT * FROM route_stops ORDER BY trip_id,position') if r['trip_id'] in trip_ids]
    for table, roles in [('production',('admin','faturamento','auditor')), ('service_records',('admin','regulacao','transporte','financeiro','faturamento','auditor')), ('pilot_measurements',('admin','auditor'))]:
        result[table] = [dict(r) for r in db.execute(f'SELECT * FROM {table} ORDER BY id DESC')] if user['role'] in roles else []
    return result
