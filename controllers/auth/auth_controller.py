from controllers.base_controller import BaseController
from flask import jsonify, make_response, request
from extensions.database import db
from models.user import User


class AuthController(BaseController):
    def _register_routes(self):
        base_name = '/auth'

        @self._app.route(base_name + "/login", methods=['POST'])
        def login():
            username = request.args.get('username')
            password = request.args.get('password')
            response = make_response(jsonify([username, password]), 200)
            return self._return_response(response)

        @self._app.route(base_name + "/register", methods=['POST'])
        def register():
            username = request.args.get('username')
            password = request.args.get('password')

            response = make_response(jsonify([username, password]), 200)
            return self._return_response(response)
