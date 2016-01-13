from flask.ext.wtf import Form
from wtforms.fields import StringField, PasswordField, SubmitField, IntegerField
from wtforms.fields import FieldList, FloatField, HiddenField
from wtforms.widgets import TextArea
from wtforms.validators import Required, Email, Length, EqualTo


class LoginForm(Form):
    email = StringField('Email', validators=[Required(), Email(), Length(1, 64)])
    password = PasswordField('Password', validators=[Required()])
    submit = SubmitField('Log In')


class CreateRawEntryForm(Form):
    content = StringField('Content', validators=[
                        Required(), Length(1, 1000)], widget=TextArea())
    submit = SubmitField('Submit')


class AddShortPreference(Form):
    food_short = StringField('Short', validators=[Required(), Length(1, 255)])
    food_id = StringField('Food Desc id', validators=[Required()])
    submit = SubmitField('Submit')


class CreateTag(Form):
    food_id = IntegerField('Food Id', validators=[Required()])
    submit = SubmitField('Add')


class SignupForm(Form):
    email = StringField('Email', validators=[Required(), Email(), Length(1, 64)])
    password = PasswordField('Password', validators=[Required()])
    password_verify = PasswordField('Password', validators=[Required(), EqualTo("password")])
    submit = SubmitField('Sign Up')


class FoodEditForm(Form):
    measure_names = FieldList(StringField('Measure Name', 
        validators=[Required(), Length(1, 255)]))
    measure_amounts = FieldList(FloatField('Measure Amount', 
        validators=[Required()]))
    nutrient_ids = FieldList(HiddenField('Nutrient Id'))
    nutrient_amounts = FieldList(FloatField('Nutrient Amount'))
    submit = SubmitField('Save Edits')

    def populate(self, food):
        for ms in food.measurements:
            self.measure_names.append_entry(ms.description)
            self.measure_amounts.append_entry(ms.gram_weight)
        for nut_data in food.nutrients:
            self.nutrient_ids.append_entry(nut_data.nutr_no)
            self.nutrient_amounts.append_entry(nut_data.nutr_val)


