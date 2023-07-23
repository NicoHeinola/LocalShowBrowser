# decorator for verifying the JWT
import datetime
from functools import wraps
from flask import Flask, jsonify, request
import jwt

from models.user import User


class JWTExtension:
    app: Flask = None

    @staticmethod
    def with_current_user(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            # jwt is passed in the request header
            if 'Authorization' in request.headers:
                token = request.headers['Authorization']
            # return 401 if token is not passed
            if not token:
                return f(None, *args, **kwargs)

            try:
                # decoding the payload to fetch the stored details
                data = jwt.decode(token, JWTExtension.app.config['SECRET_KEY'], 'HS256')
                current_user = User.query.filter_by(id=data['id']).first()
            except Exception as e:
                print("EXCEPTION:", e)
                return jsonify({'message': 'Token is invalid!'}), 401
            # returns the current logged in users context to the routes
            return f(current_user, *args, **kwargs)

        return decorated

    @staticmethod
    def token_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            # jwt is passed in the request header
            if 'Authorization' in request.headers:
                token = request.headers['Authorization']
            # return 401 if token is not passed
            if not token:
                return jsonify({'message': 'Token is missing!'}), 401

            try:
                # decoding the payload to fetch the stored details
                data = jwt.decode(token, JWTExtension.app.config['SECRET_KEY'], 'HS256')
                current_user = User.query.filter_by(id=data['id']).first()
            except Exception as e:
                print("EXCEPTION:", e)
                return jsonify({'message': 'Token is invalid!'}), 401
            # returns the current logged in users context to the routes
            return f(current_user, *args, **kwargs)

        return decorated

    @staticmethod
    def admin_token_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            # jwt is passed in the request header
            if 'Authorization' in request.headers:
                token = request.headers['Authorization']
            # return 401 if token is not passed
            if not token:
                return jsonify({'error': 'Token is missing!'}), 401

            try:
                # decoding the payload to fetch the stored details
                data = jwt.decode(token, JWTExtension.app.config['SECRET_KEY'], 'HS256')
                current_user = User.query.filter_by(id=data['id']).first()
                if not current_user.is_admin:
                    return jsonify({'error': 'Not admin!'}), 401
            except Exception as e:
                print("EXCEPTION:", e)
                return jsonify({'error': 'Token is invalid!'}), 401
            # returns the current logged in users context to the routes
            return f(current_user, *args, **kwargs)

        return decorated

    @staticmethod
    def make_jwt_token(expires_in_minutes, **kwargs):
        data = {"expiration": str(datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_in_minutes)), **kwargs}
        token = jwt.encode(data, JWTExtension.app.config['SECRET_KEY'])
        return token
