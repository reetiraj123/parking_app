from flask import Blueprint, render_template, request, redirect, url_for
from sqlalchemy.orm import joinedload
from models.models import db, ParkingLot, ParkingSpot, User, Reservation, spot_status  

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Dashboard
@admin_bp.route('/dashboard')
def dashboard():
    lots = ParkingLot.query.options(joinedload(ParkingLot.spots)).all()

    # Join reservations, spot, and lot table for user detail section
    users = User.query.options(
        joinedload(User.reservations)
        .joinedload(Reservation.spot)
        .joinedload(ParkingSpot.lot)
    ).all()

    total_spots = {lot.id: len(lot.spots) for lot in lots}
    available_spots = {
        lot.id: len([s for s in lot.spots if s.status == spot_status.AVAILABLE]) for lot in lots
    }
    occupied_spots = {
        lot.id: len([s for s in lot.spots if s.status == spot_status.OCCUPIED]) for lot in lots
    }

    # Attach latest active reservation user info
    for user in users:
        user.reservation = next(
            (r for r in sorted(user.reservations, key=lambda x: x.start_time, reverse=True)
             if r.end_time is None),
            None
        )

    return render_template(
        'admin/admin_dashboard.html',
        lots=lots,
        users=users,
        total_spots=total_spots,
        available_spots=available_spots,
        occupied_spots=occupied_spots
    )

#  Create Parking Lot 
@admin_bp.route("/create", methods=["POST"])
def create_lot():
    location_name = request.form.get("location_name")
    price = float(request.form.get("price"))
    spot_count = int(request.form.get("spot_count"))
    address = request.form.get("address")
    pin_code = request.form.get("pin_code")

    lot = ParkingLot(
        location_name=location_name,
        price=price,
        address=address,
        pin_code=pin_code,
        max_number_of_spots=spot_count
    )

    db.session.add(lot)
    db.session.flush()

    for i in range(1, spot_count + 1):
        spot = ParkingSpot(
            lot_id=lot.id,
            status=spot_status.AVAILABLE,
            spot_number=i
        )
        db.session.add(spot)
    db.session.commit()

    return redirect(url_for("admin.dashboard"))

#  Edit Parking Lot
@admin_bp.route("/edit/<int:lot_id>", methods=["POST"])
def edit_lot(lot_id):
    lot = ParkingLot.query.options(joinedload(ParkingLot.spots)).get_or_404(lot_id)
    lot.location_name = request.form.get("location_name")
    lot.price = float(request.form.get("price"))
    new_spot_count = int(request.form.get("spot_count"))

    existing_spot_count = len(lot.spots)

    if new_spot_count > existing_spot_count:
        for i in range(existing_spot_count + 1, new_spot_count + 1):
            new_spot = ParkingSpot(
                lot_id=lot.id,
                status=spot_status.AVAILABLE,
                spot_number=i
            )
            db.session.add(new_spot)
    elif new_spot_count < existing_spot_count:
        available_spots = [s for s in lot.spots if s.status == spot_status.AVAILABLE]
        to_remove = existing_spot_count - new_spot_count
        if len(available_spots) >= to_remove:
            for spot in available_spots[:to_remove]:
                db.session.delete(spot)
        else:
            return redirect(url_for("admin.dashboard"))

    lot.max_number_of_spots = new_spot_count
    db.session.commit()
    return redirect(url_for("admin.dashboard"))

#  Delete Parking Lot 
@admin_bp.route("/delete/<int:lot_id>", methods=["POST"])
def delete_lot(lot_id):
    lot = ParkingLot.query.options(joinedload(ParkingLot.spots)).get_or_404(lot_id)
    if any(s.status == spot_status.OCCUPIED for s in lot.spots):
        return redirect(url_for("admin.dashboard"))

    for spot in lot.spots:
        db.session.delete(spot)

    db.session.delete(lot)
    db.session.commit()
    return redirect(url_for("admin.dashboard"))


#  Summary Chart
@admin_bp.route("/summary")
def summary():
    lots = ParkingLot.query.options(joinedload(ParkingLot.spots)).all()

    lot_labels = [lot.location_name for lot in lots]
    lot_occupied = [len([s for s in lot.spots if s.status == spot_status.OCCUPIED]) for lot in lots]
    lot_available = [len([s for s in lot.spots if s.status == spot_status.AVAILABLE]) for lot in lots]

    return render_template(
        "admin/admin_summary.html",
        labels=lot_labels,
        occupied=lot_occupied,
        available=lot_available
    )
