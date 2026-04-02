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
SELECT t.train_no, t.name, t.source, t.destination,
       ts.seats_available, st.fare
FROM TRAIN t
JOIN TRAIN_SCHEDULE ts ON t.train_no = ts.train_no
JOIN TRAIN_STATUS st ON t.train_no = st.train_no
WHERE t.source=%s AND t.destination=%s
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

        ticket_id = int(datetime.now().timestamp())
        payment_id = ticket_id + 1
        cursor.execute("""
INSERT INTO TICKET (ticket_id, status, no_of_passengers, user_id)
VALUES (%s,%s,%s,%s)
""", (ticket_id, "Confirmed", passengers, session["user_id"]))

        passenger_ids = []

        # Insert passengers
        for i in range(passengers):
            name = request.form[f"name{i}"]
            gender = request.form[f"gender{i}"]
            pid = ticket_id + i

            passenger_ids.append(pid)

            cursor.execute("""
            INSERT INTO PASSENGER 
            (passenger_id, name, gender, reservation_status, ticket_id)
            VALUES (%s,%s,%s,%s,%s)
            """, (pid, name, gender, "Confirmed", ticket_id))

        # Assign seat for EACH passenger
        for pid in passenger_ids:
            cursor.execute("""
            SELECT s.seat_id 
            FROM SEAT s
            LEFT JOIN SEAT_ASSIGN sa ON s.seat_id = sa.seat_id
            WHERE sa.seat_id IS NULL AND s.train_no=%s
            LIMIT 1
            """, (train_no,))

            seat = cursor.fetchone()

            if seat:
                cursor.execute("""
                INSERT INTO SEAT_ASSIGN (seat_id, passenger_id, availability)
                VALUES (%s,%s,%s)
                """, (seat["seat_id"], pid, "Booked"))
            else:
                print("No seats available")

        cursor.execute("""
UPDATE TRAIN_STATUS
SET booked_seats = booked_seats + %s,
    avail_seats = avail_seats - %s
WHERE train_no = %s
""", (passengers, passengers, train_no))

        connection.commit()

        return redirect("/tickets")

    return render_template("book.html", train_no=train_no)


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

    cursor.execute("""
    DELETE FROM SEAT_ASSIGN 
    WHERE passenger_id IN (
        SELECT passenger_id FROM PASSENGER WHERE ticket_id=%s
    )
    """, (ticket_id,))

    cursor.execute("DELETE FROM PAYMENT WHERE ticket_id=%s", (ticket_id,))
    cursor.execute("DELETE FROM PASSENGER WHERE ticket_id=%s", (ticket_id,))
    cursor.execute("DELETE FROM TICKET WHERE ticket_id=%s", (ticket_id,))
    cursor.execute("""
UPDATE TRAIN_STATUS
SET booked_seats = booked_seats - 1,
    avail_seats = avail_seats + 1
WHERE train_no = (
    SELECT s.train_no
    FROM SEAT_ASSIGN sa
    JOIN SEAT s ON sa.seat_id = s.seat_id
    WHERE sa.passenger_id IN (
        SELECT passenger_id FROM PASSENGER WHERE ticket_id=%s
    )
    LIMIT 1
)
""", (ticket_id,))

    connection.commit()

    return redirect("/tickets")

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ================= Payement =================
@app.route('/payment/<int:ticket_id>', methods=['GET','POST'])
def payment(ticket_id):
    if request.method == 'POST':
        mode = request.form['mode']

        cursor.execute("""
        INSERT INTO PAYMENT 
        (payment_id, payment_mode, status, pay_date, ticket_id, amount)
        VALUES (%s,%s,%s,%s,%s,%s)
        """, (
            int(datetime.now().timestamp()),
            mode,
            "Success",
            datetime.now(),
            ticket_id,
            500
        ))

        connection.commit()

        return redirect("/tickets")

    return render_template("payment.html", ticket_id=ticket_id)

@app.route("/tickets")
def tickets():
    if "user_id" not in session:
        return redirect("/login")
    
    cursor.execute("""
SELECT t.ticket_id, t.status, t.no_of_passengers,
       GROUP_CONCAT(s.seat_number) AS seat_number,
       MAX(p.status) AS payment_status,
       MAX(tr.name) AS train_name,
       MAX(tr.source) AS source,
       MAX(tr.destination) AS destination

FROM TICKET t

LEFT JOIN PASSENGER pa ON t.ticket_id = pa.ticket_id
LEFT JOIN SEAT_ASSIGN sa ON pa.passenger_id = sa.passenger_id
LEFT JOIN SEAT s ON sa.seat_id = s.seat_id
LEFT JOIN TRAIN tr ON s.train_no = tr.train_no
LEFT JOIN PAYMENT p ON t.ticket_id = p.ticket_id

WHERE t.user_id = %s

GROUP BY t.ticket_id
""", (session["user_id"],))

    tickets = cursor.fetchall()
    return render_template("tickets.html", tickets=tickets)

@app.route('/route/<int:train_no>')
def route(train_no):
    cursor.execute("""
        SELECT s.name, ts.arrival_time, ts.halt
        FROM TRAIN_STOPS ts
        JOIN STATION s ON ts.station_id = s.station_id
        WHERE ts.train_no = %s
    """, (train_no,))

    route = cursor.fetchall()
    return render_template("route.html", route=route, train_no=train_no)

@app.route('/status')
def status():
    cursor.execute("""
        SELECT t.train_no, t.name, ts.avail_seats, ts.booked_seats, ts.waiting, ts.fare
        FROM TRAIN_STATUS ts
        JOIN TRAIN t ON ts.train_no = t.train_no
    """)
    
    data = cursor.fetchall()
    return render_template("status.html", data=data)

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)

