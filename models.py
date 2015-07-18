from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.hybrid import hybrid_property
from database import Base
import my_bcrypt

class Entry(Base):
    __tablename__ = 'entries'
    id = Column(Integer, primary_key=True)
    content = Column(String(255))
    at = Column(DateTime)

    def __init__(self, content=None, at=None):
        self.content = content
        self.at = at

    def __repr__(self):
        return '<Entry: %r>' % self.content


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(db.String(64), unique=True)
    _password = Column(String(128))

    @hybrid_property
    def password(self):
      return self._password

    @password_setter
    def _set_password(self, plaintext):
      self._password = my_bcrypt.generate_password_hash(plaintext)
