CREATE TABLE IF NOT EXISTS users (
    user_id      TEXT PRIMARY KEY,
    username     TEXT UNIQUE NOT NULL,
    email        TEXT,
    display_name TEXT,
    password_hash TEXT NOT NULL,
    created_at   TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS follows (
    follower_id TEXT NOT NULL,
    followee_id TEXT NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (follower_id, followee_id)
);

CREATE TABLE IF NOT EXISTS posts (
    post_id    TEXT PRIMARY KEY,
    author_id  TEXT NOT NULL,
    text       TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS notifications (
    notification_id TEXT PRIMARY KEY,
    recipient_id    TEXT NOT NULL,
    post_id         TEXT,
    author_id       TEXT,
    type            TEXT NOT NULL,
    entity_type     TEXT,
    entity_id       TEXT,
    read            BOOLEAN DEFAULT false,
    created_at      TIMESTAMPTZ DEFAULT now(),
    UNIQUE (recipient_id, type, entity_type, entity_id)
);

CREATE TABLE IF NOT EXISTS messages (
    message_id   TEXT PRIMARY KEY,
    sender_id    TEXT NOT NULL,
    recipient_id TEXT NOT NULL,
    text         TEXT NOT NULL,
    created_at   TIMESTAMPTZ DEFAULT now()
);
