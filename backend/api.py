from flask import request, jsonify, current_app as app, make_response
from flask_restful import Api,Resource, fields, marshal_with
from flask_security import auth_required, current_user
from .models import *
from .cache import cache
from datetime import datetime

api = Api()

parking_lot_fields = {
    'id' : fields.Integer,
    'name' : fields.String,
    'location' : fields.String,
    'address' : fields.String,
    'pin_code' : fields.Integer,
    'price' : fields.Float,
    'total_spots' : fields.Integer
}

parking_spot_fields = {
    'id': fields.Integer,
    'status': fields.String,
    'lot_id': fields.Integer
}

user_fields = {
    'id': fields.Integer,
    'email': fields.String,
    'full_name': fields.String,
}

class Lotapi(Resource):
    @auth_required("token")
    @marshal_with(parking_lot_fields)
    def get(self, lot_id):
        lot = Lot.query.get(lot_id)
        return lot if lot else {"message": "Not found"}, 404
    
    @auth_required("token")
    def put(self, lot_id):
        if not is_admin():
            return {"error" : "Only Admin Allowed"}, 403
        
        data = request.get_json()
        lot = Lot.query.get(lot_id)
        if not lot:
            return {"error" : "Lot not found"}, 404
        
        old_count = lot.total_spots
        new_count = data.get('total_spots', old_count)

        lot.name = data.get('name', lot.name)
        lot.location = data.get('location', lot.location)
        lot.address = data.get('address', lot.address)
        lot.pin_code = data.get('pin_code', lot.pin_code)
        lot.price = data.get('price', lot.price)
        lot.total_spots = new_count
        db.session.commit()
        
        if new_count > old_count:
            for i in range(new_count - old_count):
                db.session.add(Spot(lot_id = lot.id, status = "A"))
        elif new_count < old_count:
            removable_spots = Spot.query.filter_by(lot_id = lot.id, status = "A").limit(old_count - new_count).all()
            for spot in removable_spots:
                db.session.delete(spot)
        
        db.session.commit()
        return {"message" : "Lot updated"}

    @auth_required("token")
    def delete(self, lot_id):
        if not is_admin():
            return {"error" : "Only Admin allowed"}, 403
        
        lot = Lot.query.get(lot_id)
        if not lot:
            return {"error": "Lot not found"}, 404
        if any(spot.status == "O" for spot in lot.spots):
            return {"error" : "Spots still occupied"}, 400
        
        Spot.query.filter_by(lot_id = lot.id).delete()
        db.session.delete(lot)
        db.session.commit()
        return {"message" : "Lot deleted"}

class LotListapi(Resource):
    @auth_required("token")
    def get(self):
        if not is_admin():
            return {"error": "Admin only"},403
    
        lots = Lot.query.all()
        result = []

        for lot in lots:
            total = lot.total_spots
            occupied = Spot.query.filter_by(lot_id=lot.id, status="O").count()
            available = total - occupied

            result.append({
                "id": lot.id,
                "name": lot.name,
                "location": lot.location,
                "address": lot.address,
                "pin_code": lot.pin_code,
                "price": lot.price,
                "total_spots": total,
                "occupied_spots": occupied,
                "available_spots": available
            })

        return result

    
    @auth_required("token")
    def post(self):
        if not is_admin():
            return {"error" : "Only Admin Allowed"}, 403
        
        data = request.get_json()

        if not all(k in data for k in ['name', 'location', 'address', 'pin_code', 'price', 'total_spots']):
            return {"error" : "Missing required fields"}, 400
        
        lot = Lot(
            name = data['name'],
            location = data['location'],
            address = data['address'],
            pin_code = data['pin_code'],
            price = data['price'],
            total_spots = data['total_spots']
        )
        db.session.add(lot)
        db.session.commit()

        for i in range(lot.total_spots):
            spot = Spot(lot_id = lot.id, status = "A")
            db.session.add(spot)
        db.session.commit()

        return {"message" : "Lot and spots created"}, 201

class AdminHistoryapi(Resource):
    @auth_required("token")
    def get(self):
        if not is_admin():
            return {"error": "Admin only"}, 403

        reservations = Reservation.query.join(Spot).join(Lot).all()
        result = []
        for r in reservations:
            result.append({
                "id": r.id,
                "lot_id": r.spot.lot.id if r.spot and r.spot.lot else None,
                "lot_name": r.spot.lot.name if r.spot and r.spot.lot else "Unknown",
                "spot_id": r.spot_id,
                "parking_timestamp": r.parking_start_time.isoformat() if r.parking_start_time else None,
                "leaving_timestamp": r.parking_leaving_time.isoformat() if r.parking_leaving_time else None,
                "parking_cost": r.cost or 0
            })
        return result

class AdminSearchapi(Resource):
    @auth_required("token")
    def get(self):
        if not is_admin():
            return {"error": "Admin only"}, 403

        query = request.args.get('q', '').strip().lower()
        if not query:
            return []

        results = []

        if query.isdigit():
            lot = Lot.query.get(int(query))
            if lot:
                occupied = Spot.query.filter_by(lot_id=lot.id, status='O').count()
                results.append({
                    "lot_id": lot.id,
                    "lot_name": lot.name,
                    "lot_location": lot.location,
                    "address": lot.address,
                    "pin_code": lot.pin_code,
                    "price": lot.price,
                    "total_spots": lot.total_spots,
                    "occupied_spots": occupied,
                    "available_spots": lot.total_spots - occupied
                })
            return results

        # Search lots by name or location (case-insensitive)
        lots = Lot.query.filter(
            (Lot.name.ilike(f"%{query}%")) |
            (Lot.location.ilike(f"%{query}%"))
        ).all()

        for lot in lots:
            occupied = Spot.query.filter_by(lot_id=lot.id, status='O').count()
            results.append({
                "lot_id": lot.id,
                "lot_name": lot.name,
                "lot_location": lot.location,
                "address": lot.address,
                "pin_code": lot.pin_code,
                "price": lot.price,
                "total_spots": lot.total_spots,
                "occupied_spots": occupied,
                "available_spots": lot.total_spots - occupied
            })

        return results

class AdminSummaryapi(Resource):
    @auth_required("token")
    @cache.cached(timeout=30, key_prefix="admin_summary")
    def get(self):
        if not is_admin():
            return {"error": "Admin only"}, 403

        lots = Lot.query.count()
        spots = Spot.query.count()
        occupied = Spot.query.filter_by(status="O").count()
        available = Spot.query.filter_by(status="A").count()

        return {
            "total_lots": lots,
            "total_spots": spots,
            "occupied_spots": occupied,
            "available_spots": available
        }


class UsersListapi(Resource):

    @auth_required("token")
    @marshal_with(user_fields)
    @cache.cached(timeout=60, key_prefix="user_list")
    def get(self):
        if not is_admin():
            return {"error": "Admin only"}, 403

        return User.query.join(User.roles).filter(Role.name == "user", User.active == True).all()

# === User APIs ===

class AvailableLotsapi(Resource):

    @auth_required("token")
    @cache.cached(timeout=5, key_prefix="user_history")
    def get(self):
        lots = Lot.query.all()
        result = []
        for lot in lots:
            available = Spot.query.filter_by(lot_id = lot.id, status = "A").count()
            result.append({
                "id": lot.id,
                "name": lot.name,
                "location": lot.location,
                "address": lot.address,
                "pin_code": lot.pin_code,
                "spots_status": available,
                "price": lot.price
            })
        return result

class BookSpotapi(Resource):

    @auth_required("token")
    def post(self, lot_id):
        spot = Spot.query.filter_by(lot_id = lot_id, status = "A").first()
        if not spot:
            return {"error": "No available spot"}, 400
        
        spot.status = "O"
        reservation = Reservation(
            user_id = current_user.id,
            spot_id = spot.id,
            parking_start_time = datetime.utcnow()
        )
        db.session.add(reservation)
        db.session.commit()
        return {"message": "spot booked", "Spot_id":spot.id, "Reservation_id":reservation.id}
    
class ReleaseSpotapi(Resource):

    @auth_required("token")
    def post(self, reservation_id):
        r = Reservation.query.get(reservation_id)
        if not r or r.user_id != current_user.id:
            return {"error": "Not allowed"}, 403
        
        r.parking_leaving_time = datetime.utcnow()
        lot = Lot.query.get(Spot.query.get(r.spot_id).lot_id)
        duration = (r.parking_leaving_time - r.parking_start_time).total_seconds() / 3600
        print(duration)
        r.cost = round(duration * lot.price, 2)
        print(r.cost)

        spot = Spot.query.get(r.spot_id)
        spot.status = "A"

        db.session.commit()
        return {"message" : "Spot released", "cost" : r.cost, "duration_hrs": round(duration , 2)}
    
class UserHistoryapi(Resource):
    @auth_required("token")
    def get(self):
        user_id = getattr(current_user, 'id', None)
        if not user_id:
            return {"error": "User not authenticated properly"}, 401

        reservations = Reservation.query.filter_by(user_id=user_id).all()

        result = []
        for r in reservations:
            spot = Spot.query.get(r.spot_id)
            lot = Lot.query.get(spot.lot_id) if spot else None
            result.append({
                "id": r.id,
                "spot_id": r.spot_id,
                "lot_id": lot.id if lot else None,
                "lot_name": lot.name if lot else 'Unknown',
                "parking_timestamp": r.parking_start_time.isoformat() if r.parking_start_time else None,
                "leaving_timestamp": r.parking_leaving_time.isoformat() if r.parking_leaving_time else None,
                "parking_cost": r.cost,
                "status": "active" if not r.parking_leaving_time else "vacant"
            })

        return jsonify(result)

class UserExportCSVapi(Resource):
    @auth_required("token")
    def post(self):
        from backend.celery_app import export_csv_for_user
        export_csv_for_user.delay(current_user.id)
        return make_response(jsonify({
            "message": "CSV export started. You’ll receive an email soon."
        }), 202)

def is_admin():
    return current_user.has_role("admin")