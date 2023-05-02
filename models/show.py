from extensions.database import db
from models.base_model import BaseModel


class Show(BaseModel):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), unique=False, nullable=False)
    image_url = db.Column(db.String(1000), unique=False, nullable=False, default='')
    seasons = db.relationship("Season", backref=db.backref("show-seasons", uselist=False))
    show_alternate_titles = db.relationship("ShowAlternateTitle", backref=db.backref("show-show-alternate-title", uselist=False))
    cover_images = db.relationship("ShowCoverImage", backref=db.backref("cover-image", uselist=False))

    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'image_url': self.image_url,
            'seasons': [season.serialize for season in self.seasons],
            'alternate_titles': [t.serialize for t in self.show_alternate_titles],
            'cover_images': [c_image.serialize for c_image in self.cover_images],
        }

    def __repr__(self):
        return '<Show %r>' % self.title
