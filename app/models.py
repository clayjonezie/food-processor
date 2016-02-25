from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin
from datetime import datetime, timedelta
from fuzzywuzzy import fuzz
from flask import render_template
from datetime import datetime, timedelta

from . import db
from . import login_manager
from . import fplib


def get_week_days(user):
    """
    :param user: the user whos days we want
    creates a list of (dates, list of tags) over the last week with lists of
    tags from that day.
    :return: a list of tuples:
    [(date, list of tags, [list of (nutr def, nutr val)]), ...]
    """
    now = datetime.utcnow()
    dates = [(now.date() - timedelta(days=r)) for r in range(7)]
    week = list()
    for d in dates:
        tags = Tag.get_day(user, d)
        week.append((d, tags, FoodDescription.sum_nutrients(tags)))

    return week


def get_day_goals(user, day=None, graph_only=False):
    """
    returns a list of tuples of the form
    (NutrDef, percent complete, current amount, goal amount)
    :param user: the user
    :param day: (a datetime.date object)
    :param graph_only: True means filter by NutrientGoal.show_on_graph
    """
    if day is None:
        day = datetime.now().date()
    tags = Tag.get_day(user, day)
    nuts = FoodDescription.sum_nutrients(tags, group=None)

    goals = list()
    for nut in nuts:
        nutdef = nut[0]
        goal = user.get_goal(nutdef)
        if goal is not None and (graph_only is False or goal.show_on_graph):
            current_amount = nut[1]
            if goal.amount > 0:
                percent = current_amount / goal.amount
            else:
                if current_amount > 0:
                    percent = 1.0
                else:
                    percent = 0
            goals.append((nutdef, percent, current_amount, goal.amount))

    goals.sort(key=lambda x: x[0].nutr_no)
    return goals


food_description_owner_table = db.Table('food_owners', db.metadata, db.Column('food_description_id', db.Integer,
                                                                              db.ForeignKey('food_descriptions.id')),
                                        db.Column('user_id', db.Integer, db.ForeignKey('users.id')))


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), unique=True)
    password_hash = db.Column(db.String(128))

    tags = db.relationship('Tag', backref='user')
    nutrient_goals = db.relationship('NutrientGoal', backref='user')
    foods = db.relationship('FoodDescription', 
            secondary=food_description_owner_table, 
            back_populates='owners')

    @property
    def password(self):
        raise AttributeError("Password is not stored")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_goal(self, nutrient_definition):
        """
        :param nutrient_definition: the NutrientDefinition object to get the
        goal
        :return: the amount of this user's goal for that nutrient, or None
        :rtype: float or None
        """
        ng = NutrientGoal.query.\
            filter(NutrientGoal.nutrient_id == nutrient_definition.nutr_no).\
            filter(NutrientGoal.user_id == self.id).first()

        return ng

    def get_all_goals(self):
        """
        :return: a list of goals with the unset ones as zero
        """
        goals = NutrientGoal.query.filter(NutrientGoal.user_id==self.id).all()
        goal_set_nutrients = [g.nutrient for g in goals]
        nutrients = NutrientDefinition.query.all()
        for nut in nutrients:
            if nut not in goal_set_nutrients:
                goals.append(NutrientGoal(0, self, nut))
        return goals

    def get_suggestions(self, dt=None, lim=10):
        '''
        :param date: The datetime to get suggestions for
        :return: a list of tags which are likely to be chosen
        '''
        if dt is None:
            dt = datetime.now()

        # get all the foods this person consumes, and a count with it from sql

        conn = db.session.connection()
        foods = conn.execute(db.text("select food_descriptions.id, "
                                     "    food_descriptions.long_desc,"
                                     "    count(food_descriptions.id) as cnt "
                                     "FROM food_descriptions "
                                     "INNER JOIN tags "
                                     "    ON tags.food_description_id = food_descriptions.id "
                                     "INNER JOIN users "
                                     "    ON users.id = tags.user_id "
                                     "WHERE users.id = :uid "
                                     "GROUP BY food_descriptions.id "
                                     "ORDER BY cnt DESC limit :limit;"),
                             uid=self.id, limit=lim).fetchall()


        # this should be pushed to sql. finds the most recent count and measure for each
        results = []
        for foodid, food_desc, food_count in foods:
            (count, measure_id, measure_desc) = db.session.query(Tag.count,
                                                                 Tag.measurement_weight_id,
                                                                 MeasurementWeight.description)\
                .outerjoin(User).outerjoin(MeasurementWeight)\
                .filter(Tag.food_description_id == foodid)\
                .filter(User.id == self.id).order_by(Tag.at.desc()).first()

            results.append({'food_id': foodid, 'food_desc': food_desc, 'count': count,
                            'measure_id': measure_id, 'measure_desc': measure_desc})

        return results

    def get_plan(self):
        mealplans = MealPlan.query.filter(MealPlan.user_id==self.id).all()
        return mealplans


    def __repr__(self):
        return '<User: %s>' % self.email


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


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

    tags = db.relationship('Tag',
                           backref='food_description')
    short_preferences = db.relationship('ShortPreference',
                                        backref='food_description')
    measurements = db.relationship('MeasurementWeight',
                                   backref='food_description')
    nutrients = db.relationship('NutrientData',
                                backref='food_description')
    owners = db.relationship('User', secondary=food_description_owner_table,
            back_populates='foods')


    def __init__(self):
        """ in __init__ we will create empty nutrient info (0.0) """
        db.session.add(self)
        db.session.commit()
        nut_defs = NutrientDefinition.query.all()
        for nd in nut_defs:
            nut_data = NutrientData()
            nut_data.nutr_val = 0.0
            nut_data.nutr_no = nd.nutr_no
            nut_data.ndb_no = self.id
            db.session.add(nut_data)

        db.session.commit()

    def serializable(self):
        return {'description': self.common_name,
                'id': self.id}

    def __repr__(self):
        return "<FoodDescription: %s>" % self.long_desc

    def get_nutrients_by_group(self, group=1, measurement=None, count=1):
        """
        :param group: what group to gather, None means all groups
        :param measurement: the measurement to use to calculate things
        :return: list of pairs in the form of
        [(NutrientDefintion, scaled_float_nutr_value), ...]

        nutrient data is on a 100g scale, so we must scale to the measurement
        scaled_nutrient = nutrient_in_100g * grams_in_measurement / 100g
        """
        NDATA = NutrientData
        NDEF = NutrientDefinition
        query = db.session.query(NDEF, NDATA).\
            filter(NDATA.nutr_no == NDEF.nutr_no).\
            filter(NDATA.ndb_no == self.id)

        if group is not None:
            query = query.filter(NDEF.group == group)

        pairs = query.all()

        def calculate(original):
            if measurement is not None:
                return (original[0],
                        count * measurement.gram_weight *
                        original[1].nutr_val / 100)
            else:
                return original[0], count * original[1].nutr_val

        return map(calculate, pairs)

    def best_measurement(self, entry_hint=None):
        if len(self.measurements) == 0:
            return None

        favor = ["nlea", "bunch", "whole", "medium", "cup"]
        if entry_hint is not None:
            favor.insert(0, entry_hint.lower())

        for f in favor:
            for ms in self.measurements:
                if f in ms.description.lower():
                    return ms
    
        # couldn't find any
        return self.measurements[0]

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


    @staticmethod
    def sum_nutrients(tags, group=1):
        """
        :param list foods: a list of tags to be summed
        :return: list of pairs in the form of 
        [(NutrientDefintion, summed_float_nutr_value), ...]
        """
        summed_nuts = dict()
        for n in NutrientDefinition.get_group(group):
            summed_nuts[n] = 0.0

        for t in tags:
            if t.food_description is not None:
                nuts = t.food_description.get_nutrients_by_group(
                        group=group, measurement=t.measurement, count=t.count)
                for n in nuts:
                    if n[0] in summed_nuts.keys():
                        summed_nuts[n[0]] += n[1]

        return summed_nuts.items()


    @staticmethod
    def get(item):
        if isinstance(item, str):
            return FoodDescription.get_by_long_desc(item)
        if isinstance(item, int):
            return FoodDescription.query.get(item)


    @staticmethod
    def get_by_long_desc(long_desc):
        FD = FoodDescription
        return FD.query.filter(FD.long_desc==long_desc).first()


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
    nutrient_goals = db.relationship('NutrientGoal', backref='nutrient')

    def __repr__(self):
        return "<NutrientDefinition: %s, %s>" % (self.desc, self.units)

    def from_ndb(self, ndb_row):
        self.nutr_no, self.units, self.tagname, self.desc, \
            self.num_dec, self.sr_order = ndb_row
        self.nutr_no = int(self.nutr_no)
        return self


    @staticmethod
    def get_group(group):
        if group is None:
            return NutrientDefinition.query.all()
        else:
            return NutrientDefinition.query.\
                    filter(NutrientDefinition.group==group).all()


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
        return '<NutrientData: %s: %s: %s>' % (self.food_description,
                                               self.nutrient, self.nutr_val)


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
    pos = db.Column(db.Integer)
    text = db.Column(db.String(256))
    food_description_id = db.Column(db.Integer, db.ForeignKey('food_descriptions.id'))
    count = db.Column(db.Float)
    size = db.Column(db.Float)
    size_units = db.Column(db.String(10))
    measurement_weight_id = db.Column(db.Integer, db.ForeignKey('measurement_weights.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    at = db.Column(db.DateTime)

    def __repr__(self):
        return '<Tag: %s %f %s %s>' % (str(self.id), self.count or 0,
                                       self.food_description.long_desc,
                                       self.measurement.description)

    def serializable(self):
        return {'id': self.id,
                'food': {'id': self.food_description_id,
                         'description': self.food_description.long_desc},
                'count': self.count,
                'measure': {'id': self.measurement_weight_id,
                            'description':
                                self.measurement.description
                                if self.measurement is not None
                                else None},
                'at': self.at.isoformat()}

    @staticmethod
    def get_week(user):
        """
        :param user: the user
        creates a dictionary of dates over the last week with lists of
        tags from that day
        :return: a list of dicts {date, list of tags}
        """
        now = datetime.utcnow()
        weekago = now - timedelta(days=6)
        tags = Tag.query.filter(Tag.at >= weekago.isoformat()).\
            filter(Tag.at <= now.isoformat()).\
            filter(Tag.user == user).\
            order_by('at desc').all()
        dates = [(now.date() - timedelta(days=r)) for r in range(7)]
        week = dict()
        for d in dates:
            week[d] = list()
        for tag in tags:
            week[tag.at.date()].append(tag)
        return [{'date': d, 'tags': week.get(d)}
                for d in sorted(week.keys(), reverse=True)]

    @staticmethod
    def get_day(user, start):
        """ returns all tags from a day for a user """
        end = start + timedelta(days=1)
        tags = Tag.query.filter(Tag.user_id == user.id).\
            filter(Tag.at >= start.isoformat()).\
            filter(Tag.at <= end.isoformat()).all()
        return tags


class ShortPreference(db.Model):
    __tablename__ = 'short_preferences'
    id = db.Column(db.Integer, primary_key=True)
    food_short_id = db.Column(db.Integer, db.ForeignKey('food_shorts.id'))
    food_description_id = db.Column(
        db.Integer, db.ForeignKey('food_descriptions.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        if self.food_short is not None:
            food_short_name = self.food_short.name
        else:
            food_short_name = 'None (error?)'

        if self.food_description is not None:
            food_description_name = self.food_description.long_desc
        else:
            food_description_name = 'None (error?)'

        food_description_desc = 'None'
        return '<ShortPreference: %s -> %s>' %  \
            (food_short_name, food_description_name)


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

    tags = db.relationship('Tag', backref='measurement')

    def __repr__(self):
        return '<MeasurementWeight: %d %s of %s weighs %dg>' % \
                (self.amount, self.description, 
                        self.food_description, self.gram_weight)

    def from_ndb(self, ndb_row):
        self.ndb_no = int(ndb_row[0])
        self.seq = int(ndb_row[1]) if ndb_row[1] != '' else None
        self.amount = float(ndb_row[2]) if ndb_row[2] != '' else None
        self.description = ndb_row[3]
        self.gram_weight = float(ndb_row[4]) if ndb_row[4] != '' else None
        self.num_data_points = int(ndb_row[5]) if ndb_row[5] != '' else None
        self.std_dev = float(ndb_row[6]) if ndb_row[6] != '' else None

        return self

    def serializable(self):
        return {'description': self.description,
                'id': self.id}


class NutrientGoal(db.Model):
    """
    A goal for a specific user and a nutrient
    """
    __tablename__ = 'nutrient_goals'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    nutrient_id = db.Column(db.Integer, db.ForeignKey('nutrient_definitions.nutr_no'))
    show_on_graph = db.Column(db.Boolean)

    def __init__(self, amount, user, nutrient):
        self.amount = amount
        self.user = user
        self.nutrient = nutrient
        self.show_on_graph = False


meal_plan_weekdays = db.Table('meal_plan_weekdays', db.metadata,
                              db.Column('meal_plan_id', db.Integer, db.ForeignKey('meal_plans.id')),
                              db.Column('weekday_id', db.Integer, db.ForeignKey('weekdays.id')))


class MealPlan(db.Model):
    """
    Represents a plan to have a meal (currently repeating weekly)
    """
    __tablename__ = 'meal_plans'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    meal_time = db.Column(db.String(50))
    weekdays = db.relationship('Weekday', secondary=meal_plan_weekdays)
    food_id = db.Column(db.Integer, db.ForeignKey('food_descriptions.id'))
    measure_id = db.Column(db.Integer, db.ForeignKey('measurement_weights.id'))
    count = db.Column(db.Float)

    def serializable(self):
        return {'id': self.id,
                'meal_time': self.meal_time,
                'weekdays': [w.serializable() for w in self.weekdays],
                'food': FoodDescription.query.get(self.food_id).serializable(),
                'measure': MeasurementWeight.query.get(self.measure_id).serializable(),
                'count': self.count}


class Weekday(db.Model):
    """
    a single weekday with iso8601 ordering for the ids, M=1 Sun=7
    """
    __tablename__ = 'weekdays'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(10))

    def serializable(self):
        return {'description': self.description,
                'id': self.id}

    def __repr__(self):
        return "<%s >" % self.description
