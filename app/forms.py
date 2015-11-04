from flask.ext.wtf import Form
from wtforms.fields import TextField, PasswordField, SubmitField
from wtforms.widgets import TextArea
from wtforms.validators import Required, Email, Length

class LoginForm(Form):
    email = TextField('Email', validators=[Required(), Email(), Length(1, 64)])
    password = PasswordField('Password', validators=[Required()])
    submit = SubmitField('Log In')

class CreateRawEntryForm(Form):
    content = TextField('Content', validators=[Required(), Length(1, 1000)], widget=TextArea())
    submit = SubmitField('Submit')

class AddShortPreference(Form):
    food_short = TextField('Short', validators=[Required(), Length(1, 255)])
    food_id = TextField('Food Desc id', validators=[Required()])
    submit = SubmitField('Submit')

