from flask import Flask
from flask_cors import CORS, cross_origin
from controllers.show.show_controller import ShowController
from extensions.database import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db.init_app(app)

show_controller = ShowController(app)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
