from flask import Blueprint, render_template, request, redirect, url_for
from models.models import db, User, ParkingLot, ParkingSpot, Reservation
from datetime import datetime
from zoneinfo import ZoneInfo
from collections import defaultdict
from sqlalchemy import func

user_bp = Blueprint("user", __name__, url_prefix="/user")
IST = ZoneInfo("Asia/Kolkata")

# Helper to find token 
def get_user_by_token(token):
    if not token:
        return None
    return User.query.filter_by(token=token).first()

# Dashboard
@user_bp.route('/dashboard')
def dashboard():
    token = request.args.get("token")
    user = get_user_by_token(token)
    if not user:
        return redirect(url_for("login"))

    lots = ParkingLot.query.all()

    parking_lots = []
    for lot in lots:
        total = ParkingSpot.query.filter_by(lot_id=lot.id).count()
        available = ParkingSpot.query.filter_by(lot_id=lot.id, status="AVAILABLE").count()
        parking_lots.append({
            "id": lot.id,
            "location_name": lot.location_name,
            "price": lot.price,
            "available_count": available,
            "total_count": total
        })

    active_reservations = Reservation.query.filter(
        Reservation.user_id == user.id,
        Reservation.end_time.is_(None)
    ).all()

    return render_template(
        "user/user_dashboard.html",
        user=user,
        parking_lots=parking_lots,
        active_reservations=active_reservations
    )

# Book a spot
@user_bp.route("/book/<int:lot_id>", methods=["POST"])
def book(lot_id):
    token = request.args.get("token")
    user = get_user_by_token(token)
    if not user:
        return redirect(url_for("login"))
    vehicle_number = request.form.get("vehicle_number")
    if not vehicle_number:
        return redirect(url_for("user.dashboard", token=token))

    spot = ParkingSpot.query.filter(
        ParkingSpot.lot_id == lot_id,
        func.upper(ParkingSpot.status) == "AVAILABLE"
    ).first()

    if not spot:
        return redirect(url_for("user.dashboard", token=token))

    reservation = Reservation(
        spot_id=spot.id,
        user_id=user.id,
        start_time=datetime.now(IST),
        cost_per_hour=spot.lot.price,
        vehicle_number=vehicle_number  
    )

    spot.status = "OCCUPIED" 
    db.session.add(reservation)
    db.session.commit()

    return redirect(url_for("user.dashboard", token=token))

# Vacate a Spot
@user_bp.route("/vacate/<int:reservation_id>", methods=["POST"])
def vacate(reservation_id):
    token = request.args.get("token")
    user = get_user_by_token(token)
    if not user:
        return redirect(url_for("login"))

    reservation = Reservation.query.get(reservation_id)
    if not reservation or reservation.user_id != user.id:
        return redirect(url_for("user.dashboard", token=token))

    reservation.end_time = datetime.now(IST) 

    # Here we remove timezone info because it can cause error
    start = reservation.start_time.replace(tzinfo=None)
    end = reservation.end_time.replace(tzinfo=None)
    duration = (end - start).total_seconds() / 3600

    reservation.total_cost = round(duration * reservation.cost_per_hour, 2)
    reservation.spot.status = "AVAILABLE"

    db.session.commit()
    return redirect(url_for("user.dashboard", token=token))


@user_bp.route("/summary")
def summary():
    token = request.args.get("token")
    user = get_user_by_token(token)
    if not user:
        return redirect(url_for("login"))

    reservations = Reservation.query.filter(
        Reservation.user_id == user.id,
        Reservation.end_time.isnot(None)
    ).order_by(Reservation.start_time.asc()).all()

    lot_costs = defaultdict(float)
    for r in reservations:
        lot_name = r.spot.lot.location_name
        lot_costs[lot_name] += r.total_cost or 0

    # Round totals only after full accumulation
    lot_costs = {lot: round(cost, 2) for lot, cost in lot_costs.items()}

    chart_labels = list(lot_costs.keys())
    chart_values = list(lot_costs.values())

    return render_template(
        "user/user_summary.html",
        user=user,
        reservations=reservations,
        chart_labels=chart_labels,
        chart_values=chart_values
    )


