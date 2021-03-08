CREATE TABLE IF NOT EXISTS Users (
    id              BIGINT NOT NULL PRIMARY KEY,
    permissions     INT NOT NULL DEFAULT 0,
    banned          BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS Guilds (
    id              BIGINT NOT NULL PRIMARY KEY,
    config          TEXT NOT NULL DEFAULT '{}',
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS Messages (
    id              BIGINT NOT NULL PRIMARY KEY,
    bcid            BIGINT NOT NULL,
    guild_id        BIGINT NOT NULL,
    channel_id      BIGINT NOT NULL,
    author_id       BIGINT NOT NULL,
    content         TEXT NOT NULL,
    deleted         BOOLEAN NOT NULL DEFAULT FALSE
);