SELECT 'planos' tabela,COUNT(*) linhas FROM dbo.planos
UNION ALL SELECT 'unidades',COUNT(*) FROM dbo.unidades
UNION ALL SELECT 'alunos',COUNT(*) FROM dbo.alunos
UNION ALL SELECT 'checkins',COUNT(*) FROM dbo.checkins
UNION ALL SELECT 'pagamentos',COUNT(*) FROM dbo.pagamentos;

SELECT * FROM dbo.alunos WHERE id_aluno>=301;
