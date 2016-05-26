
CREATE TABLE IP (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  token text,
  server_addr text,
  update_time text
);

CREATE TABLE Camera (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shttercount text,
    state text
);

CREATE TABLE Users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT,
  password TEXT
);

