-- needed to convert old DB structure (name was primary key) to one that works with mysql


CREATE TABLE IF NOT EXISTS  people_old(name TEXT PRIMARY KEY, karma INTEGER, shame INTEGER);

INSERT INTO people_old SELECT * FROM people;

DROP TABLE people;

CREATE TABLE IF NOT EXISTS people(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, name TEXT, karma INTEGER, shame INTEGER);

INSERT INTO people(name, karma, shame) SELECT name, karma, shame FROM people_old;

DROP TABLE people_old;
