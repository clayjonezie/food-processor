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


class FoodShort(db.Model):
  __tablename__ = 'food_shorts'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(255), unique=True)
  common_long_id = db.Column(db.Integer, db.ForeignKey('food_descriptions.id'))


class FoodDescription(db.Model):
  __tablename__ = 'food_descriptions'
  id = db.Column(db.Integer, primary_key=True)
  food_group_code = db.Column(db.Integer)
  long_desc = db.Column(db.String(200))
  short_desc = db.Column(db.String(200))
  common_name = db.Column(db.String(100))
  manufac_name = db.Column(db.String(65))
  refuse_desc = db.Column(db.String(135))
  refuse_percent = db.Column(db.String(0))
  sci_name = db.Column(db.String(65))
  pro_factor = db.Column(db.String(10))
  fat_factor = db.Column(db.String(10))
  cho_factor = db.Column(db.String(10))


  def from_ndb(self, ndb_row):
    self.id, self.food_group_code, self.long_desc, self.short_desc,\
        self.common_name, self.manufac_name, _, self.refuse_desc, \
        self.refuse_percent, self.sci_name, _, self.pro_factor, \
        self.fat_factor, self.cho_factor = ndb_row
    self.id = int(self.id)
    self.food_group_code = int(self.food_group_code)
    return self


class NutrientDefinition(db.Model):
  nutr_no = db.Column(db.Integer, primary_key=True)
  units = db.Column(db.String(7))
  tagname = db.Column(db.String(20))
  desc = db.Column(db.String(60))
  num_dec = db.Column(db.String(1))
  sr_order = db.Column(db.String(6))


  def from_ndb(self, ndb_row):
    self.nutr_no, self.units, self.tagname, self.desc, \
      self.num_dec, self.sr_order = ndb_row
    self.nutr_no = int(self.nutr_no)
    return self

