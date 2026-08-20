from .models import db
from .user_datastore import user_datastore
from flask import request, make_response, jsonify
from flask_restful import Resource
from flask_security import utils, auth_token_required


class Register(Resource):
    def post(self):
        body_content = request.get_json()

        required_fields = ['email', 'password','full_name']
        if not all(field in body_content for field in required_fields):
            return make_response(jsonify({'message': 'email, password, full_name are required for registration.'}), 400)

        email = body_content['email']
        password = body_content['password']
        full_name = body_content.get('full_name',None)

        if user_datastore.find_user(email=email):
            return make_response(jsonify({'message': 'User already exists'}), 400)

        user_role = user_datastore.find_role('user')

        user = user_datastore.create_user(
            email=email,
            password = password,
            full_name=full_name,
            roles=[user_role]
        )
        db.session.commit()

        return make_response(jsonify({
            'message': 'User created successfully',
            'user': {
                'email': user.email,
                'full_name': user.full_name,
                'roles': [role.name for role in user.roles]
            }
        }), 201)


class Login(Resource):
    def post(self):
        credentials = request.get_json()

        if 'email' not in credentials or 'password' not in credentials:
            return make_response(jsonify({'message': 'email and password are required for login'}), 400)

        email = credentials['email']
        password = credentials['password']

        user = user_datastore.find_user(email=email)
        if not user:
            return make_response(jsonify({'message': 'User does not exist'}), 404)

        if not utils.verify_password(password, user.password):
            return make_response(jsonify({'message': 'Invalid password'}), 401)

        token = user.get_auth_token()
        roles = [role.name for role in user.roles]

        return make_response(jsonify({
            'message': 'Login successful',
            'Authentication-token' : token,
            'email' : user.email,
            'role' : roles[0] if roles else 'user',
        }), 200)


class Logout(Resource):
    @auth_token_required
    def post(self):
        utils.logout_user()
        return make_response(jsonify({'message': 'Logout successful'}), 200)