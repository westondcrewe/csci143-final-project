\set ON_ERROR_STOP on

SET max_parallel_maintenance_workers TO 80;
SET max_parallel_workers TO 80;
SET maintenance_work_mem TO '16 GB';

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
	id_user BIGINT REFERENCES users(id_user),
	id_url BIGINT REFERENCES urls(id_url),
	created_at timestamp NOT NULL default current_timestamp
);

CREATE EXTENSION IF NOT EXISTS RUM;

CREATE INDEX get_tweet ON tweets(created_at, id_tweet, id_user, text);
CREATE INDEX search_tweet ON tweets USING RUM(to_tsvector('english', text));

COMMIT;
