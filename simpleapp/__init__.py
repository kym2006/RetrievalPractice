from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


app = Flask(__name__)
Bootstrap(app)

app.secret_key = "thisisasecret"

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///app.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
db = SQLAlchemy(app)
db.engine.dialect.supports_sane_rowcount = db.engine.dialect.supports_sane_multi_rowcount = False # mysql bug wth outdated library outdated database what is this

login = LoginManager(app)
login.login_view = "login"
login.login_message = "You will need to login before accesing this top secret material!"
login.login_message_category = "danger"

from simpleapp import views, models

@app.cli.command("initdb")
def reset_db():
  ''' Reset the database with dummy data '''
  db.drop_all()
  db.create_all()
  models.insert_dummy_data(db)