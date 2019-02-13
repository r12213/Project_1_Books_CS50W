import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(os.getenv("DATABASE_URL"))


def main():
    # create users table
    engine.execute(
        """CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        username VARCHAR UNIQUE NOT NULL,
        password_hash VARCHAR NOT NULL,
        email VARCHAR UNIQUE)"""
    )

    # create books table
    engine.execute(
        """CREATE TABLE books (
        id SERIAL PRIMARY KEY,
        isbn VARCHAR UNIQUE NOT NULL,
        title VARCHAR NOT NULL,
        author VARCHAR NOT NULL,
        year INTEGER NOT NULL)"""
    )

    # create reviews table
    engine.execute(
        """CREATE TABLE reviews (
        id SERIAL PRIMARY KEY,
        book_id INTEGER REFERENCES books,
        author_id INTEGER REFERENCES users,
        review TEXT NOT NULL,
        rate INTEGER NOT NULL,
        date_posted TIMESTAMP WITHOUT TIME ZONE NOT NULL)"""
    )


if __name__ == "__main__":
    main()
