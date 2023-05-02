from controllers.base_controller import BaseController
from flask import jsonify, make_response, request
from extensions.database import db
from extensions.jwt import JWTExtension
from models.user import User


class UserController(BaseController):
    def _register_routes(self):
        base_name = '/user'

        @self._app.route(base_name + "/current", methods=['GET'])
        @JWTExtension.token_required
        def current_user(user):
            response = make_response(jsonify(user.serialize), 200)
            return response
