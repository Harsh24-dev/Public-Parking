from flask import Flask
from flask_security import SQLAlchemyUserDatastore, Security
from backend.user_datastore import user_datastore
from flask_restful import Api
from flask_cors import CORS
from celery import Celery
from backend.cache import Cache
from backend.models import db
from backend.api import *
from backend.auth_api import *

app = Flask(__name__)
app.app_context().push()

CORS(app, supports_credentials=True, origins=["http://localhost:5173","http://127.0.0.1:5173"])
api = Api(app)

# === Configuration ===
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///parking_db.sqlite3"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECURITY_JOIN_USER_ROLES'] = False

app.config['SECURITY_PASSWORD_SALT'] = "Something_difficult_to_guess"
app.config['SECRET_KEY'] = "Something_very_secret"
app.config['SECURITY_TOKEN_AUTHENTICATION_HEADER'] = 'Authentication-Token'
app.config['SECURITY_TOKEN_AUTHENTICATION_ENABLED'] = True

# === Redis Cache Config ===
app.config['CACHE_TYPE'] = 'RedisCache'
app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379/0'
app.config['CACHE_DEFAULT_TIMEOUT'] = 60
app.config['CACHE_KEY_PREFIX'] = 'vp2_'
app.config['CACHE_ALLOW_NULL'] = True
app.config['CACHE_OPTIONS'] = {"cache_args": ["request"]}
cache.init_app(app)

#    === DB and Security ===
db.init_app(app)
security = Security(app, user_datastore)

with app.app_context():
    db.create_all()
    admin_role = user_datastore.find_or_create_role(name='admin', description='Administrator role')
    user_role = user_datastore.find_or_create_role(name='user', description='User role')

    if not user_datastore.find_user(email="admin@parking"):
        user_datastore.create_user(
            email="admin@parking",
            password="admin123",
            full_name="Admin",
            roles=[admin_role],
        )
    db.session.commit()

# === Celery Config ===
app.config['CELERY_BROKER_URI'] = 'redis://127.0.0.1:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://127.0.0.1:6379/0'

# === API Routes ===
api.add_resource(Register, '/api/auth/register')
api.add_resource(Login, '/api/auth/login')
api.add_resource(Logout, '/api/auth/logout')

api.add_resource(Lotapi, '/api/admin/lots/<int:lot_id>')
api.add_resource(LotListapi, '/api/admin/lots')
api.add_resource(AdminSearchapi, '/api/admin/search')
api.add_resource(AdminHistoryapi, '/api/admin/history')
api.add_resource(AdminSummaryapi, '/api/admin/summary')
api.add_resource(UsersListapi, '/api/admin/users')

api.add_resource(AvailableLotsapi, '/api/user/lots')
api.add_resource(BookSpotapi, '/api/user/book/<int:lot_id>')
api.add_resource(ReleaseSpotapi, '/api/user/release/<int:reservation_id>')
api.add_resource(UserHistoryapi, '/api/user/history')
api.add_resource(UserExportCSVapi, '/api/user/export')


if __name__ == "__main__":
    app.run(debug=True)