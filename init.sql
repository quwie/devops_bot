CREATE DATABASE DB_DATABASE;

CREATE USER DB_REPL_USER WITH REPLICATION ENCRYPTED PASSWORD 'DB_REPL_PASSWORD';
SELECT pg_create_physical_replication_slot('replication_slot');

\connect DB_DATABASE;

CREATE TABLE IF NOT EXISTS emails(
        ID SERIAL PRIMARY KEY,
	Email VARCHAR (255) NOT NULL
);

CREATE TABLE IF NOT EXISTS phones(
        ID SERIAL PRIMARY KEY,
	Phone VARCHAR (50) NOT NULL
);

INSERT INTO emails (email) VALUES ('qwerlock65@gmail.com'), ('hello@ptstart.ru'), ('privet@vsem.ru');

INSERT INTO phones (phone) VALUES ('88005553535'), ('8-800-555-35-35'), ('8(800)5553535');

