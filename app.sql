DROP TABLE IF EXISTS bookings;
DROP TABLE IF EXISTS showtimes;
DROP TABLE IF EXISTS movies;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS admins;

CREATE TABLE movies (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    genre TEXT NOT NULL,
    description TEXT,
    duration INTEGER,
    rating TEXT,
    poster_url TEXT,
    price REAL DEFAULT 10.0
);

CREATE TABLE showtimes (
    id INTEGER PRIMARY KEY,
    movie_id INTEGER NOT NULL,
    show_time TEXT NOT NULL,
    FOREIGN KEY (movie_id) REFERENCES movies (id)
);

CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    password TEXT NOT NULL
);

CREATE TABLE bookings (
    id INTEGER PRIMARY KEY,
    showtime_id INTEGER NOT NULL,
    user_id TEXT NOT NULL,
    adult_seats INTEGER NOT NULL DEFAULT 0,
    child_seats INTEGER NOT NULL DEFAULT 0,
    total_seats INTEGER NOT NULL,
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (showtime_id) REFERENCES showtimes (id),
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);

CREATE TABLE admins (
    admin_id TEXT PRIMARY KEY,
    password TEXT NOT NULL
);

INSERT INTO movies (title, genre, description, duration, rating, poster_url, price) VALUES
('Neon Zone', 'Sci-Fi', 'A cyberpunk detective story in a neon-drenched futuristic city where memories can be bought and sold.', 60, '12A', '', 12.50),
('The Last Cartographer', 'Drama', 'An aging mapmaker on one last job to chart unknown territories before his eyesight fails.', 120, 'PG', '', 10.00),
('Crimson Tide Rising', 'Thriller', 'Two scientists race to find a cure as a deadly virus threatens to wipe out humanity.', 180, '15A', '', 11.00),
('Whiskers & Wonders', 'Animation', 'A curious cat opens a magical portal to a world where animals rule and humans are the pets.', 60, 'G', '', 8.50),
('Fault Lines', 'Comedy', 'A struggling comedian returns home and confronts family secrets that shake his world.', 120, 'PG', '', 9.50),
('Iron Requiem', 'Drama', 'A WWII soldier defects from his unit to save a family caught in the crossfire.', 180, 'R', '', 13.00),
('Final Strike', 'Action', 'An elite agent has one last mission to stop a global terrorist attack before time runs out.', 120, '18', '', 12.00),
('Beyond the Horizon', 'Adventure', 'A young explorer searches for a lost civilization hidden beyond uncharted seas.', 60, '16', '', 10.50),
('The Forgotten House', 'Horror', 'Teenagers explore an abandoned house hiding a deadly history that wants to repeat itself.', 120, '15A', '', 11.50),
('Countdown', 'Thriller', 'A hacker discovers a timer predicting real deaths and must stop them before time runs out.', 180, '12A', '', 10.00),
('Realm of Ashes', 'Fantasy', 'A young rider bonds with a dragon destined to change the course of history forever.', 60, 'PG', '', 9.00),
('Until We Met', 'Romance', 'Two strangers repeatedly cross paths in a bustling city before finally falling in love.', 120, '18', '', 8.00),
('City of Shadows', 'Crime', 'An undercover officer named Jake enters a dangerous crime syndicate to bring it down from within.', 180, 'PG', '', 11.00);

INSERT INTO showtimes (movie_id, show_time) VALUES
(1, '13:00'),
(1, '16:00'),
(2, '14:00'),
(3, '18:00'),
(4, '12:00'),
(5, '15:00'),
(6, '17:00'),
(7, '20:00'),
(8, '11:00'),
(9, '13:30'),
(10, '19:00'),
(11, '14:00'),
(12, '16:00'),
(13, '15:30');
INSERT INTO admins (admin_id, password)
VALUES ('Exzy', 'scrypt:32768:8:1$itJIOE5sEjogkAhw$b7d5b1c542229d42e30783242e2a051b0cc3c8927aca13050a2eabe88a521a99dca5f20ea4bd7266306e5d87259ea30b52e7ccc240f7ca04f567b8fc67fb319d');

UPDATE movies SET poster_url = 'neon-zone.jpg' WHERE id = 1;
UPDATE movies SET poster_url = 'the-last-cartographer.jpg' WHERE id = 2;
UPDATE movies SET poster_url = 'crimson-tide-rising.jpg' WHERE id = 3;
UPDATE movies SET poster_url = 'whiskers-and-wonders.jpg' WHERE id = 4;
UPDATE movies SET poster_url = 'fault-lines.jpg' WHERE id = 5;
UPDATE movies SET poster_url = 'iron-requiem.jpg' WHERE id = 6;
UPDATE movies SET poster_url = 'final-strike.jpg' WHERE id = 7;
UPDATE movies SET poster_url = 'beyond-the-horizon.jpg' WHERE id = 8;
UPDATE movies SET poster_url = 'the-forgotten-house.jpg' WHERE id = 9;
UPDATE movies SET poster_url = 'countdown.jpg' WHERE id = 10;
UPDATE movies SET poster_url = 'realm-of-ashes.jpg' WHERE id = 11;
UPDATE movies SET poster_url = 'until-we-met.jpg' WHERE id = 12;
UPDATE movies SET poster_url = 'city-of-shadows.jpg' WHERE id = 13;