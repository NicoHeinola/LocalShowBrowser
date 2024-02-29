from typing import List
from controllers.base_controller import BaseController
from flask import jsonify, make_response, request
from extensions.database import db
from extensions.jwt import JWTExtension
from models.blacklisted_folder import BlackListerFolder
from models.user import User


class BlackListerFolderController(BaseController):
    def _register_routes(self):
        base_name = '/blacklisted_folder'

        @self._app.route(f"{base_name}/all", methods=['GET'])
        @JWTExtension.token_required
        def get_blacklisted_folders(user):
            all_folders: List[BlackListerFolder] = BlackListerFolder.query.all()
            all_folders_serialized = [folder.serialize for folder in all_folders]

            return make_response(jsonify(all_folders_serialized))

        @self._app.route(f"{base_name}/<id>", methods=['PUT'])
        @JWTExtension.token_required
        def update_blacklisted_folder(user, id):
            folder = BlackListerFolder.query.filter_by(id=id).first()
            if folder is None:
                return make_response({"error": "Blacklisted folder not found!"}, 404)

            data = request.json
            path = data['path']
            folder.folder_path = path
            db.session.commit()
            return make_response("", 200)

        @self._app.route(base_name, methods=['POST'])
        @JWTExtension.token_required
        def add_blacklisted_folder(user):
            data = request.json
            path = data['path']
            folder = BlackListerFolder(folder_path=path)
            db.session.add(folder)
            db.session.commit()
            return make_response("", 200)

        @self._app.route(f"{base_name}/<id>", methods=['DELETE'])
        @JWTExtension.token_required
        def delete_blacklisted_folder(user, id):
            folder = BlackListerFolder.query.filter_by(id=id).first()
            if folder is None:
                return make_response({"error": "Blacklisted folder not found!"}, 404)

            db.session.delete(folder)
            db.session.commit()
            return make_response("", 200)
