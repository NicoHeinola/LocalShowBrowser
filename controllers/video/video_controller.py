from controllers.base_controller import BaseController
from models.user import User
from extensions.jwt import JWTExtension
from flask import make_response, send_from_directory
import os


class VideoController(BaseController):
    def _register_routes(self):
        base_name = '/video'

        @self._app.route(f"{base_name}/watch/<path:video_path>", methods=['GET'])
        @JWTExtension.with_current_user
        def get_video_data(current_user: User, video_path: str):
            # Create the full path to the video file
            video_file_path: str = os.path.join(self._app.config["SHOW_STREAM_VIDEO_PATH"], video_path)

            if not os.path.exists(video_file_path):
                return make_response({"error": "Video doesn't exist!"}, 404)

            return send_from_directory(self._app.config["SHOW_STREAM_VIDEO_PATH"], video_path)
