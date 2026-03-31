from flask import Flask, render_template, request, redirect, session
import mysql.connector
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

# ================= DATABASE CONNECTION =================
connection = mysql.connector.connect(
    host="localhost",
    user="hello",          # change if needed
    password="Google123",  # change if needed
    database="Railway"
)
cursor = connection.cursor(dictionary=True)

# ================= HOME =================
@app.route("/")
def home():
    return render_template("home.html")

# ================= REGISTER =================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user_id = request.form["user_id"]
        password = request.form["password"]
        fname = request.form["first_name"]
        lname = request.form["last_name"]
        email = request.form["email"]

        cursor.execute("""
        INSERT INTO USERS (user_id, password, first_name, last_name, email)
        VALUES (%s,%s,%s,%s,%s)
        """, (user_id, password, fname, lname, email))

        connection.commit()
        return redirect("/login")

    return render_template("register.html")

# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_id = request.form["user_id"]
        password = request.form["password"]

        cursor.execute("""
        SELECT * FROM USERS 
        WHERE user_id=%s AND password=%s
        """, (user_id, password))

        user = cursor.fetchone()

        if user:
            session["user_id"] = user_id
            return redirect("/dashboard")
        else:
            return "Invalid credentials"

    return render_template("login.html")

# ================= DASHBOARD =================
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    return render_template("dashboard.html")

# ================= SEARCH TRAINS =================
@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        source = request.form["source"]
        destination = request.form["destination"]

        cursor.execute("""
        SELECT * FROM TRAIN 
        WHERE source=%s AND destination=%s
        """, (source, destination))

        trains = cursor.fetchall()
        return render_template("search.html", trains=trains)

    return render_template("search.html")

# ================= BOOK TICKET =================
@app.route("/book/<int:train_no>", methods=["GET", "POST"])
def book(train_no):
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        passengers = int(request.form["passengers"])

        # Generate IDs
        ticket_id = int(datetime.now().timestamp())
        payment_id = ticket_id + 1

        # Insert ticket
        cursor.execute("""
        INSERT INTO TICKET (ticket_id, status, no_of_passengers, user_id)
        VALUES (%s,%s,%s,%s)
        """, (ticket_id, "Confirmed", passengers, session["user_id"]))

        # Insert passengers
        for i in range(passengers):
            name = request.form[f"name{i}"]
            gender = request.form[f"gender{i}"]
            pid = ticket_id + i

            cursor.execute("""
            INSERT INTO PASSENGER 
            (passenger_id, name, gender, reservation_status, ticket_id)
            VALUES (%s,%s,%s,%s,%s)
            """, (pid, name, gender, "Confirmed", ticket_id))

        # Insert payment
        cursor.execute("""
        INSERT INTO PAYMENT 
        (payment_id, payment_mode, status, pay_date, ticket_id, amount)
        VALUES (%s,%s,%s,%s,%s,%s)
        """, (payment_id, "UPI", "Success", datetime.now(), ticket_id, 500))

        connection.commit()

        return redirect("/dashboard")

    return render_template("book.html", train_no=train_no)

# ================= VIEW TICKETS =================
@app.route("/tickets")
def tickets():
    if "user_id" not in session:
        return redirect("/login")

    cursor.execute("""
    SELECT * FROM TICKET WHERE user_id=%s
    """, (session["user_id"],))

    tickets = cursor.fetchall()
    return render_template("tickets.html", tickets=tickets)
# ================= update profile =================
@app.route("/update_profile", methods=["GET", "POST"])
def update_profile():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        fname = request.form["first_name"]
        lname = request.form["last_name"]

        cursor.execute("""
        UPDATE USERS 
        SET first_name=%s, last_name=%s
        WHERE user_id=%s
        """, (fname, lname, session["user_id"]))

        connection.commit()
        return redirect("/dashboard")

    return render_template("update_profile.html")
# ================= delete feature=================
@app.route("/delete_ticket/<int:ticket_id>")
def delete_ticket(ticket_id):
    if "user_id" not in session:
        return redirect("/login")

    # delete related records first (important due to foreign keys)
    cursor.execute("DELETE FROM PAYMENT WHERE ticket_id=%s", (ticket_id,))
    cursor.execute("DELETE FROM PASSENGER WHERE ticket_id=%s", (ticket_id,))
    cursor.execute("DELETE FROM TICKET WHERE ticket_id=%s", (ticket_id,))

    connection.commit()

    return redirect("/tickets")

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)