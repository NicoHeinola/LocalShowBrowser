from extensions.database import db
from extensions.google_image_search import GoogleImageSearch
from models.base_model import BaseModel


class ShowCoverImage(BaseModel):

    id = db.Column(db.Integer, primary_key=True)
    cover_image = db.Column(db.LargeBinary, unique=False, nullable=False)
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'))

    @property
    def serialize(self):
        return {
            'id': self.id,
            'cover_image': GoogleImageSearch.bytes_to_base64(self.cover_image),
            'show_id': self.show_id,
        }

    def __repr__(self):
        return '<Show Cover Image %r>' % self.id
