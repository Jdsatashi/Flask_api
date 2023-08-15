from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import string
import random

from sqlalchemy import ForeignKey

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    create_at = db.Column(db.DateTime, nullable=True, default=datetime.now)
    update_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.now)
    bookmarks = db.relationship('Bookmark', backref='user')

    def __repr__(self):
        return 'User>>> {self.username}'


class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String, nullable=True)
    url = db.Column(db.String, nullable=False)
    short_url = db.Column(db.String(3), nullable=False)
    visits = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    create_at = db.Column(db.DateTime, nullable=True, default=datetime.now)
    update_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.now)

    def generate_short_url(self):
        charaters = string.digits + string.ascii_letters
        pick_chars = ''.join(random.choices(charaters, k=3))
        link = self.query.filter_by(short_url=pick_chars).first()

        if link:
            self.generate_short_url()
        else:
            return pick_chars

    def __init__(self, **kwargs):
        super().__init__(** kwargs)
        self.short_url = self.generate_short_url()

    def __repr__(self) -> str:
        return f'Bookmark>>> {self.url}'
