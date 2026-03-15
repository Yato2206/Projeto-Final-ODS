-- Apagar schema antigo se existir
DROP SCHEMA IF EXISTS dbo CASCADE;

-- Criar schema dbo
CREATE SCHEMA dbo;

-- Tabela de ODS
CREATE TABLE dbo.ods
(
    id                  SERIAL PRIMARY KEY,
    name                VARCHAR(255)        NOT NULL,
    terms              VARCHAR(511)        NOT NULL,
);

-- Tabela de Dados
CREATE TABLE dbo.data
(
    id                  SERIAL PRIMARY KEY,
    type                VARCHAR(255)        NOT NULL,
    origin              VARCHAR(512)        NOT NULL,
    date_checked        TIMESTAMP           NOT NULL DEFAULT CURRENT_TIMESTAMP,
);

-- Join table: dados_ods
CREATE TABLE dbo.dados_ods
(
    data_id INT NOT NULL REFERENCES dbo.data (id) ON DELETE CASCADE,
    ods_id  INT NOT NULL REFERENCES dbo.ods (id) ON DELETE CASCADE,
    PRIMARY KEY (data_id, ods_id)
);
