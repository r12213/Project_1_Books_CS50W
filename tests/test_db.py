import unittest
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from app import create_app
from config import TestingConfig

TEST_DATA = {
    "book": {
        "isbn": "0380795272",
        "title": "Krondor: The Betrayal",
        "author": "Raymond E. Feist",
        "year": "1998",
    },
    "user": {
        "username": "test_user",
        "password": "test_pass",
        "email": "test@email.com",
    },
    "review": {
        "review_text": "test_review",
        "rate": "5",
        "date_posted": datetime.strptime(
            datetime.now().strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M"
        ),
    },
}


class TestDBSchema(unittest.TestCase):
    # using in memory sqlite db for tests
    # schema is different than for postgres
    def create_tables(self):
        self.app.engine.execute(
            """CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username VARCHAR UNIQUE NOT NULL,
            password_hash VARCHAR NOT NULL,
            email VARCHAR UNIQUE)"""
        )

        # create books table
        self.app.engine.execute(
            """CREATE TABLE books (
            id INTEGER PRIMARY KEY,
            isbn VARCHAR UNIQUE NOT NULL,
            title VARCHAR NOT NULL,
            author VARCHAR NOT NULL,
            year INTEGER NOT NULL)"""
        )

        # create reviews table
        self.app.engine.execute(
            """CREATE TABLE reviews (
            id INTEGER PRIMARY KEY,
            book_id INTEGER REFERENCES books,
            author_id INTEGER REFERENCES users,
            review TEXT NOT NULL,
            rate INTEGER NOT NULL,
            date_posted TIMESTAMP WITHOUT TIME ZONE NOT NULL)"""
        )

    def setUp(self):
        self.app = create_app(TestingConfig)
        self.create_tables()

    def tearDown(self):
        self.app.engine.dispose()

    def test_insert_book_and_fetch_it(self):
        self.app.db.execute(
            "INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
            {
                "isbn": TEST_DATA["book"]["isbn"],
                "title": TEST_DATA["book"]["title"],
                "author": TEST_DATA["book"]["author"],
                "year": int(TEST_DATA["book"]["year"]),
            },
        )
        self.app.db.commit()
        book = self.app.db.execute(
            "SELECT * FROM books WHERE title = :title",
            {"title": TEST_DATA["book"]["title"]},
        ).fetchone()
        self.assertEqual(book["title"], TEST_DATA["book"]["title"])
        self.assertEqual(book["author"], TEST_DATA["book"]["author"])
        self.assertEqual(book["isbn"], TEST_DATA["book"]["isbn"])
        self.assertEqual(book["year"], int(TEST_DATA["book"]["year"]))
        self.assertEqual(book["id"], 1)  # first record in db

    def test_insert_user_and_check_passhash(self):
        passhash = generate_password_hash(TEST_DATA["user"]["password"])
        self.app.db.execute(
            "INSERT INTO users (username, password_hash, email) VALUES (:username, :password_hash, :email)",
            {
                "username": TEST_DATA["user"]["username"],
                "password_hash": passhash,
                "email": TEST_DATA["user"]["email"],
            },
        )
        self.app.db.commit()
        user = self.app.db.execute(
            "SELECT * FROM users WHERE username = :username",
            {"username": TEST_DATA["user"]["username"]},
        ).fetchone()
        self.assertTrue(
            check_password_hash(user["password_hash"], TEST_DATA["user"]["password"])
        )
        self.assertFalse(check_password_hash(user["password_hash"], "false_pass"))

    def test_insert_complete_review(self):
        # prepare book in db
        self.app.db.execute(
            "INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
            {
                "isbn": TEST_DATA["book"]["isbn"],
                "title": TEST_DATA["book"]["title"],
                "author": TEST_DATA["book"]["author"],
                "year": int(TEST_DATA["book"]["year"]),
            },
        )

        # prepare user in db
        self.app.db.execute(
            "INSERT INTO users (username, password_hash, email) VALUES (:username, :password_hash, :email)",
            {
                "username": TEST_DATA["user"]["username"],
                "password_hash": "mock_hash",
                "email": TEST_DATA["user"]["email"],
            },
        )
        self.app.db.commit()
        # fetch created book and user
        book1 = self.app.db.execute("SELECT * FROM books").fetchone()
        user1 = self.app.db.execute("SELECT * FROM users").fetchone()

        # prepare review
        self.app.db.execute(
            "INSERT INTO reviews (review, rate, date_posted, book_id, author_id) VALUES (:review, :rate, :date_posted, :book_id, :author_id)",
            {
                "book_id": book1["id"],
                "author_id": user1["id"],
                "review": TEST_DATA["review"]["review_text"],
                "rate": int(TEST_DATA["review"]["rate"]),
                "date_posted": datetime.strptime(
                    datetime.now().strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M"
                ),
            },
        )
        # fetch review
        review = self.app.db.execute("SELECT * FROM reviews").fetchone()
        self.assertEqual(review["book_id"], book1["id"])
        self.assertEqual(review["author_id"], user1["id"])
        self.assertEqual(review["review"], TEST_DATA["review"]["review_text"])
        self.assertEqual(review["rate"], int(TEST_DATA["review"]["rate"]))
        self.assertEqual(
            review["date_posted"],
            TEST_DATA["review"]["date_posted"].strftime("%Y-%m-%d %H:%M:%S"),
        )
        self.assertEqual(review["id"], 1)  # first record in db
