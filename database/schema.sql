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
    development_proposal TEXT,
    development_clarifiacation TEXT,
    release_date DATE,
    functional_area TEXT,
    ball_park_estimate VARCHAR(10),
    impact_on_market INT,
    product_improvement TEXT,
    priority VARCHAR(10) NOT NULL CHECK(priority IN ('low', 'medium', 'high')) DEFAULT 'low',
    comment TEXT,
    next_steps TEXT
);