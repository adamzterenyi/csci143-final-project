SET max_parallel_maintenance_workers TO 80;
SET max_parallel_workers TO 80;
SET maintenance_work_mem TO '16 GB';

CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    age INTEGER
);

CREATE TABLE urls (
    id_urls BIGSERIAL PRIMARY KEY,
    url TEXT UNIQUE
);

CREATE TABLE messages (
    id BIGSERIAL PRIMARY KEY,
    sender_id integer NOT NULL REFERENCES users(id),
    message text NOT NULL,
    id_urls INTEGER REFERENCES urls(id_urls),
    created_at timestamp NOT NULL default current_timestamp
);

CREATE EXTENSION IF NOT EXISTS RUM;

--CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX get_messages ON messages(created_at, id, sender_id, message);
CREATE INDEX query_messages ON messages USING RUM(to_tsvector('english', message));
