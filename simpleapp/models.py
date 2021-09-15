from simpleapp import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from simpleapp import login

from flask_login import UserMixin
sharelist = db.Table('sharelist', 
  db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
  db.Column('package_id', db.Integer, db.ForeignKey('package.id'), primary_key=True)
)
class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key = True)
  username = db.Column(db.String(50), unique=True)
  password = db.Column(db.String(256))
  email = db.Column(db.String(120), index=True, unique=True)
  date_created = db.Column(db.DateTime, default=datetime.now())
  packages = db.relationship("Package", secondary="sharelist", backref=db.backref("packages",lazy=False))
  def __repr__(self):
    return "<User {}>".format(self.username)

  def set_password(self, password):
    self.password = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.password, password)

class Package(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(128))
  date_created = db.Column(db.DateTime, default=datetime.now())
  public = db.Column(db.Integer)
  questions = db.relationship("Question", backref = "package", lazy=False)
  users = db.relationship("User", secondary="sharelist", backref=db.backref("user"), lazy=False)

class Question(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  packageid=db.Column(db.ForeignKey("package.id"))
  type=db.Column(db.String(20))
  prompt = db.Column(db.String(1024))
  answer = db.Column(db.String(1024))





@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def insert_dummy_data(db):
  db.drop_all()
  db.create_all()
  admin = User(username="admin", email="admin@example.com")
  guest = User(username="guest", email="guest@example.com")
  admin.set_password("secretpassword")
  guest.set_password("secretpassword")
  db.session.add(admin)
  db.session.add(guest)
  db.session.commit()

