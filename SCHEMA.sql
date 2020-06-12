DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS books;

CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR UNIQUE NOT NULL,
  password VARCHAR NOT NULL
);
CREATE TABLE books (
  id SERIAL PRIMARY KEY,
  isbn VARCHAR UNIQUE NOT NULL,
  title VARCHAR NOT NULL,
  author VARCHAR NOT NULL,
  year INTEGER NOT NULL,
  reviews_count INTEGER,
  average_rating FLOAT

);
CREATE TABLE reviews (
  id SERIAL PRIMARY KEY,
  username VARCHAR NOT NULL,
  book_id INTEGER NOT NULL,
  rating FLOAT NOT NULL,
  text_review VARCHAR,

  FOREIGN KEY (username) REFERENCES users (username),
  FOREIGN KEY (book_id) REFERENCES books (id)
)
