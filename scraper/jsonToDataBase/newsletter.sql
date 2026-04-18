CREATE TABLE newsletter (
    title           VARCHAR(255) PRIMARY KEY ,
    date            DATE NOT NULL,
    link            VARCHAR(255) NOT NULL,
    date_checked    TIMESTAMP NOT NULL
);