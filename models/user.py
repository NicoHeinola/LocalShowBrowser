from extensions.database import db
from werkzeug.security import generate_password_hash

from models.base_model import BaseModel


class User(BaseModel):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String, unique=False, nullable=False)
    is_admin = db.Column(db.Boolean, unique=False, nullable=False, default=False)
    user_episodes = db.relationship("UserEpisode", backref=db.backref("user-user-episodes", uselist=False), cascade="all,delete")

    @property
    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'is_admin': self.is_admin,
            'user_episodes': [episode.serialize for episode in self.user_episodes],
        }

    def __repr__(self):
        return '<User %r>' % self.username

    def seeds():
        hashed_password = generate_password_hash('admin')
        username = 'admin'
        exists = User.query.filter_by(username=username).first()
        if exists:
            return
        admin = User(password=hashed_password, username=username, is_admin=True)
        db.session.add(admin)
        db.session.commit()
