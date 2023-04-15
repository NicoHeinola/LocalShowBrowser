from extensions.database import db


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(1000), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username
