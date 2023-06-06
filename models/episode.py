from extensions.database import db
from models.base_model import BaseModel


class Episode(BaseModel):

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=False, nullable=False)
    title = db.Column(db.Integer, unique=False, nullable=False)
    filename = db.Column(db.String(1000), unique=False, nullable=False)
    season_id = db.Column(db.Integer, db.ForeignKey('season.id'))
    is_special = db.Column(db.Boolean, unique=False, nullable=False, default=False)
    user_episode = db.relationship("UserEpisode", backref=db.backref("user-episode", uselist=False), cascade="all,delete")

    @property
    def serialize(self):
        return {
            'id': self.id,
            'number': self.number,
            'title': self.title,
            'filename': self.filename,
            'season_id': self.season_id,
            'is_special': self.is_special,
        }

    def __repr__(self):
        return '<Episode %r>' % self.number
