from extensions.database import db
from models.base_model import BaseModel


class Season(BaseModel):

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=False, nullable=False)
    title = db.Column(db.Integer, unique=False, nullable=False)
    path = db.Column(db.String(1000), unique=False, nullable=False)
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'))
    episodes = db.relationship("Episode", backref=db.backref("season-episodes", uselist=False), cascade='all, delete')

    @property
    def serialize(self):
        return {
            'id': self.id,
            'number': self.number,
            'title': self.title,
            'path': self.path,
            'show_id': self.show_id,
            'episodes': [episode.serialize for episode in self.episodes]
        }

    def __repr__(self):
        return '<Season %r>' % self.number
