from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin

from . import db
from . import login_manager

class RawEntry(db.Model):
  __tablename__ = 'raw_entries'
  id = db.Column(db.Integer, primary_key=True)
  content = db.Column(db.String(1024))
  at = db.Column(db.DateTime)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
  tags = db.relationship('Tag', backref='raw_entry')

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


class Tag(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  raw_entry_id = db.Column(db.Integer, db.ForeignKey('raw_entries.id'))
  pos = db.Column(db.Integer)
  food_short = db.Column(db.Integer, db.ForeignKey('food_shorts.id'))
  food_description = db.Column(db.Integer, db.ForeignKey('food_descriptions.id'))


class User(UserMixin, db.Model):
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(256), unique=True)
  password_hash = db.Column(db.String(128))

  raw_entries = db.relationship('RawEntry', backref='user', order_by='desc(RawEntry.at)')

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
  refuse_percent = db.Column(db.String(10))
  sci_name = db.Column(db.String(65))
  pro_factor = db.Column(db.String(10))
  fat_factor = db.Column(db.String(10))
  cho_factor = db.Column(db.String(10))

  nutrients = db.relationship('NutrientData', backref='food')

  def __repr__(self):
    return "<FoodDescription: %s>" % self.short_desc


  def from_ndb(self, ndb_row):
    self.id = int(ndb_row[0])
    self.food_group_code = int(ndb_row[1])
    self.long_desc = ndb_row[2]
    self.short_desc = ndb_row[3]
        
    self.common_name = ndb_row[4]
    self.manufac_name = ndb_row[5]
    self.refuse_desc = ndb_row[7]
        
    self.refuse_percent = ndb_row[8]
    self.sci_name = ndb_row[9]
    self.pro_factor = ndb_row[11]
        
    self.fat_factor = ndb_row[12]
    self.cho_factor = ndb_row[13]

    return self


def search_food_descriptions(query):
  return FoodDescription.query.filter(
      FoodDescription.long_desc.like("%%%s%%" % query)).all()


class NutrientDefinition(db.Model):
  __tablename__ = 'nutrient_definitions'
  nutr_no = db.Column(db.Integer, primary_key=True)
  units = db.Column(db.String(7))
  tagname = db.Column(db.String(20))
  desc = db.Column(db.String(60))
  num_dec = db.Column(db.String(1))
  sr_order = db.Column(db.String(6))

  nutrients = db.relationship('NutrientData', backref='nutrient')

  def __repr__(self):
    return "<NutrientDefinition: %s, %s>" % (self.desc, self.units)


  def from_ndb(self, ndb_row):
    self.nutr_no, self.units, self.tagname, self.desc, \
      self.num_dec, self.sr_order = ndb_row
    self.nutr_no = int(self.nutr_no)
    return self


class NutrientData(db.Model):
  __tablename__ = 'nutrient_data'
  id = db.Column(db.Integer, primary_key=True)
  ndb_no = db.Column(db.Integer, db.ForeignKey('food_descriptions.id'))
  nutr_no = db.Column(db.Integer, 
      db.ForeignKey('nutrient_definitions.nutr_no'))
  nutr_val = db.Column(db.Float)
  num_data_pts = db.Column(db.Integer)
  std_error = db.Column(db.Float)
  add_nutr_mark = db.Column(db.String(2))
  val_min = db.Column(db.Float)
  val_max = db.Column(db.Float)

  def __repr__(self):
    return '<NutrientData: %s: %s: %s>' % (self.food, self.nutrient, self.nutr_val)

  def from_ndb(self, ndb_row):
    self.ndb_no, self.nutr_no, self.nutr_val, self.num_data_pts, \
      self.std_error, _, _, _, self.add_nutr_mark, _, self.val_min, \
      self.val_max, _, _, _, _, _, _, = ndb_row

    self.ndb_no = int(self.ndb_no)
    self.nutr_no = int(self.nutr_no)
    self.nutr_val = float(self.nutr_val) if self.nutr_val != '' else None
    self.num_data_pts = int(self.num_data_pts)
    self.std_error = float(self.std_error) if self.std_error != '' else None
    self.val_min = float(self.val_min) if self.val_min != '' else None
    self.val_max = float(self.val_max) if self.val_max != '' else None

    return self
