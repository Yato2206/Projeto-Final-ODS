-- Apagar schema antigo se existir
DROP SCHEMA IF EXISTS dbo CASCADE;

-- Criar schema dbo
CREATE SCHEMA dbo;

-- Tabela de ODS
CREATE TABLE dbo.ods
(
    id                  SERIAL PRIMARY KEY,
    name                VARCHAR(255)        NOT NULL
);

-- Tabela de Dados
CREATE TABLE dbo.data
(
    id                  SERIAL PRIMARY KEY,
    ods_id              INT[]               DEFAULT NULL,
    type                VARCHAR(255)        NOT NULL DEFAULT 'UNDEFINED' check (type IN ('UNDEFINED', 'ACAO_NA_SOCIEDAD', 'ARTISTICO', 'CIENTIFICO', 'ENSINO')),
    origin              VARCHAR(512)        NOT NULL,
    date_checked        TIMESTAMP           NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tabela da Família de Palavras (Weak Entity of ODS)
CREATE TABLE dbo.terms
(
    id                  SERIAL,
    ods_id              INT                 NOT NULL REFERENCES dbo.ods (id) ON DELETE CASCADE,
    name                VARCHAR(255)        NOT NULL,
    origin              VARCHAR(512)        NOT NULL,
    PRIMARY KEY (ods_id, id)
);

-- Join table: dados_ods
CREATE TABLE dbo.data_ods
(
    data_id INT NOT NULL REFERENCES dbo.data (id) ON DELETE CASCADE,
    ods_id  INT NOT NULL REFERENCES dbo.ods (id) ON DELETE CASCADE,
    PRIMARY KEY (data_id, ods_id)
);
