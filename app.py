from flask import Flask, Response, make_response
from flask_cors import CORS, cross_origin
from controllers.auth.auth_controller import AuthController
from controllers.media_player.media_player_controller import MediaPlayerController
from controllers.show.show_controller import ShowController
from controllers.user.user_controller import UserController
from extensions.database import db
from extensions.jwt import JWTExtension
from extensions.seeder import Seeder
from helpers.show_helper import ShowHelper
from models.show_alternate_title import ShowAlternateTitle
from models.show_cover_image import ShowCoverImage
from models.user import User
from models.user_episode import UserEpisode

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = '*AER*SAETGYSRYH*W¤&*S%¤*U%*#A'
app.config['SHOW_MAIN_PATH'] = fr"C:\Users\Nico\Desktop\TestiVideot"

CORS(app, resources={r"/*": {"origins": "*"}})

db.init_app(app)
show_controller = ShowController(app)
auth_controller = AuthController(app)
user_controller = UserController(app)
media_player_controller = MediaPlayerController(app)

JWTExtension.app = app
ShowHelper.app = app


@app.after_request
def after_request(response: Response) -> Response:
    return response


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        Seeder.run_seeds()
    app.run(host='0.0.0.0', port=5000, debug=True)
