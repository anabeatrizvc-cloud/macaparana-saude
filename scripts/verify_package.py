"""Verifica extração, integridade e inicialização do pacote de entrega."""
import hashlib
import http.cookiejar
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.stdout.reconfigure(encoding='utf-8')
with tempfile.TemporaryDirectory() as temporary:
    destination=Path(temporary)
    with zipfile.ZipFile(ROOT/'entrega'/'Macaparana-Saude-Entrega.zip') as package:
        assert package.testzip() is None
        assert all((destination/info.filename).resolve().is_relative_to(destination.resolve()) for info in package.infolist())
        package.extractall(destination)
    project=destination/'Macaparana-Saude'
    manifest=json.loads((project/'MANIFESTO-SHA256.json').read_text(encoding='utf-8'))
    for name,digest in manifest.items():
        assert hashlib.sha256((project/name).read_bytes()).hexdigest()==digest,name
    process=subprocess.Popen([sys.executable,'server.py','--port','8003'],cwd=project,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    try:
        for _ in range(60):
            try:
                with urllib.request.urlopen('http://127.0.0.1:8003',timeout=1) as response:
                    assert response.status==200
                break
            except OSError:
                time.sleep(.2)
        else:
            raise RuntimeError('O pacote não iniciou.')
        client=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        request=urllib.request.Request('http://127.0.0.1:8003/api/login',data=json.dumps({'username':'admin','password':'demo123'}).encode(),headers={'X-App':'macaparana','Content-Type':'application/json'})
        with client.open(request) as response:
            assert response.status==200
        with client.open('http://127.0.0.1:8003/api/state') as response:
            state=json.load(response)
            assert len(state['patients'])==8
        for path in ['docs/documentacao.html','docs/prototipo.html','docs/roteiro.html','docs/fluxos.html','docs/fluxos/manifesto.json','docs/mark.svg','docs/Documentacao-Macaparana.pdf','docs/Prototipo-de-Telas.pdf','docs/Roteiro-de-Apresentacao.pdf','docs/Fluxos-Funcionando.pdf']:
            with client.open('http://127.0.0.1:8003/'+path) as response:
                assert response.status==200,path
        print(json.dumps({'result':'PASS','integrity_files':len(manifest),'clean_start':True,'demo_patients':8,'documents':'HTML e PDF acessíveis'},ensure_ascii=False))
    finally:
        process.terminate()
        process.wait(timeout=10)
