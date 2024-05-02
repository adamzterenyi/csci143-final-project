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

create table messages (
    id BIGSERIAL primary key,
    sender_id integer not null REFERENCES users(id),
    message text not null,
    created_at timestamp not null default current_timestamp,
    id_urls INTEGER REFERENCES urls(id_urls)
);
