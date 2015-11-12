from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin
from datetime import datetime, timedelta

from . import db
from . import login_manager
from . import fplib


class RawEntry(db.Model):
    """
    A RawEntry object is the text a user initially entered, and the entry point
    to the NLP pipeline. Currently limited to 1024 chars, this could be easily
    increased. 
    """
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


def get_week_list(user):
    """
    :param user: the user
    returns a list of RawEntry objects for a given user 
    over the last week
    """
    now = datetime.utcnow()
    weekago = now - timedelta(days=6)
    return RawEntry.query.filter(RawEntry.at >= weekago.isoformat()).\
            filter(RawEntry.user == user).\
            query.order_by('at desc').all()

def get_week_hist(user):
    """
    :param user: the user
    creates a dictionary of dates over the last week with lists of
    entries from that day
    :return: a list of tuples (date, list of entries) like
    [(date, [entry1, entry2]), (date2,[...]),...]
    """
    now = datetime.utcnow()
    entries = get_week_list(user)
    dates = [(now.date() - timedelta(days=r)) for r in range(6)]
    week = dict()
    for d in dates:
        week[d] = list()

    for entry in entries:
        week[entry.at.date()].append(entry)

    return [(d, week.get(d)) for d in sorted(week.keys(), reverse=True)]


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), unique=True)
    password_hash = db.Column(db.String(128))

    raw_entries = db.relationship(
        'RawEntry', backref='user', order_by='desc(RawEntry.at)')
    short_preferences = db.relationship('ShortPreference', backref='user')

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


class FoodShort(db.Model):
    __tablename__ = 'food_shorts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    common_long_id = db.Column(
        db.Integer, db.ForeignKey('food_descriptions.id'))

    tags = db.relationship('Tag', backref='food_short')
    short_preferences = db.relationship(
        'ShortPreference', backref='food_short')

    @staticmethod
    def get_or_create(short):
        fs = FoodShort.query.filter(FoodShort.name == short).first()
        if fs is None:
            nearby_foods = fplib.nlp.nearby_food_descriptions(short)
            if len(nearby_foods) > 0:
                fs = FoodShort(name=short, common_long=nearby_foods[0])
            else:
                fs = FoodShort(name=short)
            db.session.add(fs)
            db.session.commit()
        return fs

    @staticmethod
    def get_food(short, user=None):
        fs = FoodShort.get_or_create(short)
        if user is not None:
            pref = ShortPreference.query.filter(ShortPreference.food_short == fs,
                                                ShortPreference.user == user).first()
            if pref is None:
                return fs.common_long
            else:
                return pref.food_description
        else:
            return fs.common_long


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

    shorts = db.relationship('FoodShort', backref='common_long')
    tags = db.relationship('Tag', backref='food_description')
    short_preferences = db.relationship('ShortPreference', backref='food_description')
    measurements = db.relationship('MeasurementWeight', backref='food_description')
    nutrients = db.relationship('NutrientData', backref='food_description')

    def __repr__(self):
        return "<FoodDescription: %s>" % self.long_desc

    
    def get_nutrient_by_group(self, group):
        """ 
        :param group: string contained in the nutrient descriptin 
        :return: all nutrients in this group or lower 
        """
        NDATA = NutrientData
        NDEF = NutrientDefinition
        pairs = db.session.query(NDEF, NDATA).\
                filter(NDEF.group==group).\
                filter(NDATA.nutr_no==NDEF.nutr_no).\
                filter(NDATA.ndb_no==self.id).all()
        return map(lambda i: i[1], pairs)


    def get_nutrient_group(self, measurement_weight=None, group=0):
        """ 
        :param: measurement_weight a MeasurementWeight object to use to 
        calculate the nutrient values, if None, the 100g values are returned
        :param: group list nutrients up to and equal to this group
        """
        
        if measurement_weight == None:
            return None
            


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


class NutrientDefinition(db.Model):
    __tablename__ = 'nutrient_definitions'
    nutr_no = db.Column(db.Integer, primary_key=True)
    units = db.Column(db.String(7))
    tagname = db.Column(db.String(20))
    desc = db.Column(db.String(60))
    num_dec = db.Column(db.String(1))
    sr_order = db.Column(db.String(6))
    group = db.Column(db.Integer)

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
    nutr_no = db.Column(db.Integer, db.ForeignKey('nutrient_definitions.nutr_no'))
    nutr_val = db.Column(db.Float)
    num_data_pts = db.Column(db.Integer)
    std_error = db.Column(db.Float)
    add_nutr_mark = db.Column(db.String(2))
    val_min = db.Column(db.Float)
    val_max = db.Column(db.Float)


    def __repr__(self):
        return '<NutrientData: %s: %s: %s>' % (self.food_description, self.nutrient, self.nutr_val)


    def _html_table_row(self):
        return '<tr><td></td><td></td></tr>'

    def _html_select_item(self):
        return 'todo'

    def from_ndb(self, ndb_row):
        self.ndb_no, self.nutr_no, self.nutr_val, self.num_data_pts, \
            self.std_error, _, _, _, self.add_nutr_mark, _, self.val_min, \
            self.val_max, _, _, _, _, _, _, = ndb_row

        self.ndb_no = int(self.ndb_no)
        self.nutr_no = int(self.nutr_no)
        self.nutr_val = float(self.nutr_val) if self.nutr_val != '' else None
        self.num_data_pts = int(self.num_data_pts)
        self.std_error = float(
            self.std_error) if self.std_error != '' else None
        self.val_min = float(self.val_min) if self.val_min != '' else None
        self.val_max = float(self.val_max) if self.val_max != '' else None

        return self


class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    raw_entry_id = db.Column(db.Integer, db.ForeignKey('raw_entries.id'))
    pos = db.Column(db.Integer)
    text = db.Column(db.String(256))
    food_short_id = db.Column(db.Integer, db.ForeignKey('food_shorts.id'))
    food_description_id = db.Column(db.Integer, db.ForeignKey('food_descriptions.id'))
    count = db.Column(db.Float)
    size = db.Column(db.Float)
    size_units = db.Column(db.String(10))
    measurement_weight_id = db.Column(db.Integer, db.ForeignKey('measurement_weights.id'))

    def __repr__(self):
        return '<Tag: %i %f %s>' % (self.id, self.count or 0, self.text)


class ShortPreference(db.Model):
    __tablename__ = 'short_preferences'
    id = db.Column(db.Integer, primary_key=True)
    food_short_id = db.Column(db.Integer, db.ForeignKey('food_shorts.id'))
    food_description_id = db.Column(
        db.Integer, db.ForeignKey('food_descriptions.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return '<ShortPreference: %s -> %s>' %  \
            (self.food_short.name, self.food_description.long_desc)


class MeasurementWeight(db.Model):
    """ this class helps go between common weights and the 100g values
    in the nutrient database"""
    __tablename__ = 'measurement_weights'
    id = db.Column(db.Integer, primary_key=True)
    ndb_no = db.Column(db.Integer, db.ForeignKey('food_descriptions.id'))
    seq = db.Column(db.Integer)
    amount = db.Column(db.Float)
    description = db.Column(db.String(255))
    gram_weight = db.Column(db.Float)
    num_data_points = db.Column(db.Integer)
    std_dev = db.Column(db.Float)

    def __repr__(self):
        return '<MeasurementWeight: %s of %s weighs %dg>' % \
                (self.description, self.food_description, self.gram_weight)

    
    def from_ndb(self, ndb_row):
        self.ndb_no = int(ndb_row[0])
        self.seq = int(ndb_row[1]) if ndb_row[1] != '' else None
        self.amount = float(ndb_row[2]) if ndb_row[2] != '' else None
        self.description = ndb_row[3]
        self.gram_weight = float(ndb_row[4]) if ndb_row[4] != '' else None
        self.num_data_points = int(ndb_row[5]) if ndb_row[5] != '' else None
        self.std_dev = float(ndb_row[6]) if ndb_row[6] != '' else None

        return self

