from flask import Flask, render_template, request, redirect, session, flash, url_for
from datetime import datetime, timedelta
import sqlite3

app = Flask(__name__)
app.config["SECRET_KEY"] = "SECRET"
app.config["DATABASE"] = "library.sqlite3"


# MODELS
def create_users_table():
    conn = sqlite3.connect(app.config["DATABASE"])
    cursor = conn.cursor()

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            usertype TEXT NOT NULL DEFAULT 'user')"""
    )

    conn.commit()
    conn.close()


def create_sections_table():
    conn = sqlite3.connect(app.config["DATABASE"])
    cursor = conn.cursor()

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS sections (
            section_id INTEGER PRIMARY KEY AUTOINCREMENT,
            section_name TEXT UNIQUE NOT NULL,
            section_dateCreated DATE NOT NULL,
            section_desc TEXT,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id))"""
    )

    conn.commit()
    conn.close()


def create_books_table():
    conn = sqlite3.connect(app.config["DATABASE"])
    cursor = conn.cursor()

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_name TEXT NOT NULL,
            book_content TEXT,
            book_author TEXT NOT NULL,
            book_price INTEGER NOT NULL,
            section_id INTEGER,
            FOREIGN KEY (section_id) REFERENCES sections (section_id))"""
    )

    conn.commit()
    conn.close()


def create_rating_table():
    conn = sqlite3.connect(app.config["DATABASE"])
    cursor = conn.cursor()

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS ratings (
            rating_id INTEGER PRIMARY KEY AUTOINCREMENT,
            rating_value INTEGER NOT NULL,
            book_id INTEGER,
            user_id INTERGER,
            FOREIGN KEY (book_id) REFERENCES books (book_id),
            FOREIGN KEY (user_id) REFERENCES users (id))"""
    )

    conn.commit()
    conn.close()


def create_bookIssue_table():
    conn = sqlite3.connect(app.config["DATABASE"])
    cursor = conn.cursor()

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS bookIssues (
            bookIssue_id INTEGER PRIMARY KEY AUTOINCREMENT,
            bookIssue_issueDate DATE NOT NULL,
            bookIssue_returnDate DATE NOT NULL,
            bookIssue_access INTEGER NOT NULL DEFAULT 0,
            bookIssue_requested INTEGER NOT NULL DEFAULT 0,
            book_id INTEGER,
            user_id INTERGER,
            FOREIGN KEY (book_id) REFERENCES books (book_id),
            FOREIGN KEY (user_id) REFERENCES users (id))"""
    )

    conn.commit()
    conn.close()


create_users_table()
create_sections_table()
create_books_table()
create_rating_table()
create_bookIssue_table()


# BASE ROUTE
@app.route("/")
def root():
    return redirect("/home")


# DISPLAY LOGIN PAGE
@app.route("/home", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        choice = request.form["choice"]
        if choice == "register":
            return redirect("/register")
        elif choice == "login":
            return redirect("/login")
        elif choice == "admin_login":
            return redirect("/admin_login")

    return render_template("home.html")


# USER REGISTRATION
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect(app.config["DATABASE"])
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            conn.close()
            return "Username already exists. Please choose a different username.", 409
        else:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password),
            )
            conn.commit()
            conn.close()
        return redirect(url_for("user_login"))

    return render_template("register.html")


# USER LOGIN
@app.route("/user_login", methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect(app.config["DATABASE"])
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM users WHERE username = ? AND password = ? AND usertype = "user"',
            (username, password),
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            session["username"] = user[1]
            session["usertype"] = user[3]
            session["user_id"] = user[0]
            return redirect(url_for("user_dashboard"))

        else:
            return "Invalid credentials. Please try again.", 401
    return render_template("user_login.html")


# ADMIN LOGIN
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["admin_username"]
        password = request.form["admin_password"]

        conn = sqlite3.connect(app.config["DATABASE"])
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM users WHERE username = ? AND password = ? AND usertype = "admin"',
            (username, password),
        )
        user = cursor.fetchone()
        conn.close()

        if user is None:
            return "Invalid admin credentials. Please try again.", 401
        else:
            session["username"] = user[1]
            session["usertype"] = user[3]
            session["user_id"] = user[0]
            return redirect(url_for("admin_dashboard"))

    return render_template("admin_login.html")


# ADMIN DASHBOARD
@app.route("/admin_dashboard", methods=["GET", "POST"])
def admin_dashboard():
    if "username" not in session or session["usertype"] != "admin":
        return redirect(url_for("admin_login"))

    else:
        conn = sqlite3.connect(app.config["DATABASE"])
        cursor = conn.cursor()

        # Retrieve all Sections
        cursor.execute("SELECT * FROM sections")
        sections_data = cursor.fetchall()

        conn.close()

        return render_template(
            "admin_dashboard.html",
            sections_data=sections_data,
            session=session,
        )


# ADMIN ADD SECTION ACCESS
@app.route("/admin_dashboard/add_section", methods=["GET", "POST"])
def add_section():
    if "username" not in session or session["usertype"] != "admin":
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        user_id = session["user_id"]
        section_name = request.form["section_name"]
        section_dateCreated = datetime.now().strftime("%Y-%m-%d")
        section_desc = request.form["section_desc"]

        if section_name:
            conn = sqlite3.connect(app.config["DATABASE"])
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO sections (section_name, section_dateCreated, section_desc, user_id) VALUES (?,?,?,?)",
                (section_name, section_dateCreated, section_desc, user_id),
            )
            conn.commit()
            conn.close()

            return redirect("/admin_dashboard")
    else:
        return redirect("/admin_login")


# ADMIN EDIT SECTION ACCESS
@app.route("/admin_dashboard/edit_section/<int:section_id>", methods=["GET", "POST"])
def edit_section(section_id):
    if "username" in session and session["usertype"] == "admin":
        conn = sqlite3.connect(app.config["DATABASE"])
        cursor = conn.cursor()

        if request.method == "POST":
            if "new_section_name" in request.form:
                new_section_name = request.form["new_section_name"]
                cursor.execute(
                    "UPDATE sections SET section_name = ? WHERE section_id = ?",
                    (new_section_name, section_id),
                )
                conn.commit()

            if "new_section_dateCreated" in request.form:
                new_section_dateCreated = request.form["new_section_dateCreated"]
                cursor.execute(
                    "UPDATE sections SET section_dateCreated = ? WHERE section_id = ?",
                    (new_section_dateCreated, section_id),
                )
                conn.commit()

            if "new_section_desc" in request.form:
                new_section_desc = request.form["new_section_desc"]
                cursor.execute(
                    "UPDATE sections SET section_desc = ? WHERE section_id = ?",
                    (new_section_desc, section_id),
                )
                conn.commit()

        return render_template("edit_section.html")
    else:
        return redirect("/admin_login")


# ADMIN DELETE SECTION ACCESS
@app.route("/admin_dashboard/delete_section/<int:section_id>", methods=["GET", "POST"])
def delete_section(section_id):
    if "username" in session and session["usertype"] == "admin":
        conn = sqlite3.connect(app.config["DATABASE"])
        cursor = conn.cursor()

        if request.method == "GET":
            return render_template("confirm_delete_section.html")

        elif request.method == "POST":
            cursor.execute("DELETE FROM books WHERE section_id = ?", (section_id,))
            cursor.execute("DELETE FROM sections WHERE section_id = ?", (section_id,))
            conn.commit()
            conn.close()

            return redirect("/admin_dashboard")

    else:
        return redirect("/admin_login")


# ADMIN BOOKS OF SECTION
@app.route("/admin_dashboard/section_books/<int:section_id>", methods=["GET", "POST"])
def section_books(section_id):
    if "username" not in session or session["usertype"] == "admin":
        conn = sqlite3.connect(app.config["DATABASE"])
        cursor = conn.cursor()

        # Retrieve all Books
        cursor.execute("SELECT * FROM books where section_id = ?", (section_id,))
        books_data = cursor.fetchall()

        cursor.execute(
            "SELECT section_name, section_id FROM sections WHERE section_id = ?",
            (section_id,),
        )
        section_details = cursor.fetchone()
        conn.close()

        return render_template(
            "section_books.html",
            books_data=books_data,
            session=session,
            section_details=section_details,
        )

    else:
        return redirect("/admin_login")


# ADMIN ADD BOOK ACCESS
@app.route("/admin_dashboard/add_book/<int:section_id>", methods=["GET", "POST"])
def add_book(section_id):
    if "username" not in session or session["usertype"] != "admin":
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        book_name = request.form["book_name"]
        book_content = request.form["book_content"]
        book_author = request.form["book_author"]
        book_price = request.form["book_price"]

        if book_name:
            conn = sqlite3.connect(app.config["DATABASE"])
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO books (book_name, book_content, book_author, book_price, section_id) VALUES (?,?,?,?,?)",
                (book_name, book_content, book_author, book_price, section_id),
            )
            conn.commit()
            conn.close()

            return redirect("/admin_dashboard/section_books/" + str(section_id))
    else:
        return redirect("/admin_login")


# ADMIN EDIT BOOK ACCESS
@app.route(
    "/admin_dashboard/edit_book/<int:section_id>/<int:book_id>", methods=["GET", "POST"]
)
def edit_book(section_id, book_id):
    if "username" in session and session["usertype"] == "admin":
        conn = sqlite3.connect(app.config["DATABASE"])
        cursor = conn.cursor()

        if request.method == "POST":
            if "new_book_name" in request.form:
                new_book_name = request.form["new_book_name"]
                cursor.execute(
                    "UPDATE books SET book_name = ? WHERE section_id = ? AND book_id = ?",
                    (new_book_name, section_id, book_id),
                )
                conn.commit()

            if "new_book_price" in request.form:
                new_book_price = request.form["new_book_price"]
                cursor.execute(
                    "UPDATE books SET book_price = ? WHERE section_id = ? AND book_id = ?",
                    (new_book_price, section_id, book_id),
                )
                conn.commit()

            if "new_book_author" in request.form:
                new_book_author = request.form["new_book_author"]
                cursor.execute(
                    "UPDATE books SET book_author = ? WHERE section_id = ? AND book_id = ?",
                    (new_book_author, section_id, book_id),
                )
                conn.commit()

            if "new_book_content" in request.form:
                new_book_content = request.form["new_book_content"]
                cursor.execute(
                    "UPDATE books SET book_content = ? WHERE section_id = ? AND book_id = ?",
                    (new_book_content, section_id, book_id),
                )
                conn.commit()
            conn.close()

        return render_template("edit_book.html")
    else:
        return redirect("/admin_login")


# ADMIN DELETE BOOK ACCESS
@app.route(
    "/admin_dashboard/delete_book/<int:section_id>/<int:book_id>",
    methods=["GET", "POST"],
)
def delete_book(section_id, book_id):
    if "username" in session and session["usertype"] == "admin":
        if request.method == "GET":
            return render_template("confirm_delete_book.html")

        elif request.method == "POST":
            conn = sqlite3.connect(app.config["DATABASE"])
            cursor = conn.cursor()

            cursor.execute("DELETE FROM books WHERE book_id = ?", (book_id,))
            conn.commit()
            conn.close()

            return redirect("/admin_dashboard/section_books/" + str(section_id))
    else:
        return redirect("/admin_login")


# ASSIGN SECTION TO BOOK
@app.route(
    "/admin_dashboard/assign_section_to_book/<int:section_id>/<int:book_id>",
    methods=["GET", "POST"],
)
def assign_section_to_book(section_id, book_id):
    if "username" in session and session["usertype"] == "admin":
        conn = sqlite3.connect(app.config["DATABASE"])
        cursor = conn.cursor()

        if request.method == "POST":
            if "new_section_name" in request.form:
                new_section_name = request.form["new_section_name"]
                cursor.execute(
                    "SELECT * FROM sections WHERE section_name = ?", (new_section_name,)
                )
                section_id = cursor.fetchone()[0]

            if section_id:
                cursor.execute(
                    "UPDATE books SET section_id = ? WHERE book_id = ?",
                    (section_id, book_id),
                )

                conn.commit()
                conn.close()

        return render_template("assign_section_to_book.html")
    else:
        return redirect("/admin_login")


# VIEW RATINGS
@app.route("/admin_dashboard/view_ratings", methods=["GET", "POST"])
def view_ratings():
    if "username" not in session or session["usertype"] != "admin":
        return redirect(url_for("admin_login"))

    else:
        # Retrieve all Ratings
        conn = sqlite3.connect(app.config["DATABASE"])
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ratings")
        ratings_data = cursor.fetchall()
        ratings = {}
        for item in ratings_data:
            cursor.execute("SELECT book_name FROM books WHERE book_id = ?", (item[2],))
            book_name = cursor.fetchone()[0]
            cursor.execute("SELECT username FROM users WHERE id = ?", (item[3],))
            username = cursor.fetchone()[0]
            ratings[item] = (book_name, username)
        conn.close()

        return render_template(
            "view_ratings.html", ratings_data=ratings_data, ratings=ratings
        )


# VIEW RATING GRAPH
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use("agg")


@app.route("/view_ratings/rating_graph", methods=["GET", "POST"])
def rating_graph():
    if "username" not in session or session["usertype"] != "admin":
        return redirect(url_for("admin_login"))

    else:
        conn = sqlite3.connect(app.config["DATABASE"])
        cursor = conn.cursor()
        cursor.execute("SELECT rating_value FROM ratings")
        ratings = cursor.fetchall()
        cursor.execute("SELECT COUNT(*) FROM ratings GROUP BY rating_value")
        values = cursor.fetchall()
        conn.close()

        # Process data
        ratings_values = [rating[0] for rating in ratings]
        ratings_value_counts = [value[0] for value in values]
        ratings_values = list(set(ratings_values))
        # ratings_values = sorted(ratings_values)
        # ratings_value_counts = sorted(ratings_value_counts)
        print(ratings_value_counts)
        print(ratings_values)

        # Plotting Bar Graph
        plt.figure(figsize=(5, 5))
        plt.barh(ratings_values, ratings_value_counts, height=0.2, color="red")
        plt.xlabel("Frequency")
        plt.ylabel("Rating")
        plt.title("Distribution of Ratings")
        plt.savefig("static/img_data.png")
        plt.close()

        return render_template("rating_graph.html")


# VIEW ISSUE REQUESTS
@app.route("/admin_dashboard/view_book_requests", methods=["GET", "POST"])
def view_book_requests():
    if "username" not in session or session["usertype"] != "admin":
        return redirect(url_for("admin_login"))

    else:
        # Retrieve all Requests
        conn = sqlite3.connect(app.config["DATABASE"])
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM bookIssues")
        requests_data = cursor.fetchall()
        requests = {}
        for item in requests_data:
            cursor.execute("SELECT book_name FROM books WHERE book_id = ?", (item[5],))
            book_name = cursor.fetchone()[0]
            cursor.execute("SELECT username FROM users WHERE id = ?", (item[6],))
            section_name = cursor.fetchone()[0]
            requests[item] = (book_name, section_name)
        conn.close()

        conn.close()

        return render_template(
            "view_book_requests.html", requests_data=requests_data, requests=requests
        )


# ADMIN GRANT BOOK ACCESS
@app.route(
    "/view_book_requests/grant_access/<int:bookIssue_id>", methods=["GET", "POST"]
)
def grant_access(bookIssue_id):
    if "username" not in session or session["usertype"] != "admin":
        return redirect(url_for("admin_login"))

    conn = sqlite3.connect(app.config["DATABASE"])
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE bookIssues SET bookIssue_access = 1 where bookIssue_id = ?",
        (bookIssue_id,),
    )
    conn.commit()
    conn.close()

    return redirect("/admin_dashboard/view_book_requests")


# ADMIN REVOKE BOOK ACCESS
@app.route(
    "/view_book_requests/revoke_access/<int:bookIssue_id>", methods=["GET", "POST"]
)
def revoke_access(bookIssue_id):
    if "username" not in session or session["usertype"] != "admin":
        return redirect(url_for("admin_login"))

    conn = sqlite3.connect(app.config["DATABASE"])
    cursor = conn.cursor()

    cursor.execute(
        "SELECT bookIssue_access FROM bookIssues where bookIssue_id = ?",
        (bookIssue_id,),
    )
    access = cursor.fetchone()[0]

    if access == 1:
        cursor.execute("DELETE FROM bookIssues WHERE bookIssue_id = ?", (bookIssue_id,))
        conn.commit()
        conn.close()

    return redirect("/admin_dashboard/view_book_requests")


# USER DASHBOARD
@app.route("/user_dashboard")
def user_dashboard():
    conn = sqlite3.connect(app.config["DATABASE"])
    cursor = conn.cursor()
    user_id = session["user_id"]

    # Retrieve all Sections
    cursor.execute("SELECT * FROM sections")
    sections_data = cursor.fetchall()
    books_by_section = {}

    for section in sections_data:
        cursor.execute("SELECT * FROM books WHERE section_id = ?", (section[0],))
        books = cursor.fetchall()
        books_by_section[section] = books
    conn.close()

    return render_template(
        "user_dashboard.html",
        sections_data=sections_data,
        books_by_section=books_by_section,
        session=session,
    )


# USER ISSUE BOOK
@app.route("/user_dashboard/issue_book/<int:book_id>", methods=["GET", "POST"])
def issue_book(book_id):
    user_id = session["user_id"]
    conn = sqlite3.connect(app.config["DATABASE"])
    cursor = conn.cursor()

    cursor.execute(
        "SELECT bookIssue_id FROM bookIssues WHERE book_id = ? AND user_id = ?",
        (book_id, user_id),
    )
    entry = cursor.fetchall()

    if entry:
        cursor.execute("SELECT book_name FROM books WHERE book_id = ?", (book_id,))
        book_name = cursor.fetchone()

        cursor.execute(
            "SELECT * FROM bookIssues WHERE bookIssue_id = ?", (entry[0][0],)
        )
        issue_data = cursor.fetchone()

        def calculate_date_difference(date1_str, date2_str):
            date1 = datetime.strptime(date1_str, "%Y-%m-%d")
            date2 = datetime.strptime(date2_str, "%Y-%m-%d")

            difference_days = (date1 - date2).days

            return difference_days

        current_date = datetime.now().strftime("%Y-%m-%d")
        date_criteria = calculate_date_difference(issue_data[2], current_date)

        if date_criteria < 0:
            cursor.execute(
                "DELETE FROM bookIssues WHERE bookIssue_id = ?", (entry[0][0],)
            )
            conn.commit()
            conn.close()

            return render_template("book_timeout.html")

        return render_template(
            "issue_book.html",
            book_name=book_name,
            issue_data=issue_data,
        )

    else:
        issue_date = datetime.now().strftime("%Y-%m-%d")
        return_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

        cursor.execute(
            "INSERT INTO bookIssues (bookIssue_issueDate, bookIssue_returnDate, user_id, book_id) VALUES (?, ?, ?, ?)",
            (issue_date, return_date, user_id, book_id),
        )
        conn.commit()
        conn.close()

        return redirect("/user_dashboard/issue_book/" + str(book_id))


# USER REQUEST BOOK
@app.route("/issue_book/request_book/<int:book_id>", methods=["GET", "POST"])
def request_book(book_id):
    user_id = session["user_id"]
    conn = sqlite3.connect(app.config["DATABASE"])
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(user_id) FROM bookissues WHERE bookIssue_requested = 1 AND user_id = ?",
        (user_id,),
    )
    user_book_count = cursor.fetchone()[0]

    if user_book_count == 5:
        return render_template("user_request_overload.html")
    else:
        cursor.execute(
            "UPDATE bookIssues SET bookIssue_requested = 1 WHERE user_id = ? AND book_id = ?",
            (
                user_id,
                book_id,
            ),
        )
        conn.commit()
        conn.close()

    return redirect("/user_dashboard/issue_book/" + str(book_id))


# USER CANCEL REQUEST
@app.route("/issue_book/cancel_request/<int:book_id>", methods=["GET", "POST"])
def cancel_request(book_id):
    user_id = session["user_id"]
    conn = sqlite3.connect(app.config["DATABASE"])
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE bookIssues SET bookIssue_requested = 0 WHERE user_id = ? AND book_id = ?",
        (
            user_id,
            book_id,
        ),
    )
    conn.commit()
    conn.close()

    return redirect("/user_dashboard/issue_book/" + str(book_id))


# USER RETURN BOOK
@app.route("/issue_book/return_book/<int:book_id>", methods=["GET", "POST"])
def return_book(book_id):
    user_id = session["user_id"]
    conn = sqlite3.connect(app.config["DATABASE"])
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM bookIssues WHERE user_id = ? AND book_id = ?",
        (
            user_id,
            book_id,
        ),
    )
    conn.commit()
    conn.close()

    return redirect("/user_dashboard/issue_book/" + str(book_id))


# USER BOOK RATING
@app.route("/user_dashboard/rate_book/<int:book_id>", methods=["GET", "POST"])
def rate_book(book_id):
    if "username" not in session or session["usertype"] != "user":
        return redirect(url_for("user_login"))

    if request.method == "POST":
        user_id = session["user_id"]
        rating_value = request.form["rating_value"]

        conn = sqlite3.connect(app.config["DATABASE"])
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO ratings (rating_value, user_id, book_id) VALUES (?, ?, ?)",
            (rating_value, user_id, book_id),
        )
        conn.commit()
        conn.close()

        return redirect("/user_dashboard")


# LOGOUT
@app.route("/logout")
def logout():
    user_type = session.get("usertype")
    if user_type == "admin":
        dashboard_url = "/admin_dashboard"
    else:
        dashboard_url = "/user_dashboard"

    return render_template("logout_confirmation.html", dashboard_url=dashboard_url)


@app.route("/logout", methods=["POST"])
def perform_logout():
    if request.form.get("action") == "logout":
        session.clear()
        flash("You have been logged out.", "Success")

    return redirect(url_for("home"))


# SEARCH BASED ON SECTION (ADMIN)
@app.route("/admin_dashboard/section_search_results", methods=["GET", "POST"])
def admin_section_search_results():
    # Fetch books based on section search criteria
    admin_section_search = request.args.get("admin_section_search")

    conn = sqlite3.connect(app.config["DATABASE"])
    cursor = conn.cursor()

    cursor.execute(
        "SELECT section_id FROM sections WHERE section_name = ?",
        (admin_section_search,),
    )
    section_id = cursor.fetchone()[0]

    cursor.execute(
        "SELECT * FROM books WHERE section_id=?",
        (section_id,),
    )
    books_data = cursor.fetchall()
    conn.close()

    return render_template(
        "admin_section_search_results.html",
        search_type="Section",
        books_data=books_data,
    )


# SEARCH BASED ON SECTION
@app.route("/user_dashboard/section_search_results", methods=["GET", "POST"])
def section_search_results():
    # Fetch books based on section search criteria
    section_search = request.args.get("section_search")

    conn = sqlite3.connect(app.config["DATABASE"])
    cursor = conn.cursor()

    cursor.execute(
        "SELECT section_id FROM sections WHERE section_name = ?", (section_search,)
    )
    section_id = cursor.fetchone()[0]

    cursor.execute(
        "SELECT * FROM books WHERE section_id=?",
        (section_id,),
    )
    books_data = cursor.fetchall()
    conn.close()

    return render_template(
        "section_search_results.html",
        search_type="Section",
        books_data=books_data,
    )


# SEARCH BASED ON AUTHOR (ADMIN)
@app.route("/admin_dashboard/admin_author_search_results", methods=["GET", "POST"])
def admin_author_search_results():
    # Fetch products based on author search criteria
    admin_author_search = request.args.get("admin_author_search")

    conn = sqlite3.connect(app.config["DATABASE"])
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM books WHERE book_author = ?", (admin_author_search,))
    books_data = cursor.fetchall()
    conn.close()

    return render_template(
        "admin_author_search_results.html",
        search_type="Author",
        books_data=books_data,
    )


# SEARCH BASED ON AUTHOR (USER)
@app.route("/user_dashboard/author_search_results", methods=["GET", "POST"])
def author_search_results():
    # Fetch products based on author search criteria
    author_search = request.args.get("author_search")

    conn = sqlite3.connect(app.config["DATABASE"])
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM books WHERE book_author = ?", (author_search,))
    books_data = cursor.fetchall()
    conn.close()

    return render_template(
        "author_search_results.html",
        search_type="Author",
        books_data=books_data,
    )


# BUY BOOK
@app.route("/user_dashboard/buy_book/<int:book_id>", methods=["GET", "POST"])
def buy_book(book_id):
    if "username" in session and session["usertype"] == "user":
        conn = sqlite3.connect(app.config["DATABASE"])
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM books WHERE book_id = ?", (book_id,))
        book_data = cursor.fetchone()

        if request.method == "POST":
            user_name = session["username"]
            payment = request.form["payment"]
            payment = int(payment)

            if book_data[4] > payment:
                return render_template("insufficient_amount.html")
            else:
                return render_template(
                    "book_purchased.html", user_name=user_name, book_data=book_data
                )

        return render_template("buy_book.html", book_data=book_data)

    else:
        return redirect("/user_dashboard")


if __name__ == "__main__":
    app.run(debug=True)
