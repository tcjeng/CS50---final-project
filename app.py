import os
from cs50 import SQL
from flask import Flask, redirect, render_template, request, session, flash
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Session configuration
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Database configuration
db = SQL("sqlite:///books.db")

# Create tables if not already created
db.execute("""
    CREATE TABLE IF NOT EXISTS books (
        book_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        genre TEXT,
        page_count INTEGER,
        date_started DATE,
        date_finished DATE,
        rating REAL CHECK (rating >= 0 AND rating <= 5),
        review TEXT,
        status TEXT CHECK (status IN ('TBR', 'In Progress', 'Completed')),
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    );
""")

db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        nickname TEXT,
        password_hash TEXT NOT NULL,
        email TEXT UNIQUE,
        date_joined DATE DEFAULT CURRENT_DATE
    );
""")

db.execute("""
    CREATE TABLE IF NOT EXISTS reading_goals (
        user_id INTEGER PRIMARY KEY,
        books_to_read INTEGER NOT NULL,
        goal_date DATE NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    );
""")

@app.route("/register", methods=["GET", "POST"])
def register():
    """User registration route"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Check if the username and password match
        if not username or not password or not confirmation:
            flash("All fields are required!")
            return redirect("/register")

        if password != confirmation:
            flash("Passwords don't match!")
            return redirect("/register")

        # Check if the username already exists
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) != 0:
            flash("Username already taken!")
            return redirect("/register")

        # Insert user into the database
        db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", username, generate_password_hash(password))

        # Log the user in
        session["user_id"] = db.execute("SELECT user_id FROM users WHERE username = ?", username)[0]["user_id"]

        return redirect("/")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """User login route"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Check that both fields are filled
        if not username or not password:
            flash("Username and password are required!")
            return redirect("/login")

        # Query the database for the user
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,))

        if len(user) != 1 or not check_password_hash(user[0]["password_hash"], password):
            flash("Invalid username or password!")
            return redirect("/login")

        # Store user info in the session
        session["user_id"] = user[0]["user_id"]
        session["username"] = user[0]["username"]

        return redirect("/")

    return render_template("login.html")


@app.route("/")
def index():
    """Homepage, show books if logged in"""
    if "user_id" not in session:
        return redirect("/login")  # If not logged in, redirect to login

    goal = db.execute("SELECT * FROM reading_goals WHERE user_id = ?", session["user_id"])
    books = db.execute("SELECT * FROM books WHERE user_id = ?", session["user_id"])
    user = db.execute("SELECT username FROM users WHERE user_id = ?", session["user_id"])
    username = user[0]["username"] if user else "User"

    return render_template("index.html", books=books, username=username, goal=goal[0] if goal else None)


@app.route("/add", methods=["GET", "POST"])
def add_book():
    """Allow user to add a new book"""
    if "user_id" not in session:
        return redirect("/login")  # Redirect to login if user is not logged in

    if request.method == "POST":
        # Get data from the form
        title = request.form.get("title")
        author = request.form.get("author")
        genre = request.form.get("genre")
        page_count = request.form.get("page_count")
        date_started = request.form.get("date_started")
        date_finished = request.form.get("date_finished")
        rating = request.form.get("rating")
        review = request.form.get("review")
        status = request.form.get("status")

        # Validate inputs
        if not title or not author or not status:
            flash("Title, Author, and Status are required!")
            return redirect("/add")

        # If rating is provided, ensure it's a valid value
        if rating:
            rating = float(rating)
            if not (0 <= rating <= 5):
                flash("Rating must be between 0 and 5!")
                return redirect("/add")

        # Insert the book into the database
        db.execute("""
            INSERT INTO books (user_id, title, author, genre, page_count, date_started, date_finished, rating, review, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, session["user_id"], title, author, genre, page_count, date_started, date_finished, rating, review, status)

        flash("Book added successfully!")
        return redirect("/")

    return render_template("add_book.html")

@app.route("/logout")
def logout():
    """Logs the user out and clears the session."""
    session.clear()
    flash("You have been logged out!")
    return redirect("/login")


@app.route("/edit/<int:book_id>", methods=["GET", "POST"])
def edit_book(book_id):
    """Allow user to edit a book"""
    if "user_id" not in session:
        return redirect("/login")

    # Get the current book from the database
    book = db.execute("SELECT * FROM books WHERE book_id = ? AND user_id = ?", book_id, session["user_id"])

    if len(book) != 1:
        flash("Book not found!")
        return redirect("/")

    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")
        genre = request.form.get("genre")
        page_count = request.form.get("page_count")
        status = request.form.get("status")
        review = request.form.get("review")  # Get review text

        if not title or not author or not status:
            flash("Title, Author, and Status are required!")
            return redirect(f"/edit/{book_id}")

        # Update the book in the database, including the review field
        db.execute("""
            UPDATE books
            SET title = ?, author = ?, genre = ?, page_count = ?, status = ?, review = ?
            WHERE book_id = ? AND user_id = ?
        """, title, author, genre, page_count, status, review, book_id, session["user_id"])

        flash("Book updated successfully!")
        return redirect("/")

    return render_template("edit_book.html", book=book[0])


@app.route("/delete/<int:book_id>")
def delete_book(book_id):
    """Allow user to delete a book"""
    # Ensure the user is logged in
    if "user_id" not in session:
        return redirect("/login")

    # Delete the book from the database
    db.execute("DELETE FROM books WHERE book_id = ? AND user_id = ?", book_id, session["user_id"])

    flash("Book deleted successfully!")
    return redirect("/")

@app.route("/goal", methods=["GET", "POST"])
def goal():
    """Allow user to set or view their reading goal."""
    if "user_id" not in session:
        return redirect("/login")  # Redirect to login if user is not logged in

    if request.method == "POST":
        # Get data from the form
        books_to_read = request.form.get("books_to_read")
        goal_date = request.form.get("goal_date")

        # Validate inputs
        if not books_to_read or not goal_date:
            flash("Both fields are required!")
            return redirect("/goal")

        try:
            # Insert or update the goal in the database
            db.execute("""
                INSERT INTO reading_goals (user_id, books_to_read, goal_date)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                books_to_read = ?, goal_date = ?;
            """, session["user_id"], books_to_read, goal_date, books_to_read, goal_date)

            flash("Your reading goal has been set!")
            return redirect("/")

        except Exception as e:
            flash(f"Error: {e}")
            return redirect("/goal")

    # Fetch existing goal if it exists
    goal = db.execute("SELECT * FROM reading_goals WHERE user_id = ?", session["user_id"])

    return render_template("goal.html", goal=goal[0] if goal else None)


@app.route("/delete_goal", methods=["POST"])
def delete_goal():
    """Allow user to delete their reading goal"""
    if "user_id" not in session:
        return redirect("/login")  # If not logged in, redirect to login

    # Delete the reading goal for the current user
    db.execute("DELETE FROM reading_goals WHERE user_id = ?", session["user_id"])

    flash("Your reading goal has been deleted.")
    return redirect("/")  # Redirect back to the homepage

@app.route("/book/<int:book_id>")
def book_details(book_id):
    """Show details for a specific book."""
    if "user_id" not in session:
        return redirect("/login")  # If not logged in, redirect to login

    # Fetch the book details from the database
    book = db.execute("SELECT * FROM books WHERE book_id = ? AND user_id = ?", book_id, session["user_id"])

    # Check if the book exists and belongs to the current user
    if not book:
        flash("Book not found.")
        return redirect("/")

    return render_template("book_detail.html", book=book[0])


if __name__ == "__main__":
    app.run(debug=True)
