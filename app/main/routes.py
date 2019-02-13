import requests
from datetime import datetime

from flask import current_app as app
from flask import render_template, request, jsonify, redirect, url_for, session
from app.main import bp


def goodreads(isbn):
    # use goodreads api to get data about given book
    res = requests.get(
        "https://www.goodreads.com/book/review_counts.json",
        params={"key": app.config["GOODREADS_API_KEY"], "isbns": isbn},
    )

    if not res:
        return None

    res_json = res.json()["books"][0]

    goodreads_dict = {}

    goodreads_dict["n_ratings"] = res_json.get("work_ratings_count")
    goodreads_dict["average_rating"] = res_json.get("average_rating")
    goodreads_dict["n_reviews"] = res_json.get("work_reviews_count")

    return goodreads_dict


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/results")
def book_results():
    search_string = request.args.get("search")
    s_string = "%{}%".format(search_string)
    books = app.db.execute(
        "SELECT * FROM books WHERE isbn ILIKE :search or title ILIKE :search or author ILIKE :search",
        {"search": s_string}).fetchall()

    if not books:
        return render_template("search_result.html")

    return render_template("search_result.html", books=books)


@bp.route("/books/<int:book_id>", methods=["GET", "POST"])
def book_details(book_id):
    book = app.db.execute(
        "SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()

    reviews = app.db.execute(
        """SELECT *
                         FROM reviews r
                         JOIN users u ON (u.id = r.author_id)
                         WHERE book_id = :book_id""",
        {"book_id": book["id"]},
    ).fetchall()

    goodreads_dict = goodreads(book["isbn"])

    if book is None:
        return render_template("index.html")

    if request.method == "POST":
        if "user" not in session:
            error = "You need to login first to submit review!"
            return render_template("login.html", error=error)

        current_user_id = app.db.execute(
            "SELECT id FROM users WHERE username = :username",
            {"username": session["user"]}).fetchone()
        if (
            app.db.execute(
                "SELECT author_id, book_id FROM reviews WHERE author_id = :author_id AND book_id = :book_id",
                {"book_id": book["id"], "author_id": current_user_id["id"]},
            ).rowcount > 0
        ):
            error = "You've already submitted review for that book"
            return render_template(
                "book.html",
                book=book,
                good=goodreads_dict,
                reviews=reviews,
                error=error,
            )

        rate = request.form.get("rating")
        review = request.form.get("review")

        app.db.execute(
            "INSERT INTO reviews (book_id, author_id, review, date_posted, rate) VALUES (:book_id, :author_id, :review, :date_posted, :rate)",
            {
                "book_id": book["id"],
                "author_id": current_user_id["id"],
                "review": review,
                "rate": int(rate),
                "date_posted": datetime.strptime(
                    datetime.now().strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M"
                ),
            },
        )
        app.db.commit()

        return redirect(url_for("main.book_details", book_id=book_id))

    return render_template("book.html", book=book, good=goodreads_dict, reviews=reviews)


@bp.route("/reviews/<string:username>")
def user_reviews(username):
    reviews = app.db.execute(
        """
        SELECT * FROM reviews r
        JOIN users u ON (u.id = r.author_id)
        JOIN books b on (b.id = r.book_id)
        WHERE username = :user""",
        {"user": username},
    ).fetchall()
    if not reviews:
        return render_template(
            "search_result.html",
            message=f"User {username} didn't submit any reviews"
        )
    return render_template("search_result.html", reviews=reviews, username=username)


@bp.route("/api/<string:isbn>")
def api_access(isbn):
    res = app.db.execute(
        "SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}
    ).fetchone()
    # return 404 if not in app.db
    if not res:
        return jsonify({'error': 'No results'}), 404

    goodreads_dict = goodreads(isbn)

    return jsonify(
        title=res["title"],
        author=res["author"],
        year=res["year"],
        isbn=isbn,
        review_count=goodreads_dict["n_reviews"],
        average_score=goodreads_dict["average_rating"],
    )
