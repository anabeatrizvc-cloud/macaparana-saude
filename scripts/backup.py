"""Backup consistente do SQLite local. Não inclui dados no Git ou pacote."""
import argparse
import sqlite3
from contextlib import closing
from pathlib import Path
from datetime import datetime

def backup(source, target):
    source=Path(source).resolve()
    target=Path(target).resolve()
    if not source.is_file() or source==target or target.exists():
        raise ValueError('Origem deve existir e destino deve ser novo e diferente.')
    target.parent.mkdir(parents=True,exist_ok=True)
    with closing(sqlite3.connect(source.as_uri()+'?mode=ro',uri=True)) as original:
        with closing(sqlite3.connect(target)) as copy:
            original.backup(copy)
            assert copy.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    return target

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--source',type=Path,default=Path('data/macaparana.db'))
    parser.add_argument('--target',type=Path,default=Path('data/backups')/f'macaparana-{datetime.now():%Y%m%d-%H%M%S}.db')
    args=parser.parse_args()
    print(backup(args.source,args.target))
