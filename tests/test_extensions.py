import tempfile
import unittest
from pathlib import Path
from datetime import date
from app.domain import connect, execute, get, insert, state, RuleError
from app.seed import initialize


class ExtensionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.db=connect(Path(self.temp.name)/'test.db')
        initialize(self.db)
        self.admin=get(self.db,'users',1)

    def tearDown(self):
        self.db.close()
        self.temp.cleanup()

    def act(self, action, **data):
        with self.db:
            return execute(self.db,self.admin,action,data)

    def test_segment_capacity_reuses_seat_but_rejects_overlap(self):
        vehicle=self.act('vehicle.create',name='Teste',plate='SEG-001',capacity=1)['id']
        trip=self.act('trip.create',date=date.today().isoformat(),departure='18:00',arrival='22:00',destination='Teste',route='Teste',vehicle_id=vehicle,driver_id=3)['id']
        self.act('route.save',trip_id=trip,stops='Macaparana\nCarpina\nRecife',reason='Planejamento')
        for oid in (2,5,6):
            o=get(self.db,'occurrences',oid)
            self.act('trip.release',trip_id=o['trip_id'],occurrence_id=oid,reason='Teste de trecho')
        self.act('trip.allocate',trip_id=trip,occurrence_id=2,segment_start=0,segment_end=1)
        self.act('trip.allocate',trip_id=trip,occurrence_id=5,segment_start=1,segment_end=2)
        with self.assertRaisesRegex(RuleError,'Capacidade'):
            self.act('trip.allocate',trip_id=trip,occurrence_id=6,segment_start=0,segment_end=2)
        with self.assertRaisesRegex(RuleError,'Trecho'):
            self.act('trip.allocate',trip_id=trip,occurrence_id=6,segment_start=2,segment_end=1)
        with self.assertRaisesRegex(RuleError,'alocações'):
            self.act('route.save',trip_id=trip,stops='A\nB',reason='Alteração')
        self.assertEqual(len(state(self.db,self.admin)['route_stops']),3)

    def test_production_requires_proof_and_preserves_sent_record(self):
        data=dict(procedure_code='0000000001',quantity=1,destination='Revisão interna',note='Código fictício')
        with self.assertRaisesRegex(RuleError,'Concilie'):
            self.act('production.save',occurrence_id=1,**data)
        identifier=self.act('production.save',occurrence_id=7,**data)['id']
        self.assertEqual(self.act('production.save',occurrence_id=7,**data)['id'],identifier)
        self.act('production.submit',id=identifier,protocol='DEMO-001')
        with self.assertRaisesRegex(RuleError,'sobrescrita'):
            self.act('production.save',occurrence_id=7,**data)

    def test_permissions_and_migration_preserve_existing_data(self):
        driver=dict(self.db.execute("SELECT * FROM users WHERE role='motorista'").fetchone())
        with self.assertRaisesRegex(RuleError,'permissão'):
            execute(self.db,driver,'production.save',{})
        before=self.db.execute('SELECT COUNT(*) FROM patients').fetchone()[0]
        initialize(self.db)
        self.assertEqual(before,self.db.execute('SELECT COUNT(*) FROM patients').fetchone()[0])
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM users WHERE role='faturamento'").fetchone()[0],1)

    def test_backup_can_be_opened_and_does_not_overwrite(self):
        from scripts.backup import backup
        target=Path(self.temp.name)/'copy.db'
        backup(Path(self.temp.name)/'test.db',target)
        restored=connect(target)
        try:
            self.assertEqual(restored.execute('PRAGMA integrity_check').fetchone()[0],'ok')
            self.assertEqual(restored.execute('SELECT COUNT(*) FROM patients').fetchone()[0],8)
        finally:
            restored.close()
        with self.assertRaises(ValueError):
            backup(Path(self.temp.name)/'test.db',target)

    def test_pilot_support_and_assisted_confirmation_are_audited(self):
        self.act('occurrence.confirm',id=1,status='Confirmado',channel='Telefone',note='Responsável confirmou')
        self.assertEqual(get(self.db,'occurrences',1)['confirmation_channel'],'Telefone')
        identifier=self.act('service.create',kind='Capacitação',title='Oficina fictícia',owner='Equipe de teste',notes='Execução em laboratório')['id']
        self.act('service.close',id=identifier,notes='Fluxo concluído')
        self.assertEqual(get(self.db,'service_records',identifier)['status'],'Concluído')
        self.act('pilot.create',indicator='Tempo',unit='min',baseline=20,measured=10,start_date='2026-10-01',end_date='2026-10-02',source='Simulação de teste',responsible='Equipe teste',scenario='Simulação acadêmica')
        self.assertTrue(self.db.execute("SELECT 1 FROM audit WHERE action='pilot.create'").fetchone())
