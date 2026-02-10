#  Vehicle Parking Management System

A web-based parking management application built using **Flask**, **SQLite**, and **HTML & CSS**. This system allows users to book and vacate parking spots, while admins can manage parking lots, view occupancy, and analyze usage statistics.

---

##  Features

### User Side
- User Registration and Login
- Token-based authentication
- Dashboard showing available lots and active reservations
- Book a parking spot (auto-allotment)
- Vacate a spot with cost calculation
- View usage summary (with charts)

###  Admin Side
- Login using default credentials
- Dashboard with:
  - Parking lot management (Create, Edit, Delete)
  - Spot availability and occupancy data
  - Registered user and vehicle details
- Spot detail view
- Visual summary of lot utilization

---

# Database Models Overview

- **Admin:** Manages admin login and authentication.
- **User:** Handles user registration, login, and reservations.
- **ParkingLot:** Stores parking lot details.
- **ParkingSpot:** Stores individual spot status and lot association.
- **Reservation:** Tracks user reservations, timings, and cost.

# Database Models Overview


## Project Structure

APP_24F1000182/
├── controller/
│   ├── admin_controller.py
│   └── user_controller.py
├── instance/
│   └── database.db
├── models/
│   └── models.py
├── static/
│   ├── css/
│   │   ├── admin_dashboard.css
│   │   ├── landing.css
│   │   ├── login.css
│   │   ├── sign.css
│   │   └── user_dashboard.css
│   └── images
├── templates/
│   ├── admin/
│   │   ├── admin_dashboard.html
│   │   └── admin_summary.html
│   └── user/
│   │   ├── user_dashboard.html
│   │   └── user_summary.html
│   ├── landing.html
│   ├── login.html
│   └── signup.html
├── app.py
├── readme.md
└── token_utils.py



## Tech Stack

- **Python 3**
- **Flask**
- **Flask-SQLAlchemy**
- **Jinja2**
- **HTML/CSS**
- **SQLite** (as database)
- **ZoneInfo** (for timezone support)

---

## Future Improvements

- More Secure Login system
- User/admin session-based login
- API endpoints for mobile app support
- Parking history export
- SMS/email notifications
- Add more admins


