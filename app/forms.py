from flask.ext.wtf import Form
from wtforms.fields import StringField, PasswordField, SubmitField, IntegerField
from wtforms.fields import FieldList, FloatField, HiddenField
from wtforms.validators import Required, Email, Length, EqualTo
from app.models import MeasurementWeight, NutrientData, FoodDescription
from app import db


class LoginForm(Form):
    email = StringField('Email', validators=[Required(), Email(), Length(1, 64)])
    password = PasswordField('Password', validators=[Required()])
    submit = SubmitField('Log In')


class SignupForm(Form):
    email = StringField('Email', validators=[Required(), Email(), Length(1, 64)])
    password = PasswordField('Password', validators=[Required()])
    password_verify = PasswordField('Password', validators=[Required(), EqualTo("password")])
    submit = SubmitField('Sign Up')


class FoodEditForm(Form):
    name = StringField('Name', validators=[Required(), Length(1, 255)])
    measure_ids = FieldList(HiddenField('Measure Id'))
    measure_names = FieldList(StringField('Measure Name', 
        validators=[Required(), Length(1, 255)]))
    measure_amounts = FieldList(FloatField('Measure Amount', 
        validators=[Required()]))
    nutrient_names = []
    nutrient_units = []
    nutrient_data_ids = FieldList(HiddenField('Nutrient Data Id'))
    nutrient_amounts = FieldList(FloatField('Nutrient Amount'))
    submit = SubmitField('Save Edits')

    def populate(self, food):
        for ms in food.measurements:
            self.measure_ids.append_entry(ms.id)
            self.measure_names.append_entry(ms.description)
            self.measure_amounts.append_entry(ms.gram_weight)
        for nut_data in food.nutrients:
            self.nutrient_names.append(nut_data.nutrient.desc)
            self.nutrient_units.append(nut_data.nutrient.units)
            self.nutrient_data_ids.append_entry(nut_data.id)
            self.nutrient_amounts.append_entry(nut_data.nutr_val)


    def update_models(self, food):
        """ updates the models for a submitted form"""

        food.long_desc = self.name.data

        existing_measure_ids = set(map(lambda x: x.id, food.measurements))
        received_measure_ids = set(map(lambda x: x.data, self.measure_ids))

        print "existing", existing_measure_ids
        print "received" , received_measure_ids

        for i in range(len(self.measure_ids)):
            id = self.measure_ids[i].data

            if len(id) == 0:
                ms = MeasurementWeight()
                ms.food_description = food
                db.session.add(ms)
            else:
                ms = MeasurementWeight.query.get(id)

            name = self.measure_names[i].data
            weight = float(self.measure_amounts[i].data)

            ms.description = name
            ms.gram_weight = weight

        for i in range(len(self.nutrient_data_ids)):
            id = self.nutrient_data_ids[i].data
            amount = self.nutrient_amounts[i].data

            nut_data = NutrientData.query.get(id)
            nut_data.nutr_val = float(amount)

        db.session.commit()

