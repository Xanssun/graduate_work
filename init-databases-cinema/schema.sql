CREATE SCHEMA IF NOT EXISTS cinema;
CREATE TABLE IF NOT EXISTS cinema.rooms(
    id uuid PRIMARY KEY,
    film_id uuid NOT NULL,
    creator_id uuid NOT NULL,
    created_at timestamp NOT NULL,
    users uuid []
);
CREATE TABLE IF NOT EXISTS cinema.messages(
    id uuid PRIMARY KEY,
    user_id uuid NOT NULL,
    room_id uuid REFERENCES cinema.rooms(id),
    message TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS cinema.players(
    id uuid PRIMARY KEY,
    room_id uuid REFERENCES cinema.rooms(id),
    is_active BOOLEAN DEFAULT FALSE,
    view_progress INT
);
