from extensions.database import db


class Season(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=False, nullable=False)
    title = db.Column(db.Integer, unique=False, nullable=False)
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'))
    show = db.relationship("show", backref=db.backref("show", uselist=False))

    def __repr__(self):
        return '<Season %r>' % self.number
