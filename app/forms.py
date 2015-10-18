from flask.ext.wtf import Form
from wtforms.fields import TextField, PasswordField, SubmitField
from wtforms.validators import Required, Email, Length

class LoginForm(Form):
    email = TextField('Email', validators=[Required(), Email(), Length(1, 64)])
    password = PasswordField('Password', validators=[Required()])
    submit = SubmitField('Log In')

class ImportFromTwitterForm(Form):
  screen_name = TextField('Screen Name', validators=[Required(), Length(1, 255)])
  submit = SubmitField('Import')

