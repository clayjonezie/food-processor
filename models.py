from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin

from web import db, login_manager

class RawEntry(db.Model):
  __tablename__ = 'raw_entries'
  id = db.Column(db.Integer, primary_key=True)
  content = db.Column(db.String(1024))
  at = db.Column(db.DateTime)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

  def __init__(self, content=None, at=None):
      self.content = content
      self.at = at

  def __repr__(self):
    return '<Entry: %r>' % self.content

  def from_tweet(self, tweet, user):
    self.at = tweet.created_at
    self.content = tweet.text
    self.user = user
    return self


class User(UserMixin, db.Model):
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(256), unique=True)
  password_hash = db.Column(db.String(128))

  raw_entries = db.relationship('RawEntry', backref='user')

  @property
  def password(self):
    raise AttributeError("Password is not stored")

  @password.setter
  def password(self, password):
    self.password_hash = generate_password_hash(password)

  def verify_password(self, password):
    return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))


class BadWord(db.Model):
  __tablename__ = 'bad_words'
  id = db.Column(db.Integer, primary_key=True)
  word = db.Column(db.String(255), unique=True)

  def __repr__(self):
    return '<BadWord: %r>' % self.word


class Food(db.Model):
  __tablename__ = 'foods'
  id = db.Column(db.Integer, primary_key=True)
