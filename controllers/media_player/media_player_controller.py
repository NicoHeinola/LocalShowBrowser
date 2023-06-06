from controllers.base_controller import BaseController
from flask import jsonify, make_response, request
from extensions.database import db
from extensions.jwt import JWTExtension
from extensions.vlc_media_player import VLCMediaPlayerExtension
from models.user import User


class MediaPlayerController(BaseController):
    def _register_routes(self):
        base_name = '/media-player'

        @self._app.route(base_name + "/is-downloaded", methods=['GET'])
        @JWTExtension.admin_token_required
        def is_media_player_downloaded(user):
            response = make_response(jsonify(VLCMediaPlayerExtension.vlc_media_player_is_downloaded()), 200)
            return response

        @self._app.route(base_name + "/download", methods=['GET'])
        @JWTExtension.admin_token_required
        def download_media_player(user):
            response = make_response(jsonify(VLCMediaPlayerExtension.download()), 200)
            return response
