
USE Railway;

-- ================= USERS =================
CREATE TABLE USERS (
    user_id INT PRIMARY KEY,
    password VARCHAR(50),
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    address VARCHAR(100),
    contact VARCHAR(15),
    email VARCHAR(100) UNIQUE,
    aadhar_no VARCHAR(20) UNIQUE,
    age INT,
    gender VARCHAR(10),
    sec_que VARCHAR(100),
    sec_ans VARCHAR(100)
);


-- ================= STATION =================
CREATE TABLE STATION (
    station_id INT PRIMARY KEY,
    name VARCHAR(100)
);

INSERT INTO STATION VALUES 
(1,'Chennai'),
(2,'Bangalore'),
(3,'Mumbai'),
(4,'Delhi');


-- ================= TRAIN =================
CREATE TABLE TRAIN (
    train_no INT PRIMARY KEY,
    name VARCHAR(100),
    source VARCHAR(50),
    destination VARCHAR(50),
    arrival_time DATETIME,
    departure_time DATETIME
);

INSERT INTO TRAIN VALUES 
(101,'Chennai Express','Chennai','Mumbai','2026-03-10 20:00:00','2026-03-10 20:15:00'),
(102,'Delhi Express','Delhi','Bangalore','2026-03-11 18:00:00','2026-03-11 18:30:00');


-- ================= TRAIN SCHEDULE =================
CREATE TABLE TRAIN_SCHEDULE (
    train_no INT,
    travel_date DATE,
    seats_available INT,
    PRIMARY KEY (train_no, travel_date),
    FOREIGN KEY (train_no) REFERENCES TRAIN(train_no)
);

INSERT INTO TRAIN_SCHEDULE VALUES 
(101,'2026-03-10',200),
(102,'2026-03-11',150);


-- ================= TRAIN STATUS =================
CREATE TABLE TRAIN_STATUS (
    train_no INT PRIMARY KEY,
    avail_seats INT,
    booked_seats INT,
    waiting INT,
    fare DECIMAL(10,2),
    FOREIGN KEY (train_no) REFERENCES TRAIN(train_no)
);

INSERT INTO TRAIN_STATUS VALUES 
(101,200,0,0,750.00),
(102,150,0,0,900.00);


-- ================= TRAIN STARTS =================
CREATE TABLE TRAIN_STARTS (
    train_no INT PRIMARY KEY,
    station_id INT,
    departure_time DATETIME,
    FOREIGN KEY (train_no) REFERENCES TRAIN(train_no),
    FOREIGN KEY (station_id) REFERENCES STATION(station_id)
);

INSERT INTO TRAIN_STARTS VALUES 
(101,1,'2026-03-10 20:15:00'),
(102,4,'2026-03-11 18:30:00');


-- ================= TRAIN STOPS =================
CREATE TABLE TRAIN_STOPS (
    train_no INT,
    station_id INT,
    arrival_time DATETIME,
    halt INT,
    PRIMARY KEY (train_no, station_id),
    FOREIGN KEY (train_no) REFERENCES TRAIN(train_no),
    FOREIGN KEY (station_id) REFERENCES STATION(station_id)
);

INSERT INTO TRAIN_STOPS VALUES 
(101,1,'2026-03-10 20:00:00',10),
(101,2,'2026-03-10 23:00:00',15),
(101,3,'2026-03-11 08:00:00',20),
(102,4,'2026-03-11 18:00:00',10),
(102,2,'2026-03-12 05:00:00',15);


-- ================= TICKET =================
CREATE TABLE TICKET (
    ticket_id INT PRIMARY KEY,
    status VARCHAR(20),
    no_of_passengers INT,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES USERS(user_id)
);



-- ================= PASSENGER =================
CREATE TABLE PASSENGER (
    passenger_id INT PRIMARY KEY,
    name VARCHAR(100),
    gender VARCHAR(10),
    reservation_status VARCHAR(20),
    ticket_id INT,
    FOREIGN KEY (ticket_id) REFERENCES TICKET(ticket_id)
);



-- ================= PAYMENT =================
CREATE TABLE PAYMENT (
    payment_id INT PRIMARY KEY,
    payment_mode VARCHAR(20),
    status VARCHAR(20),
    pay_date DATE,
    ticket_id INT,
    amount DECIMAL(10,2),
    FOREIGN KEY (ticket_id) REFERENCES TICKET(ticket_id)
);



-- ================= SEAT =================
CREATE TABLE SEAT (
    seat_id INT PRIMARY KEY,
    coach VARCHAR(10),
    seat_number INT,
    type VARCHAR(20),
    train_no INT,
    FOREIGN KEY (train_no) REFERENCES TRAIN(train_no)
);

INSERT INTO SEAT VALUES 
(1,'S1',12,'Sleeper',101),
(2,'A1',5,'AC',102);


-- ================= SEAT ASSIGN =================
CREATE TABLE SEAT_ASSIGN (
    seat_id INT,
    passenger_id INT,
    availability VARCHAR(20),
    PRIMARY KEY (seat_id, passenger_id),
    FOREIGN KEY (seat_id) REFERENCES SEAT(seat_id),
    FOREIGN KEY (passenger_id) REFERENCES PASSENGER(passenger_id)
);

