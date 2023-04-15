from extensions.database import db


class Show(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), unique=False, nullable=False)

    def __repr__(self):
        return '<Show %r>' % self.title
