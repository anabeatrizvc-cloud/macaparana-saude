"""Inspeção estrutural dos PDFs e prévias locais para revisão visual."""
import json
from pathlib import Path
import pymupdf

ROOT=Path(__file__).resolve().parents[1]
PREVIEW=ROOT/'data'/'pdf-preview'
PREVIEW.mkdir(parents=True,exist_ok=True)
reports=[]
for path in (ROOT/'docs').glob('*.pdf'):
    with pymupdf.open(path) as document:
        empty=[]
        for i,page in enumerate(document):
            if len(page.get_text().strip())<40 and not page.get_images():
                empty.append(i+1)
        for index in sorted({0,min(2,len(document)-1),len(document)-1}):
            document[index].get_pixmap(matrix=pymupdf.Matrix(1.2,1.2)).save(PREVIEW/f'{path.stem}-{index+1}.png')
        reports.append({'arquivo':path.name,'paginas':len(document),'bytes':path.stat().st_size,'paginas_vazias':empty})
print(json.dumps(reports,ensure_ascii=False,indent=2))
assert all(not r['paginas_vazias'] for r in reports)
