DROP TABLE IF EXISTS user;

CREATE TABLE user
(
    discord_id VARCHAR(32) PRIMARY KEY,
    rating     FLOAT     NOT NULL DEFAULT 1500,
    created_at TIMESTAMP NOT NULL DEFAULT current_timestamp,
    updated_at TIMESTAMP NOT NULL DEFAULT current_timestamp ON UPDATE current_timestamp
);

DROP TABLE IF EXISTS game;

CREATE TABLE game
(
    game_id    BIGINT PRIMARY KEY AUTO_INCREMENT,
    winner     TINYINT,
    created_at TIMESTAMP NOT NULL DEFAULT current_timestamp
);

DROP TABLE IF EXISTS player;

CREATE TABLE player
(
    game_id    BIGINT,
    discord_id VARCHAR(32),
    team       TINYINT,
    PRIMARY KEY (game_id, discord_id)
);
