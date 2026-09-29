"""Executa a suíte sem dependências e salva a evidência em UTF-8."""
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.stdout.reconfigure(encoding='utf-8')
result=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace')
report=f'Macaparana Saúde — testes automatizados\nExecução: {datetime.now().isoformat(timespec="seconds")}\nPython: {sys.version.split()[0]}\nComando: python -m unittest discover -s tests -v\n\n{result.stdout}{result.stderr}\nCódigo de saída: {result.returncode}\n'
(ROOT/'docs'/'resultado-testes.txt').write_text(report,encoding='utf-8')
print(report)
sys.exit(result.returncode)
