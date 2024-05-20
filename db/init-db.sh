#!/bin/bash

psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE TABLE emails(
        ID SERIAL PRIMARY KEY,
        Email VARCHAR (255) NOT NULL
    );

    CREATE TABLE phones(
        ID SERIAL PRIMARY KEY,
        Phone VARCHAR (50) NOT NULL
    );

    INSERT INTO emails (email) VALUES ('qwerlock65@gmail.com'), ('hello@ptstart.ru'), ('privet@vsem.ru');

    INSERT INTO phones (phone) VALUES ('88005553535'), ('8-800-555-35-35'), ('8(800)5553535');

    CREATE USER ${DB_REPL_USER} WITH REPLICATION ENCRYPTED PASSWORD '${DB_REPL_PASSWORD}';
    SELECT pg_create_physical_replication_slot('replication_slot');
EOSQL

echo "host replication ${DB_REPL_USER} ${DB_REPL_HOST}/24 scram-sha-256" >> /var/lib/postgresql/data/pg_hba.conf