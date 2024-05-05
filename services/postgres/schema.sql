\set ON_ERROR_STOP on

SET maintenance_work_mem = '16GB';
/*SET max_parallel_maintenance_workers TO */

BEGIN; /* create database within transaction */

CREATE TABLE users (
	id_user BIGSERIAL PRIMARY KEY,
	username TEXT NOT NULL,
	password TEXT NOT NULL
);

CREATE TABLE urls (
	id_url BIGSERIAL PRIMARY KEY,
	url TEXT NOT NULL UNIQUE
);

CREATE TABLE tweets (
	id_tweet BIGSERIAL PRIMARY KEY,
	text TEXT,
	id_user BIGINT REFERENCES users(id_user)
);

COMMIT;
