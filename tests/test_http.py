import http.cookiejar
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from contextlib import closing
from pathlib import Path
from http.server import ThreadingHTTPServer

import server
from app.domain import connect
from app.seed import initialize


class HttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory()
        cls.previous=server.DB_PATH
        server.DB_PATH=Path(cls.temp.name)/'http.db'
        with closing(connect(server.DB_PATH)) as db:
            initialize(db)
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()
        cls.base=f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
        server.DB_PATH=cls.previous
        import gc
        gc.collect()
        cls.temp.cleanup()

    def setUp(self):
        self.client=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

    def request(self,path,body=None,headers=None):
        req=urllib.request.Request(self.base+path,data=json.dumps(body).encode() if body is not None else None,headers=headers or {'X-App':'macaparana','Content-Type':'application/json'})
        try:
            with self.client.open(req) as response:
                return response.status,response.read(),response.headers
        except urllib.error.HTTPError as error:
            with error:
                return error.code,error.read(),error.headers

    def login(self,role='admin'):
        return self.request('/api/login',{'username':role,'password':'demo123'})

    def test_session_cookie_and_logout(self):
        self.assertEqual(self.request('/api/state')[0],401)
        status,body,headers=self.login()
        self.assertEqual(status,200)
        self.assertIn('HttpOnly',headers['Set-Cookie'])
        self.assertIn('SameSite=Strict',headers['Set-Cookie'])
        self.assertEqual(self.request('/api/state')[0],200)
        self.assertEqual(self.request('/api/logout',{})[0],200)
        self.assertEqual(self.request('/api/state')[0],401)

    def test_cross_origin_and_missing_header_are_rejected(self):
        payload={'username':'admin','password':'demo123'}
        self.assertEqual(self.request('/api/login',payload,{'Content-Type':'application/json'})[0],403)
        self.assertEqual(self.request('/api/login',payload,{'Content-Type':'application/json','X-App':'macaparana','Origin':'https://external.invalid'})[0],403)

    def test_driver_cannot_download_documents_or_export(self):
        self.login('motorista')
        self.assertEqual(self.request('/api/documents/1')[0],400)
        self.assertEqual(self.request('/api/export')[0],400)
        data=json.loads(self.request('/api/state')[1])
        self.assertEqual(data['documents'],[])
        self.assertNotIn('bank',data['patients'][0])

    def test_production_export_and_role_restriction(self):
        from datetime import date, timedelta
        self.login('faturamento')
        status,body,_=self.request('/api/action',{'action':'production.save','data':{'occurrence_id':7,'procedure_code':'0000000001','quantity':1,'destination':'Revisão','note':'Dado fictício'}})
        self.assertEqual(status,200,body)
        month=(date.today()-timedelta(days=1)).isoformat()[:7]
        status,body,headers=self.request('/api/production/export?month='+month)
        self.assertEqual(status,200)
        self.assertIn('0000000001',body.decode('utf-8-sig'))
        self.assertIn('attachment',headers['Content-Disposition'])
        self.request('/api/logout',{})
        self.login('motorista')
        self.assertEqual(self.request('/api/production/export?month='+month)[0],400)

    def test_document_and_export_download(self):
        self.login()
        status,body,headers=self.request('/api/documents/1')
        self.assertEqual(status,200)
        self.assertIn(b'FICT',body)
        self.assertIn('attachment',headers['Content-Disposition'])
        status,body,headers=self.request('/api/export')
        self.assertEqual(status,200)
        self.assertTrue(body.startswith(b'\xef\xbb\xbf'))
        self.assertIn(b'Benefici',body)

    def test_data_and_source_files_are_not_served(self):
        for path in ['/data/macaparana.db','/server.py','/app/domain.py','/../server.py']:
            self.assertEqual(self.request(path)[0],404,path)


if __name__=='__main__':
    unittest.main(verbosity=2)
