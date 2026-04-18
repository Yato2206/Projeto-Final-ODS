CREATE TABLE newsletter_content (
    title                       VARCHAR(255) PRIMARY KEY ,
    politecnico_titulo          VARCHAR(255) NOT NULL,
    politecnico_texto           TEXT NOT NULL,
    noticias -- Objeto com titulo e texto
    date_checked                TIMESTAMP NOT NULL
);