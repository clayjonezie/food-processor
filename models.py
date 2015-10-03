from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.hybrid import hybrid_property

from web import db

class Entry(db.Model):
    __tablename__ = 'entries'
    id = Column(Integer, primary_key=True)
    content = Column(String(255))
    at = Column(DateTime)

    def __init__(self, content=None, at=None):
        self.content = content
        self.at = at

    def __repr__(self):
        return '<Entry: %r>' % self.content


class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(db.String(64), unique=True)

