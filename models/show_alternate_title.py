from extensions.database import db
from models.base_model import BaseModel


class ShowAlternateTitle(BaseModel):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), unique=False, nullable=False)
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'))

    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'show_id': self.show_id,
        }

    def __repr__(self):
        return '<Show Alternate Title: %r>' % self.title
