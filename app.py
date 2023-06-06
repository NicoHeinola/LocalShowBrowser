from flask import Flask, Response
from flask_cors import CORS
from controllers.auth.auth_controller import AuthController
from controllers.blacklisted_folder.blacklisted_folder_controller import BlackListerFolderController
from controllers.media_player.media_player_controller import MediaPlayerController
from controllers.setting.setting_controller import SettingController
from controllers.show.show_controller import ShowController
from controllers.user.user_controller import UserController
from extensions.database import db
from extensions.jwt import JWTExtension
from extensions.seeder import Seeder
from helpers.config_helper import ConfigHelper
from helpers.show_helper import ShowHelper
from helpers.vlc_media_player_helper import VLCMediaPlayerHelper
from models.show_alternate_title import ShowAlternateTitle
from models.show_cover_image import ShowCoverImage
from models.user import User
from models.user_episode import UserEpisode
from models.setting import Setting
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = '*AER*SAETGYSRYH*W¤&*S%¤*U%*#A'

CORS(app, resources={r"/*": {"origins": "*"}})

migrate = Migrate(app, db)  # Migration support !!!

db.init_app(app)
show_controller = ShowController(app)
auth_controller = AuthController(app)
user_controller = UserController(app)
setting_controller = SettingController(app)
media_player_controller = MediaPlayerController(app)
blacklisted_folder_controller = BlackListerFolderController(app)

JWTExtension.app = app
ShowHelper.app = app
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
