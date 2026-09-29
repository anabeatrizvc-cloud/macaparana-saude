"""Pacote reproduzível sem banco, credenciais de sessão ou artefatos temporários."""
import hashlib
import json
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'entrega'
OUT.mkdir(exist_ok=True)
archive=OUT/'Macaparana-Saude-Entrega.zip'
files=[ROOT/name for name in ['README.md','iniciar.bat','server.py','.gitignore','.gitattributes']]
for directory in ['app','static','frontend','docs','exemplos','tests','scripts']:
    files.extend(path for path in (ROOT/directory).rglob('*') if path.is_file() and '__pycache__' not in path.parts and 'node_modules' not in path.parts and path.suffix!='.pyc' and path.name!='e2e-decision.png')
manifest={str(path.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(files)}
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as package:
    for path in files:
        package.write(path,Path('Macaparana-Saude')/path.relative_to(ROOT))
    package.writestr('Macaparana-Saude/MANIFESTO-SHA256.json',json.dumps(manifest,indent=2,ensure_ascii=False))
with zipfile.ZipFile(archive) as package:
    assert package.testzip() is None
digest=hashlib.sha256(archive.read_bytes()).hexdigest()
(OUT/'SHA256.txt').write_text(f'{digest}  {archive.name}\n',encoding='utf-8')
print(json.dumps({'arquivo':str(archive),'arquivos':len(files)+1,'bytes':archive.stat().st_size,'sha256':digest},ensure_ascii=False,indent=2))
