"""Baixa Node.js LTS portátil oficial para desenvolvimento local no Windows."""
import hashlib
import json
import urllib.request
import zipfile
from pathlib import Path

root=Path(__file__).resolve().parents[1]/'.tools'
root.mkdir(exist_ok=True)
with urllib.request.urlopen('https://nodejs.org/dist/index.json') as response:
    release=next(item for item in json.load(response) if item['lts'] and 'win-x64-zip' in item['files'])
version=release['version']
name=f'node-{version}-win-x64.zip'
url=f'https://nodejs.org/dist/{version}/'
with urllib.request.urlopen(url+'SHASUMS256.txt') as response:
    checksum=next(line.split()[0] for line in response.read().decode().splitlines() if line.endswith('  '+name))
target=root/name
urllib.request.urlretrieve(url+name,target)
assert hashlib.sha256(target.read_bytes()).hexdigest()==checksum,'Checksum inválido'
with zipfile.ZipFile(target) as archive:
    archive.extractall(root)
print(root/name.removesuffix('.zip'))
