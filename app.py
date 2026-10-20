from flask import Flask, render_template, request, g, session, redirect, url_for, flash
from database import get_db, close_db
from forms import SearchForm, BookingForm, RegistrationForm, DateFilterForm, AdminLoginForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps
import random

"""
My system has two kinds of user: regular ones, and administrators.
Choose Register on the main page in order to register as a regular user.
But to login as an administrator, the user name is Exzy and the password is 125348816.
#1.Index page #2.datetime manipulation #3.admin protection decorator 
#4.search movie #5.filter showtimes #6.unique movie #7.unique booking
#8.bookings cart #9.User Login #10.User Logout #11.admin login #12.admin logout #13.admin dashboard
#14.register #15.delete unique booking #16. #delete all bookings
"""

app = Flask(__name__)
app.config["SECRET_KEY"] = "this-is-my-secret-key"
app.teardown_appcontext(close_db)


@app.route("/")
def index():
    db = get_db()
    today, next_week = get_date_range()
    all_showtimes = db.execute("""SELECT m.id, m.title, m.price, m.poster_url, s.show_time, s.id AS showtime_id
        FROM movies m JOIN showtimes s ON m.id = s.movie_id ORDER BY s.show_time, m.title""").fetchall()
    movies = []
    for show in all_showtimes:
        show_date = given_random_date(show["showtime_id"])
        available = get_available_seats(show["showtime_id"])
        if today <= show_date <= next_week:
            movies.append({"id": show["id"],
                "title": show["title"],
                "price": show["price"],
                "child_price": show["price"] / 2,
                "show_date": show_date,
                "show_time": show["show_time"],
                "showtime_id": show["showtime_id"],
                "available_seats": available,
                "poster_url": show["poster_url"]})
    movies.sort(key=sort_by_date_time)
    return render_template("index.html", movies=movies, today=today, next_week=next_week)

'''https://flask.palletsprojects.com/en/stable/api/#flask.Flask.permanent_session_lifetime'''
app.permanent_session_lifetime = timedelta(minutes=30)

@app.before_request
def make_session_permanent():
    session.permanent = True

def get_date_range():
    today = datetime.now().date()
    next_week = today + timedelta(days=7)
    return today, next_week

def get_available_seats(showtime_id):
    db = get_db()
    booked = db.execute(
        """SELECT SUM(total_seats) as total FROM bookings WHERE showtime_id=?""",
        (showtime_id,)).fetchone()
    booked_seats = booked["total"] if booked["total"] else 0
    return max(0, 50 - booked_seats)

def given_random_date(showtime_id):
    today = datetime.now().date()
    rng = random.Random(showtime_id)
    random_days = rng.randint(0, 7)
    return today + timedelta(days=random_days)

def sort_by_date_time(item):
    return (item["show_date"], item["show_time"])
def sort_by_time(item):
    return item["show_time"]

'''https://flask.palletsprojects.com/en/stable/tutorial/views/#require-authentication-in-other-views'''
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin" not in session:
            flash("Admin access required")
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/search_movies", methods=["GET", "POST"])
def search_movies():
    form = SearchForm()
    results = None
    if form.validate_on_submit():
        title = form.title.data
        db = get_db()
        results = db.execute("""SELECT * FROM movies WHERE title LIKE ?;""", ('%' + title + '%',)).fetchall()
    return render_template("search_results.html", form=form, results=results)

@app.route("/filter_showtimes", methods=["GET", "POST"])
def filter_showtimes():
    form = DateFilterForm()
    results = None
    if form.validate_on_submit():
        chosen_date = form.show_date.data
        db = get_db()
        showtimes = db.execute("""SELECT s.id, s.show_time, s.movie_id, m.title
            FROM showtimes s
            JOIN movies m ON s.movie_id = m.id""").fetchall()
        results = []
        for showtime in showtimes:
            show_date = given_random_date(showtime["id"])
            available = get_available_seats(showtime["id"])
            if show_date == chosen_date:
                results.append({
                    "id": showtime["id"],
                    "title": showtime["title"],
                    "show_date": show_date,
                    "show_time": showtime["show_time"],
                    "available_seats": available
                })
        results.sort(key=sort_by_time)
    return render_template("filter_showtimes.html", form=form, results=results)


@app.route("/movie/<int:movie_id>")
def movie(movie_id):
    db = get_db()
    movie = db.execute(
        "SELECT * FROM movies WHERE id=?;",
        (movie_id,)
    ).fetchone()
    all_showtimes = db.execute("""SELECT * FROM showtimes WHERE movie_id=? ORDER BY show_time;""",
        (movie_id,)).fetchall()
    showtimes = []
    for show in all_showtimes:
        show_date = given_random_date(show["id"])
        available = get_available_seats(show["id"])
        showtimes.append({
            "id": show["id"],
            "show_date": show_date,
            "show_time": show["show_time"],
            "available_seats": available})
    showtimes.sort(key=sort_by_date_time)
    return render_template("movie.html", movie=movie, showtimes=showtimes)

@app.route("/book/<int:showtime_id>", methods=["GET", "POST"])
def book(showtime_id):
    if "user_id" not in session:
        flash("Please login first")
        session['next_url'] = url_for('book', showtime_id=showtime_id)
        return redirect(url_for("login"))

    db = get_db()
    showtime = db.execute("""SELECT s.*, m.title, m.price, m.description, m.poster_url FROM showtimes s
        JOIN movies m ON s.movie_id = m.id
        WHERE s.id=?;""", (showtime_id,)).fetchone()
    available_seats = get_available_seats(showtime_id)
    if available_seats <= 0:
        flash("Sold out!")
        return redirect(url_for("movie", movie_id=showtime["movie_id"]))
    form = BookingForm()
    show_date = given_random_date(showtime_id)
    if form.validate_on_submit():
        adult = form.adult_seats.data
        child = form.child_seats.data
        if child > 0 and adult == 0:
            flash("Children must be accompanied by an adult")
            return redirect(url_for("book", showtime_id=showtime_id))

        total_seats = adult + child
        if total_seats > available_seats:
            flash("Not enough seats available")
            return redirect(url_for("book", showtime_id=showtime_id))

        db.execute("""INSERT INTO bookings(showtime_id, user_id, adult_seats, child_seats, total_seats, booking_date)
            VALUES (?, ?, ?, ?, ?, ?)""", (showtime_id,
            session["user_id"],
            adult,
            child,
            total_seats,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        db.commit()
        booking = {
            "adult_seats": adult,
            "child_seats": child,
            "total": (adult * showtime["price"]) + (child * (showtime["price"] / 2))}
        return render_template("confirmation.html",
            movie=showtime,
            showtime=showtime,
            booking=booking,
            show_date=show_date)

    return render_template("booking.html",
        form=form,
        showtime=showtime,
        available_seats=available_seats,
        show_date=show_date)

@app.route("/my_bookings")
def my_bookings():
    if "user_id" not in session:
        flash("Please login first")
        return redirect(url_for("login", next=request.url))

    db = get_db()
    bookings = db.execute("""SELECT b.*, m.title, m.price, m.description, m.poster_url, s.show_time, s.id as showtime_id
        FROM bookings b
        JOIN showtimes s ON b.showtime_id = s.id
        JOIN movies m ON s.movie_id = m.id
        WHERE b.user_id = ?
        ORDER BY b.booking_date DESC;""", (session["user_id"],)).fetchall()

    result = []
    for booking in bookings:
        show_date = given_random_date(booking["showtime_id"])
        total_cost = (booking["adult_seats"] * booking["price"]) + (booking["child_seats"] * (booking["price"] / 2))
        result.append({"id": booking["id"],
            "showtime_id": booking["showtime_id"],
            "title": booking["title"],
            "description": booking["description"],
            "poster_url": booking["poster_url"],
            "show_date": show_date,
            "show_time": booking["show_time"],
            "adult_seats": booking["adult_seats"],
            "child_seats": booking["child_seats"],
            "total_seats": booking["total_seats"],
            "total_cost": round(total_cost, 2),
            "booking_date": booking["booking_date"]})
    return render_template("my_bookings.html", bookings=result)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db = get_db()
        user = db.execute("""SELECT * FROM users WHERE user_id=?""",
            (form.user_id.data,) ).fetchone()
        if user and check_password_hash(user["password"], form.password.data):
            session["user_id"] = user["user_id"]
            next_url = session.pop('next_url', None)
            if next_url:
                return redirect(next_url)
            return redirect(url_for("index"))
        flash("Invalid")
    return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out")
    return redirect(url_for("index"))

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    form = AdminLoginForm()
    if form.validate_on_submit():
        db = get_db()
        admin = db.execute(
            """SELECT * FROM admins WHERE admin_id=?""",
            (form.admin_id.data,)).fetchone()
        if admin and check_password_hash(admin["password"], form.password.data):
            session["admin"] = True
            flash("Admin login successful")
            return redirect(url_for("admin_dashboard"))
        flash("Invalid admin credentials")
    return render_template("admin_login.html", form=form)

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    flash("Admin logged out")
    return redirect(url_for("index"))

@app.route("/admin/dashboard", methods=["GET", "POST"])
@admin_required
def admin_dashboard():
    db = get_db()
    if request.method == "POST":
        action = request.form.get("action")
        if action == "add_movie":
            db.execute("""INSERT INTO movies (title, genre, description, duration, rating, price)
                VALUES (?, ?, ?, ?, ?, ?)""", (
                request.form["title"],
                request.form["genre"],
                request.form["description"],
                request.form["duration"],
                request.form["rating"],
                request.form["price"]))
            db.commit()
            flash("Movie added")
        elif action == "add_showtime":
            db.execute("""
                INSERT INTO showtimes (movie_id, show_time)
                VALUES (?, ?)""", (
                request.form["movie_id"],
                request.form["show_time"] ))
            db.commit()
            flash("Showtime added")
        elif action == "delete_movie":
            db.execute("""DELETE FROM showtimes WHERE movie_id=?""", (request.form["movie_id"],))
            db.execute("""DELETE FROM movies WHERE id=?""", (request.form["movie_id"],))
            db.commit()
            flash("Movie deleted")
        elif action == "delete_showtime":
            db.execute("""DELETE FROM showtimes WHERE id=?""", (request.form["showtime_id"],))
            db.commit()
            flash("Showtime deleted")

    movies = db.execute("""SELECT * FROM movies""").fetchall()
    raw_showtimes = db.execute("""SELECT s.*, m.title FROM showtimes s
        JOIN movies m ON s.movie_id = m.id
        ORDER BY s.show_time""").fetchall()
    showtimes = []
    for show in raw_showtimes:
        showtimes.append({
            "id": show["id"],
            "movie_id": show["movie_id"],
            "title": show["title"],
            "show_time": show["show_time"],
            "show_date": given_random_date(show["id"])})
    return render_template("admin_dashboard.html", movies=movies, showtimes=showtimes)

@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        db = get_db()
        existing = db.execute(
            """SELECT * FROM users WHERE user_id = ?""", 
            (form.user_id.data,)
        ).fetchone()
        if existing:
            flash("Username already taken. Please choose another, or else Please Log in.")
            return render_template("register.html", form=form)
        hashed_password = generate_password_hash(form.password.data)
        db.execute("""INSERT INTO users (user_id, password)
            VALUES (?, ?)""", (form.user_id.data, hashed_password))
        db.commit()
        flash("Registration successful. Please login.")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)
def cleanup():
    db = get_db()
    today = datetime.now().date()
    showtimes = db.execute("""SELECT s.id, m.title, s.show_time FROM showtimes s
        JOIN movies m ON s.movie_id = m.id""").fetchall()
    for showtime in showtimes:
        show_date = given_random_date(showtime["id"])
        if show_date < today:
            db.execute("""SELECT DISTINCT user_id FROM bookings WHERE showtime_id=?""", (showtime["id"],)).fetchall()
            db.execute(
                """DELETE FROM bookings WHERE showtime_id=?""",
                (showtime["id"],) )
            db.commit()
    
@app.route("/delete_booking/<int:booking_id>", methods=["POST"])
def delete_booking(booking_id):
    if "user_id" not in session:
        flash("Please login first")
        return redirect(url_for("login"))
    db = get_db()
    booking = db.execute(
        """SELECT * FROM bookings WHERE id=? AND user_id=?""",
        (booking_id, session["user_id"])).fetchone()
    if booking:
        db.execute("""DELETE FROM bookings WHERE id=?""",
            (booking_id,))
        db.commit()
        flash("Booking cancelled.")
    else:
        flash("Booking not found.")
    return redirect(url_for("my_bookings"))

@app.route("/clear_all_bookings", methods=["POST"])
def clear_all_bookings():
    if "user_id" not in session:
        flash("Please login first")
        return redirect(url_for("login"))
    db = get_db()
    db.execute("""DELETE FROM bookings WHERE user_id=?""",
        (session["user_id"],))
    db.commit()
    flash("All bookings cancelled successfully.")
    return redirect(url_for("my_bookings"))

