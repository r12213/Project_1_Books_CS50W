from werkzeug.security import generate_password_hash, check_password_hash

from flask import request, render_template, session
from flask import current_app as app
from app.auth import bp


@bp.route("/login", methods=["GET", "POST"])
def login():
    # use werkzeug here to check_password_hash
    if request.method == "POST":
        user_pass = app.db.execute(
            "SELECT password_hash FROM users WHERE username = :username",
            {"username": request.form.get("username")},
        ).fetchone()
        if user_pass is None:
            error = "Wrong login or user does not exists!"
            return render_template("auth/login.html", error=error)

        if check_password_hash(user_pass[0], request.form.get("password")):
            # assign to session
            session["user"] = request.form.get("username")
            success = "You are successfully logged in!"
            return render_template("index.html", success=success)
        else:
            error = "Wrong password!"
            return render_template("auth/login.html", error=error)
    else:
        return render_template("auth/login.html")


@bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get('email')
        # check if user or email is not already in database
        if (
            app.db.execute(
                "SELECT * FROM users WHERE username = :username", {"username": username}
            ).rowcount > 0
        ):
            error = "Account with this username address already exists!"
            return render_template("auth/signup.html", error=error)

        if (
            app.db.execute(
                "SELECT * FROM users WHERE email = :email", {"email": email}
            ).rowcount > 0
        ):
            error = "Account with this email address already exists!"
            return render_template("auth/signup.html", error=error)

        # check if passwords are same
        if request.form.get("password") != request.form.get("password_conf"):
            error = "Passwords are not the same!"
            return render_template("auth/signup.html", error=error)
        # generate_password_hash for new user
        passhash = generate_password_hash(request.form.get("password"))

        # create user in database
        app.db.execute(
            "INSERT INTO users (username, password_hash, email) VALUES (:username, :password_hash, :email)",
            {
                "username": request.form.get("username"),
                "password_hash": passhash,
                "email": request.form.get("email"),
            },
        )
        app.db.commit()
        success = "Success! You many now log in!"
        return render_template("auth/signup.html", success=success)
    else:
        return render_template("auth/signup.html")


@bp.route("/logout")
def logout():
    if "user" in session:
        session.pop("user", None)
    # add some message here
    success = "You have been successfully logged out!"
    return render_template("index.html", success=success)
