import csv, sqlite3, json, hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
out=R/'data'; out.mkdir(exist_ok=True)
db=out/'academia.db'
tables=['planos','unidades','alunos','checkins','pagamentos']
keys={'planos':'id_plano','unidades':'id_unidade','alunos':'id_aluno','checkins':'id_checkin','pagamentos':'id_pagamento'}
with sqlite3.connect(db) as c:
    c.execute('PRAGMA foreign_keys=ON')
    for t in reversed(tables): c.execute(f'DROP TABLE IF EXISTS "{t}"')
    for t in tables:
        with (out/f'{t}.csv').open(encoding='utf-8',newline='') as f:
            reader=csv.DictReader(f); cols=reader.fieldnames; rows=list(reader)
        definitions=[f'"{col}" TEXT'+(' PRIMARY KEY' if col==keys[t] else '') for col in cols]
        if t=='alunos': definitions.append('FOREIGN KEY(id_plano) REFERENCES planos(id_plano)')
        if t in ('checkins','pagamentos'): definitions.append('FOREIGN KEY(id_aluno) REFERENCES alunos(id_aluno)')
        if t=='checkins': definitions.append('FOREIGN KEY(id_unidade) REFERENCES unidades(id_unidade)')
        c.execute(f'CREATE TABLE "{t}" ('+','.join(definitions)+')')
        c.executemany(f'INSERT INTO "{t}" VALUES ('+','.join('?' for _ in cols)+')',[tuple(r[x] for x in cols) for r in rows])
    assert not c.execute('PRAGMA foreign_key_check').fetchall()
    counts={t:c.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0] for t in tables}
manifest={'tables':counts,'sha256':hashlib.sha256(db.read_bytes()).hexdigest()}
(out/'origem_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps(manifest,indent=2))
