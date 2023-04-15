import json
from controllers.base_controller import BaseController
from flask import jsonify, make_response, request
from extensions.database import db


class ShowController(BaseController):
    def _register_routes(self):
        base_name = '/shows'

        @self._app.route(base_name + "", methods=['GET'])
        def shows():
            search_term = request.args.get('searchTerm')
            response = make_response(jsonify(search_term), 200)
            return self._return_response(response)
