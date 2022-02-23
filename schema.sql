DROP TABLE IF EXISTS User;

CREATE TABLE User (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    phone_number INTEGER NOT NULL,
    longtitude INTEGER NOT NULL,
    latitude INTEGER NOT NULL,
);