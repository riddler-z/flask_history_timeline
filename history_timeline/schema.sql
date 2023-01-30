DROP TABLE IF EXISTS tabUser;

CREATE TABLE tabUser (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name VARCHAR(140),
    last_name VARCHAR(140),
    full_name VARCHAR(140) NOT NULL,
    email VARCHAR(140) UNIQUE NOT NULL,
    password VARCHAR(140) NOT NULL,
    user_type VARCHAR(140) NOT NULL,
    creation DATETIME(6),
    modified DATETIME(6),
    last_login DATETIME(6)
);
