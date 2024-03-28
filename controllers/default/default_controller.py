from typing import List
from controllers.base_controller import BaseController
from flask import jsonify, make_response, render_template, request, send_from_directory
from extensions.database import db
from extensions.jwt import JWTExtension
from models.blacklisted_folder import BlackListerFolder
from models.user import User
import os


class DefaultController(BaseController):
    def _register_routes(self):
        base_name = ''
        front_dir = os.path.join(self._app.root_path, 'front_build')

        @self._app.route(f"{base_name}/")
        def front_index():
            return send_from_directory(front_dir, 'index.html')

        @self._app.route(f'{base_name}/<path:filename>')
        def serve_static(filename):
            return send_from_directory(front_dir, filename)
