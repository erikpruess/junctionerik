DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    password TEXT NOT NULL,
    email TEXT NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user'
);

DROP TABLE IF EXISTS tickets;

CREATE TABLE tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title VARCHAR(255) NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('open', 'in_progress', 'closed')) DEFAULT 'open',
    priority VARCHAR(10) NOT NULL CHECK(priority IN ('low', 'medium', 'high')) DEFAULT 'low',
    description TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
);