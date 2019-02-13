import requests
import unittest

from app import create_app
from config import TestingConfig

TEST_DATA = {
    "book": {
        "isbn": "0380795272",
        "title": "Krondor: The Betrayal",
        "author": "Raymond E. Feist",
        "year": "1998",
    }
}


class TestGoodreadsApi(unittest.TestCase):
    def create_tables(self):
        # create books table
        self.app.engine.execute(
            """CREATE TABLE books (
            id INTEGER PRIMARY KEY,
            isbn VARCHAR UNIQUE NOT NULL,
            title VARCHAR NOT NULL,
            author VARCHAR NOT NULL,
            year INTEGER NOT NULL)"""
        )

    def insert_book(self):
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

    def setUp(self):
        self.app = create_app(TestingConfig)
        self.create_tables()
        self.insert_book()

    def tearDown(self):
        self.app.engine.dispose()

    def test_api(self):
        res = requests.get(
            "https://www.goodreads.com/book/review_counts.json",
            params={
                "key": self.app.config["GOODREADS_API_KEY"],
                "isbns": TEST_DATA["book"]["isbn"],
            },
        )
        res_json = res.json()["books"][0]
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res_json.get("isbn"), TEST_DATA["book"]["isbn"])
        self.assertIn("ratings_count", res_json)
        self.assertIn("reviews_count", res_json)
        self.assertIn("average_rating", res_json)
