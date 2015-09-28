from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from database import db_session

from forms import EmailPasswordForm

SQLALCHEMY_DATABASE_URI = "sqlite:////var/www/foodprocessor/foodprocessor.db"

app = Flask(__name__)
db = SQLAlchemy(app)


@app.route("/")
def home():
  return render_template("home.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    form = EmailPasswordForm()
    if form.validate_on_submit():
        return redirect(url_for('home'))
    else:
        return render_template('login.html', form=form)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


if __name__ == "__main__":
  app.run()
