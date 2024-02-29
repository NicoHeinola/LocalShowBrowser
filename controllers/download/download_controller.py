from controllers.base_controller import BaseController
from flask import jsonify, make_response, request
from extensions.database import db
from extensions.jwt import JWTExtension
from extensions.vlc_media_player import VLCMediaPlayerExtension
from helpers.video_helper import VideoHelper
from models.user import User


class DownloadController(BaseController):
    def _register_routes(self):
        base_name = '/download'

        @self._app.route(f"{base_name}/vlc/is-downloaded", methods=['GET'])
        @JWTExtension.admin_token_required
        def is_media_player_downloaded(user):
            response = make_response(jsonify(VLCMediaPlayerExtension.vlc_media_player_is_downloaded()), 200)
            return response

        @self._app.route(f"{base_name}/vlc/download", methods=['GET'])
        @JWTExtension.admin_token_required
        def download_media_player(user):
            response = make_response(jsonify(VLCMediaPlayerExtension.download()), 200)
            return response

        @self._app.route(f"{base_name}/ffmpeg/is-downloaded", methods=['GET'])
        @JWTExtension.admin_token_required
        def is_ffmpeg_downloaded(user):
            response = make_response(jsonify(VideoHelper.is_ffmpeg_installed()), 200)
            return response

        @self._app.route(f"{base_name}/ffmpeg/download", methods=['GET'])
        @JWTExtension.admin_token_required
        def download_ffmpeg(user):
            response = make_response(jsonify(VideoHelper.install_ffmpeg()), 200)
            return response
