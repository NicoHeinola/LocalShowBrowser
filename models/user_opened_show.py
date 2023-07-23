from extensions.database import db
from models.base_model import BaseModel


class UserOpenedShow(BaseModel):

    id = db.Column(db.Integer, primary_key=True)
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    @property
    def serialize(self):
        return {
            'id': self.id,
            'episode_id': self.episode_id,
            'user_id': self.user_id,
        }

    def __repr__(self):
        return '<UserOpenedShow %r>' % self.id
