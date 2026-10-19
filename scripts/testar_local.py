import csv, sqlite3, json, hashlib, ast
from pathlib import Path
R=Path(__file__).resolve().parents[1]
m=json.loads((R/'data/origem_manifest.json').read_text())
assert hashlib.sha256((R/'data/academia.db').read_bytes()).hexdigest()==m['sha256']
with sqlite3.connect(R/'data/academia.db') as c:
    assert not c.execute('PRAGMA foreign_key_check').fetchall()
    for t,n in m['tables'].items():
        assert c.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]==n
        with (R/f'data/{t}.csv').open(encoding='utf-8') as f: assert sum(1 for _ in csv.DictReader(f))==n
for p in (R/'notebooks').glob('*.py'): ast.parse(p.read_text(encoding='utf-8'))
print('PASSOU: origem, integridade referencial, contagens, hash e sintaxe dos notebooks. Spark/Databricks ainda requer execução remota.')
