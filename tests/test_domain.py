import base64
import sqlite3
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from app.domain import connect, execute, get, insert, state, RuleError
from app.seed import initialize


class MunicipalFlowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = connect(Path(self.temp.name)/'test.db')
        initialize(self.db)
        self.admin = get(self.db,'users',1)
        self.today = date.today().isoformat()

    def tearDown(self):
        self.db.close()
        self.temp.cleanup()

    def act(self,action,**data):
        with self.db:
            return execute(self.db,self.admin,action,data)

    def document(self,kind,**link):
        return self.act('document.create',kind=kind,name='comprovante.txt',content=base64.b64encode(b'DOCUMENTO FICTICIO').decode(),**link)

    def new_request(self,kind='TFD',companion=False):
        return self.act('request.create',patient_id=4,facility_id=1,kind=kind,specialty='Teste',companion=companion,start_date=self.today,end_date=(date.today()+timedelta(days=60)).isoformat())['id']

    def authorize(self,rid):
        self.document('Laudo',request_id=rid)
        self.act('request.decide',id=rid,status='Autorizada',reason='Análise demonstrativa completa')

    def test_authorization_requires_report(self):
        rid=self.new_request()
        with self.assertRaisesRegex(RuleError,'laudo'):
            self.act('request.decide',id=rid,status='Autorizada',reason='Teste')
        self.assertEqual(get(self.db,'requests',rid)['status'],'Em análise')
        self.authorize(rid)
        self.assertEqual(get(self.db,'requests',rid)['status'],'Autorizada')

    def test_recurrence_crosses_months_without_duplicates(self):
        rid=self.new_request()
        self.authorize(rid)
        end=(date.today()+timedelta(days=50)).isoformat()
        for _ in range(2):
            self.act('schedule.create',request_id=rid,start_date=self.today,end_date=end,weekdays=[0,2])
        rows=self.db.execute('SELECT date FROM occurrences WHERE request_id=?',(rid,)).fetchall()
        self.assertEqual(len(rows),len({r['date'] for r in rows}))
        self.assertGreater(len({r['date'][:7] for r in rows}),1)

    def test_recurrence_outside_authorization_is_blocked(self):
        rid=self.new_request()
        self.authorize(rid)
        with self.assertRaisesRegex(RuleError,'validade'):
            self.act('schedule.create',request_id=rid,start_date=self.today,end_date=(date.today()+timedelta(days=90)).isoformat(),weekdays=[0])

    def test_conflicting_driver_or_vehicle_is_blocked(self):
        with self.assertRaisesRegex(RuleError,'alocado'):
            self.act('trip.create',date=self.today,departure='06:00',arrival='10:00',destination='Teste',route='Teste',vehicle_id=1,driver_id=3,estimated_km=1)

    def test_expired_license_is_blocked(self):
        did=self.act('driver.create',name='CNH vencida',license='TESTE',valid_until='2000-01-01')['id']
        with self.assertRaisesRegex(RuleError,'CNH'):
            self.act('trip.create',date=self.today,departure='18:00',arrival='20:00',destination='Teste',route='Teste',vehicle_id=3,driver_id=did)

    def test_companion_counts_toward_capacity(self):
        vid=self.act('vehicle.create',name='Um lugar',plate='TEST-001',capacity=1)['id']
        tid=self.act('trip.create',date=self.today,departure='18:00',arrival='20:00',destination='Recife',route='Teste',vehicle_id=vid,driver_id=3)['id']
        with self.assertRaisesRegex(RuleError,'Capacidade'):
            self.act('trip.allocate',trip_id=tid,occurrence_id=4)

    def test_accessibility_is_required(self):
        self.act('trip.release',trip_id=1,occurrence_id=3,reason='Realocação para teste')
        with self.assertRaisesRegex(RuleError,'acessível'):
            self.act('trip.allocate',trip_id=2,occurrence_id=3)

    def test_boarding_does_not_prove_attendance(self):
        self.act('occurrence.board',id=1,status='Embarcou')
        self.assertFalse(get(self.db,'occurrences',1)['attendance'])
        with self.assertRaisesRegex(RuleError,'declaração'):
            self.act('occurrence.prove',id=1,permanence='Mesmo dia')

    def test_unconfirmed_passenger_cannot_board(self):
        with self.assertRaisesRegex(RuleError,'Confirme'):
            self.act('occurrence.board',id=3,status='Embarcou')

    def test_companion_proof_is_separate(self):
        self.act('occurrence.board',id=1,status='Embarcou')
        self.document('Declaração do paciente',occurrence_id=1)
        with self.assertRaisesRegex(RuleError,'separada'):
            self.act('occurrence.prove',id=1,permanence='Mesmo dia',companion_proof=True)
        self.act('occurrence.prove',id=1,permanence='Mesmo dia',companion_proof=False)
        self.act('benefit.calculate',month=self.today[:7])
        rows=self.db.execute('SELECT beneficiary FROM benefits WHERE occurrence_id=1').fetchall()
        self.assertEqual([r[0] for r in rows],['Paciente'])
        self.document('Declaração do acompanhante',occurrence_id=1)
        self.act('occurrence.prove',id=1,permanence='Mesmo dia',companion_proof=True)
        self.act('benefit.calculate',month=self.today[:7])
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM benefits WHERE occurrence_id=1').fetchone()[0],2)

    def test_transport_without_tfd_never_generates_benefit(self):
        self.act('occurrence.board',id=5,status='Embarcou')
        self.document('Declaração do paciente',occurrence_id=5)
        self.act('occurrence.prove',id=5,permanence='Mesmo dia')
        self.act('benefit.calculate',month=self.today[:7])
        self.assertFalse(self.db.execute('SELECT 1 FROM benefits WHERE occurrence_id=5').fetchone())

    def test_calculation_is_idempotent_and_preserves_rate(self):
        self.act('benefit.calculate',month=self.today[:7])
        before=[tuple(r) for r in self.db.execute('SELECT id,amount_cents,rule_id FROM benefits')]
        self.act('rule.create',patient_rate=999,companion_rate=999,label='Nova regra ilustrativa')
        self.act('benefit.calculate',month=self.today[:7])
        after=[tuple(r) for r in self.db.execute('SELECT id,amount_cents,rule_id FROM benefits')]
        self.assertEqual(before,after)

    def test_payment_requires_accounting_reference_and_valid_date(self):
        self.act('benefit.advance',id=3)
        with self.assertRaisesRegex(RuleError,'accounting_ref'):
            self.act('benefit.advance',id=3)
        self.act('benefit.advance',id=3,accounting_ref='DEMO-1')
        with self.assertRaisesRegex(RuleError,'Pagamento'):
            self.act('benefit.advance',id=3,accounting_ref='DEMO-1',payment_date='2000-01-01')
        self.act('benefit.advance',id=3,accounting_ref='DEMO-1',payment_date=self.today)
        self.assertEqual(get(self.db,'benefits',3)['status'],'Pago')

    def test_driver_only_sees_operational_data_and_assigned_trips(self):
        driver=dict(self.db.execute("SELECT * FROM users WHERE role='motorista'").fetchone())
        data=state(self.db,driver)
        self.assertTrue(all(t['driver_id']==driver['driver_id'] for t in data['trips']))
        for patient in data['patients']:
            self.assertFalse({'bank','cpf','cns','birth'} & patient.keys())
        for request in data['requests']:
            self.assertNotIn('specialty',request)
        self.assertEqual(data['documents'],[])
        with self.assertRaisesRegex(RuleError,'permissão'):
            execute(self.db,driver,'benefit.calculate',{'month':self.today[:7]})
        with self.assertRaisesRegex(RuleError,'outro motorista'):
            execute(self.db,driver,'occurrence.confirm',{'id':5,'status':'Confirmado'})

    def test_audit_stores_before_after_actor_and_reason(self):
        self.act('request.decide',id=7,status='Pendente',reason='Documento precisa de correção')
        row=dict(self.db.execute('SELECT * FROM audit ORDER BY id DESC LIMIT 1').fetchone())
        self.assertIn('Em análise',row['before_json'])
        self.assertIn('Pendente',row['after_json'])
        self.assertEqual(row['user_id'],1)
        self.assertEqual(row['reason'],'Documento precisa de correção')

    def test_full_new_patient_to_payment_flow(self):
        pid=self.act('patient.create',name='Paciente teste completo',address='Rua fictícia',boarding='Praça')['id']
        rid=self.act('request.create',patient_id=pid,facility_id=1,kind='TFD',specialty='Teste',start_date=self.today,end_date=self.today)['id']
        self.authorize(rid)
        self.act('schedule.create',request_id=rid,start_date=self.today,end_date=self.today,weekdays=[])
        oid=self.db.execute('SELECT id FROM occurrences WHERE request_id=?',(rid,)).fetchone()[0]
        tid=self.act('trip.create',date=self.today,departure='18:00',arrival='20:00',destination='Recife',route='Macaparana - Recife - Macaparana',vehicle_id=1,driver_id=1,estimated_km=220)['id']
        self.act('trip.allocate',trip_id=tid,occurrence_id=oid)
        self.act('occurrence.confirm',id=oid,status='Confirmado')
        self.act('occurrence.board',id=oid,status='Embarcou')
        self.act('trip.close',id=tid,km=220,liters=20,cost=150)
        self.document('Declaração do paciente',occurrence_id=oid)
        self.act('occurrence.prove',id=oid,permanence='Mesmo dia')
        self.act('benefit.calculate',month=self.today[:7])
        bid=self.db.execute('SELECT id FROM benefits WHERE occurrence_id=?',(oid,)).fetchone()[0]
        for _ in range(3):
            self.act('benefit.advance',id=bid,accounting_ref='TESTE-1',payment_date=self.today)
        self.assertEqual(get(self.db,'benefits',bid)['status'],'Pago')
        self.assertEqual(get(self.db,'trips',tid)['status'],'Encerrada')


if __name__=='__main__':
    unittest.main(verbosity=2)
