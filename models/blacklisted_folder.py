from extensions.database import db
from models.base_model import BaseModel


class BlackListerFolder(BaseModel):

    id = db.Column(db.Integer, primary_key=True)
    folder_path = db.Column(db.String(1000), unique=False, nullable=False)

    def __repr__(self):
        return '<BlackListedFolder: %r>' % self.folder_path

    @property
    def serialize(self):
        return {
            'id': self.id,
            'folder_path': self.folder_path,
        }

    def seeds():
        path = 'Rick and mort Season 1'
        exists = BlackListerFolder.query.filter_by(folder_path=path).first()
        if exists:
            return
        black_listed_folder = BlackListerFolder(folder_path=path)
        db.session.add(black_listed_folder)
        db.session.commit()
