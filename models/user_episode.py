from extensions.database import db
from models.base_model import BaseModel


class UserEpisode(BaseModel):

    id = db.Column(db.Integer, primary_key=True)
    episode_id = db.Column(db.Integer, db.ForeignKey('episode.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    watched = db.Column(db.Boolean, unique=False, nullable=False, default=False)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'episode_id': self.episode_id,
            'user_id': self.user_id,
            'watched': self.watched,
        }

    def __repr__(self):
        return '<Episode %r>' % self.number
