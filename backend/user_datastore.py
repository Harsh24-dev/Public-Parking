from flask_security import SQLAlchemyUserDatastore
from backend.models import db
from backend.models import User, Role

user_datastore = SQLAlchemyUserDatastore(db, User, Role)