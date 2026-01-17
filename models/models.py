from datetime import datetime
from enum import Enum 
from zoneinfo import ZoneInfo
from token_utils import generate_token 


from flask_sqlalchemy import SQLAlchemy


db: SQLAlchemy=SQLAlchemy()
IST=ZoneInfo("Asia/Kolkata")

# Set Symbol for avalable or occupied
class spot_status(str, Enum):
    AVAILABLE = "A"
    OCCUPIED = "O"


# Admin model
class Admin(db.Model):
    __tablename__ = "admins"
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role     = db.Column(db.String(20), default="admin")
    token    = db.Column(db.String(64), unique=True, nullable=False)

# User model
class User(db.Model):
    __tablename__ = "users"
    id          = db.Column(db.Integer, primary_key=True)
    user_name   = db.Column(db.String(120), unique=True, nullable=False)
    full_name   = db.Column(db.String(120), nullable=False)
    password    = db.Column(db.String(256), nullable=False)
    role        = db.Column(db.String(20), default="user")
    token       = db.Column(db.String(64), unique=True, nullable=False)
    created_time = db.Column(db.DateTime, default=lambda: datetime.now(IST))

    reservations = db.relationship(
        "Reservation", back_populates="user", cascade="all, delete-orphan"
    )
    
# Parking lot model
class ParkingLot(db.Model):
    __tablename__ = "parking_lots"
    id = db.Column(db.Integer, primary_key=True)
    location_name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(255), nullable=False)  
    pin_code = db.Column(db.String(10), nullable=False)
    max_number_of_spots = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(IST))

    spots = db.relationship(
        "ParkingSpot", back_populates="lot", cascade="all, delete-orphan"
    )

# Parking spot model
class ParkingSpot(db.Model):
    __tablename__ = "parking_spots"
    id = db.Column(db.Integer, primary_key=True)
    spot_number = db.Column(db.Integer, nullable=False) 
    lot_id = db.Column(db.Integer, db.ForeignKey("parking_lots.id"), nullable=False)
    status = db.Column(db.Enum(spot_status), default=spot_status.AVAILABLE, nullable=False)

    lot = db.relationship("ParkingLot", back_populates="spots")
    reservations = db.relationship(
        "Reservation", back_populates="spot", cascade="all, delete-orphan"
    )


# Reservation model
class Reservation(db.Model):
    __tablename__ = "reservations"
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey("parking_spots.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    vehicle_number = db.Column(db.String(20), nullable=True) 

    start_time = db.Column(db.DateTime, default=lambda: datetime.now(IST))
    end_time = db.Column(db.DateTime, nullable=True)

    cost_per_hour = db.Column(db.Float, nullable=False)
    total_cost = db.Column(db.Float, nullable=True)

    user = db.relationship("User", back_populates="reservations")
    spot = db.relationship("ParkingSpot", back_populates="reservations")


#Set default Admin
DEFAULT_ADMIN_UNAME="tushar"
DEFAULT_ADMIN_PASS="tushar123"

# Insert default admin if not exists
def insert_admin():
    if not Admin.query.filter_by(username=DEFAULT_ADMIN_UNAME).first():
        admin = Admin(
            username=DEFAULT_ADMIN_UNAME,
            password=DEFAULT_ADMIN_PASS,
            token=generate_token() 
        )
        db.session.add(admin)
        db.session.commit()

#Init fucntion to craete database instance
def init_database(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
        insert_admin()






