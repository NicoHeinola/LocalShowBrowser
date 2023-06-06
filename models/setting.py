from extensions.database import db
from models.base_model import BaseModel


class Setting(BaseModel):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000), unique=False, nullable=False)
    value = db.Column(db.String(1000), unique=False, nullable=True)
    data_type = db.Column(db.String(1000), unique=False, nullable=False)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'value': self.value,
            'data_type': self.data_type,
        }

    def __repr__(self):
        return '<Setting %r>' % self.name
