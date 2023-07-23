from extensions.database import db
from models.base_model import BaseModel


class Show(BaseModel):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), unique=False, nullable=False)
    image_url = db.Column(db.String(1000), unique=False, nullable=True, default='')
    seasons = db.relationship("Season", backref=db.backref("show-seasons", uselist=False), cascade='all, delete')
    show_alternate_titles = db.relationship("ShowAlternateTitle", backref=db.backref("show-show-alternate-title", uselist=False), cascade="all,delete")
    cover_images = db.relationship("ShowCoverImage", backref=db.backref("cover-image", uselist=False), cascade="all,delete")
    user_opened_shows = db.relationship("UserOpenedShow", backref=db.backref("show-user-opened-show", uselist=False), cascade="all,delete")  # Don't get this in serialize

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
