-- Execute no banco academia_lakehouse já criado no portal Azure.
-- Não cria recursos pagos, não apaga dados. O script Python também cria estas tabelas.
-- Campos de negócio textuais preservam inconsistências para a demonstração de qualidade.

IF OBJECT_ID(N'dbo.planos',N'U') IS NULL
CREATE TABLE dbo.[planos] (
    [id_plano] INT NOT NULL PRIMARY KEY,
    [nome] NVARCHAR(500) NULL,
    [valor_mensal] NVARCHAR(500) NULL,
    [duracao_meses] NVARCHAR(500) NULL
);

IF OBJECT_ID(N'dbo.unidades',N'U') IS NULL
CREATE TABLE dbo.[unidades] (
    [id_unidade] INT NOT NULL PRIMARY KEY,
    [nome] NVARCHAR(500) NULL,
    [cidade] NVARCHAR(500) NULL,
    [bairro] NVARCHAR(500) NULL,
    [data_inauguracao] NVARCHAR(500) NULL
);

IF OBJECT_ID(N'dbo.alunos',N'U') IS NULL
CREATE TABLE dbo.[alunos] (
    [id_aluno] INT NOT NULL PRIMARY KEY,
    [nome] NVARCHAR(500) NULL,
    [email] NVARCHAR(500) NULL,
    [cidade] NVARCHAR(500) NULL,
    [id_plano] NVARCHAR(500) NULL,
    [data_matricula] NVARCHAR(500) NULL,
    [ativo] NVARCHAR(500) NULL
);

IF OBJECT_ID(N'dbo.checkins',N'U') IS NULL
CREATE TABLE dbo.[checkins] (
    [id_checkin] INT NOT NULL PRIMARY KEY,
    [id_aluno] NVARCHAR(500) NULL,
    [id_unidade] NVARCHAR(500) NULL,
    [data_hora] NVARCHAR(500) NULL
);

IF OBJECT_ID(N'dbo.pagamentos',N'U') IS NULL
CREATE TABLE dbo.[pagamentos] (
    [id_pagamento] INT NOT NULL PRIMARY KEY,
    [id_aluno] NVARCHAR(500) NULL,
    [competencia] NVARCHAR(500) NULL,
    [data_pagamento] NVARCHAR(500) NULL,
    [valor] NVARCHAR(500) NULL,
    [forma_pagamento] NVARCHAR(500) NULL,
    [status] NVARCHAR(500) NULL
);
