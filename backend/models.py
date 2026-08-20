from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin

db = SQLAlchemy()

# Association table for many-to-many relationship between User and Role
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(300))

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    full_name = db.Column(db.String(100),nullable = False)
    active = db.Column(db.Boolean(), default=True)

    fs_uniquifier = db.Column(db.String(), unique=True, nullable=False)
    fs_token_uniquifier = db.Column(db.String(), unique=True, nullable=False)

    reservations = db.relationship('Reservation', backref='user', lazy=True)
    # Use association table for roles
    roles = db.relationship('Role', secondary=user_roles, backref=db.backref('users', lazy='dynamic'))

class Lot(db.Model):
    __tablename__ = 'lot'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    location = db.Column(db.String(100))
    address = db.Column(db.String(200))
    pin_code = db.Column(db.Integer())
    price = db.Column(db.Float())
    total_spots = db.Column(db.Integer())

    spots = db.relationship('Spot', cascade="all, delete", backref='lot', lazy=True)

class Spot(db.Model):
    __tablename__ = 'spot'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    lot_id = db.Column(db.Integer(), db.ForeignKey('lot.id'), nullable=False)
    status = db.Column(db.String(1), default='A')
    spot_number = db.Column(db.String(10))

    reservations = db.relationship('Reservation', cascade="all, delete", backref='spot', lazy=True)

class Reservation(db.Model):
    __tablename__ = 'reservation'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    spot_id = db.Column(db.Integer(), db.ForeignKey('spot.id'))
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    parking_start_time = db.Column(db.DateTime(), default = datetime.utcnow)
    parking_leaving_time = db.Column(db.DateTime(), nullable = True)
    cost = db.Column(db.Float())