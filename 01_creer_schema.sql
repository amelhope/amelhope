-- Schéma synthétique compatible avec la structure réelle LANALA
-- (global_def.entity, account, productservice, entityfield, patrimonials)
-- Isolé dans son propre schéma "lanala_synthetic" pour ne jamais toucher aux vraies données.

CREATE SCHEMA IF NOT EXISTS lanala_synthetic;

CREATE TABLE lanala_synthetic.entity (
    pk_          SERIAL PRIMARY KEY,
    firstname_   VARCHAR(255),
    lastname_    VARCHAR(255),
    fullname_    VARCHAR(255),
    birthday_    TIMESTAMP,
    civilstatus_ VARCHAR(9),
    type_        VARCHAR(255)
);

CREATE TABLE lanala_synthetic.productservice (
    code_ VARCHAR(50) PRIMARY KEY,
    type_ VARCHAR(255)
);

CREATE TABLE lanala_synthetic.account (
    pk_          SERIAL PRIMARY KEY,
    ownerpk_     INTEGER REFERENCES lanala_synthetic.entity(pk_),
    productcode_ VARCHAR(50) REFERENCES lanala_synthetic.productservice(code_)
);

CREATE TABLE lanala_synthetic.entityfield (
    pk_        SERIAL PRIMARY KEY,
    entitypk_  INTEGER REFERENCES lanala_synthetic.entity(pk_),
    name_      VARCHAR(255),
    itemvalue_ VARCHAR(255)
);

CREATE TABLE lanala_synthetic.patrimonials (
    pk_                SERIAL PRIMARY KEY,
    entitypk_          INTEGER REFERENCES lanala_synthetic.entity(pk_),
    revenumensuelnet_  NUMERIC(12, 2)
);