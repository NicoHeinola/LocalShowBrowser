from typing import List
from controllers.base_controller import BaseController
from flask import jsonify, make_response, request
from extensions.database import db
from extensions.jwt import JWTExtension
from helpers.config_helper import ConfigHelper
from models.season import Season
from models.setting import Setting


class SettingController(BaseController):
    def _register_routes(self):
        base_name = '/setting'

        @self._app.route(f"{base_name}/all", methods=['GET'])
        @JWTExtension.admin_token_required
        def get_settings(user):
            all_settings: List[Setting] = Setting.query.all()
            all_settings_serialized = [setting.serialize for setting in all_settings]
            all_settings_serialized = sorted(all_settings_serialized, key=lambda x: x['name'])

            return make_response(jsonify(all_settings_serialized))

        @ self._app.route(f"{base_name}/<name>", methods=['DELETE'])
        @ JWTExtension.admin_token_required
        def reset_setting(user, name):
            setting = Setting.query.filter_by(name=name).first()
            if setting is None:
                return make_response({"error": "Setting not found!"}, 404)

            db.session.delete(setting)
            db.session.commit()

            ConfigHelper.reload_configurations()

            return make_response("", 200)

        @ self._app.route(f"{base_name}/<name>", methods=['PUT'])
        @ JWTExtension.admin_token_required
        def change_setting(user, name):
            data = request.json
            value = data['value']

            setting = Setting.query.filter_by(name=name).first()
            if setting is None:
                return make_response({"error": "Setting not found!"}, 404)

            ConfigHelper.custom_logic_for_setting(name, value)

            setting.value = value
            db.session.commit()

            ConfigHelper.reload_configurations()

            return make_response("", 200)
