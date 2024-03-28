from flask_cors import cross_origin
import jwt
from controllers.base_controller import BaseController
from flask import jsonify, make_response, request
from extensions.database import db
from extensions.jwt import JWTExtension
from models.user import User
from werkzeug.security import generate_password_hash, check_password_hash


class AuthController(BaseController):
    def _register_routes(self):
        base_name = '/auth'

        @self._app.route(f"{base_name}/login", methods=['POST'])
        def login():
            data = request.json
            username = data['username']
            password = data['password']

            # Check that params exist
            if not username or not password:
                return make_response({"error": 'Missing parameter(s)'}, 400)

            # Check that user exists
            user = User.query.filter_by(username=username).first()
            if not user:
                return make_response({"error": 'Invalid username or password!'}, 401)

            if not check_password_hash(user.password, password):
                return make_response({"error": 'Invalid username or password!'}, 401)

            # generates the JWT Token
            expires_in_minutes = 2 ** 20
            token = JWTExtension.make_jwt_token(expires_in_minutes, id=user.id, is_admin=user.is_admin, username=user.username)

            return make_response(jsonify({'token': token}), 200)

        @self._app.route(f"{base_name}/register", methods=['POST'])
        def register():
            data = request.json
            username = data['username']
            password = data['password']

            # Check that params exist
            if not username or not password:
                return make_response({"error": 'Missing parameter(s)'}, 400)

            # Check that user doesn't exist
            user = User.query.filter_by(username=username).first()
            if user:
                return make_response({"error": 'Username already in use!'}, 400)

            # Create new user
            password_hash = generate_password_hash(password)
            user = User(username=username, password=password_hash)
            db.session.add(user)
            db.session.commit()

            return make_response({"status": "success"}, 200)
