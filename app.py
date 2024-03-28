import os
from flask import Flask, Response
from flask_cors import CORS
from controllers.auth.auth_controller import AuthController
from controllers.blacklisted_folder.blacklisted_folder_controller import BlackListerFolderController
from controllers.default.default_controller import DefaultController
from controllers.download.download_controller import DownloadController
from controllers.setting.setting_controller import SettingController
from controllers.show.show_controller import ShowController
from controllers.user.user_controller import UserController
from controllers.video.video_controller import VideoController
from extensions.database import db
from extensions.jwt import JWTExtension
from extensions.seeder import Seeder
from helpers.config_helper import ConfigHelper
from helpers.show_helper import ShowHelper
from helpers.video_helper import VideoHelper
from helpers.vlc_media_player_helper import VLCMediaPlayerHelper
from models.show_alternate_title import ShowAlternateTitle
from models.show_cover_image import ShowCoverImage
from models.user import User
from models.user_episode import UserEpisode
from models.user_opened_show import UserOpenedShow
from models.setting import Setting
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = '*AER*SAETGYSRYH*W¤&*S%¤*U%*#A'

CORS(app, resources={r"/*": {"origins": "*"}})

migrate = Migrate(app, db)  # Migration support !!!

db.init_app(app)

show_controller = ShowController(app)
video_controller = VideoController(app)
auth_controller = AuthController(app)
user_controller = UserController(app)
setting_controller = SettingController(app)
download_controller = DownloadController(app)
blacklisted_folder_controller = BlackListerFolderController(app)
default_controller = DefaultController(app)

JWTExtension.app = app
ShowHelper.app = app
VideoHelper.app = app
VLCMediaPlayerHelper.app = app
ConfigHelper.app = app


@app.after_request
def after_request(response: Response) -> Response:
    return response


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        Seeder.run_seeds()
        ConfigHelper.reload_configurations()

    app.run(host='0.0.0.0', port=5000, debug=True)
