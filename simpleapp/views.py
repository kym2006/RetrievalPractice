from simpleapp import app, db
from flask import render_template, request, flash, url_for, redirect
import sys 
from simpleapp.forms import SignupForm, TaskForm, LoginForm, DefinitionForm, ExplanationForm, ExampleForm, QuestionForm, SignupForm, AddUserForm
from simpleapp.models import User, Package, Question, sharelist

from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.urls import url_parse
import json

di=dict()
def init(username):
  if username not in di.keys():
    di[username]=dict()
  if("questions" not in di[username].keys()):
    di[username]["questions"]=[] 
  if "name" not in di[username]:
    di[username]["name"] = ""

@app.route('/',methods=["POST","GET"])
@login_required
def index():
  form=AddUserForm()
  if request.method=='GET':
    packages = (User.query.filter_by(id = current_user.id).first()).packages
    for i in packages:
      i.date_created=i.date_created.strftime("%b %d %Y %H:%M")
    return render_template("index.html", packages=packages, form=form)
  else:
    if form.validate_on_submit():
      user=User.query.filter_by(username = form.username.data).first()
      package=Package.query.filter_by(id=form.packageid.data).first()
      user.packages.append(package)

      db.session.commit()
      packages = (User.query.filter_by(id = current_user.id).first()).packages
      return redirect(url_for('index'))
    else: 
      flash("Failure to submit form {}".format(form.errors))

      return redirect(url_for('index'))

@app.route('/revise/<int:packageid>')
@login_required
def revise(packageid):
  packages = (User.query.filter_by(id = current_user.id).first()).packages
  found = 0
  pkg=None
  for i in packages:
    if i.id==packageid:
      found = 1
      pkg=i
  if found:
    for i in pkg.questions:
      if i.type=="example":
        i.answer=i.answer.replace(";", " ")
        print(i.answer)
    for j in pkg.questions:
      print(j.answer)
    return render_template("revise.html", package=pkg)
  else:
    flash("You do not have access to this package!",category="danger")
    return redirect(url_for('index'))

@app.route('/test/<int:packageid>')
@login_required
def test(packageid):
  packages = (User.query.filter_by(id = current_user.id).first()).packages
  found = 0
  pkg=None
  for i in packages:
    if i.id==packageid:
      found = 1
      pkg=i
  if found:
    for i in pkg.questions:
      if i.type=="example":
        i.answer=i.answer.replace(";", " ")
        print(i.answer)
    for j in pkg.questions:
      print(j.answer)
    return render_template("test.html",package=pkg)
  else:
    flash("You do not have access to this package!",category="danger")
    return redirect(url_for('index'))
  
@app.route('/delete/<int:packageid>')
@login_required
def deletepackage(packageid):
  db.session.delete(Package.query.filter_by(id = packageid).first())
  db.session.commit()
  flash("Task deleted successfully", category="success")
  return redirect(url_for("index"))

@app.route('/postname', methods=["POST"])
@login_required
def postname():
  tmp=(request.data.decode('utf-8'))
  tmp=json.loads(tmp)
  x=tmp["value"]
  init(current_user.username)
  di[current_user.username]["name"]=x 
  return "ecksdee"

@app.route('/removelink', methods=["POST"])
@login_required
def removelink():
  tmp=(request.data.decode('utf-8'))
  tmp=json.loads(tmp)
  x=tmp["username"]
  packageid=tmp["packageid"]
  user=User.query.filter_by(username = x).first()
  package=Package.query.filter_by(id=packageid).first()
  user.packages.remove(package)
  db.session.commit()
  return "ecksdee"
  
@app.route('/getpackageprompt', methods=["POST"])
@login_required
def getpackageprompt():
    print("User id:",current_user.id)
    packages = (User.query.filter_by(id = current_user.id).first()).packages
    tmp=(request.data.decode('utf-8'))
    tmp=json.loads(tmp)
    x=tmp["value"]
    pkgid=tmp["pkgid"]
    found = 0
    pkg=None
    for i in packages:
      if i.id==pkgid:
        found = 1
        pkg=i
    if found:
      for i in pkg.questions:
        if i.type=="example":
          i.answer=i.answer.replace(";", " ")
    
    return pkg.questions[x-1].prompt

@app.route('/getpackageanswer', methods=["POST"])
@login_required
def getpackageanswer():
    print("User id:",current_user.id)
    packages = (User.query.filter_by(id = current_user.id).first()).packages
    tmp=(request.data.decode('utf-8'))
    tmp=json.loads(tmp)
    x=tmp["value"]
    pkgid=tmp["pkgid"]
    found = 0
    pkg=None
    for i in packages:
      if i.id==pkgid:
        found = 1
        pkg=i
    if found:
      for i in pkg.questions:
        if i.type=="example":
          i.answer=i.answer.replace(";", " ")
    
    return pkg.questions[x-1].answer



@app.route('/makepackage', methods=["GET", "POST"])
@login_required
def makepackage():
  form = QuestionForm()
  init(current_user.username)
  if request.method=="GET":
    return render_template("makepackage.html", form=form, packagename=di[current_user.username]["name"])
  else:
    print(request.form)
    init(current_user.username)
    if "submitdefinition" in request.form:
       if form.definition.validate(form):
        di[current_user.username]["questions"].append(("definition",request.form["definition-prompt"],request.form["definition-answer"]))
       else:
        flash("Failure to submit form {}".format(form.errors),category="danger")

    elif "submitexample" in request.form:
      if form.example.validate(form):
        print(request.form)
        ans = f'{(request.form["example-object"])};{request.form["example-time"]};{request.form["example-data"]};{request.form["example-action"]}'
        print(ans)
        di[current_user.username]["questions"].append(("example",request.form["example-prompt"],ans))

      else:
        flash("Failure to submit form {}".format(form.errors),category="danger")

    elif "submitexplanation" in request.form:
      if form.explanation.validate(form):
        di[current_user.username]["questions"].append(("explanation",request.form["explanation-prompt"],request.form["explanation-answer"]))
      else:
        flash("Failure to submit form {}".format(form.errors),category="danger")
    else:
      if "name" not in di[current_user.username].keys():
        flash("Fill up the name!",category="danger")
         
      else: 
        newpackage=Package(name=di[current_user.username]["name"], public=0)
        db.session.add(newpackage)
        db.session.commit()
        user = User.query.filter_by(id = current_user.id).first()
        newpackage.users.append(user)
        for qns in di[current_user.username]["questions"]:
          newqns=Question(packageid=newpackage.id,type=qns[0],prompt=qns[1],answer=qns[2])
          db.session.add(newqns)
          db.session.commit() 
        di[current_user.username]["name"]=""
        di[current_user.username]["questions"]=[]

        
    return render_template("makepackage.html", form=form, packagename=di[current_user.username]["name"])


@app.route("/demobootstrap")
def demobootstrap():
  return render_template("demobootstrap.html")

@app.route("/regularform")
def regularform():
  return render_template("regularform.html")

@app.route("/wtform", methods=["GET", "POST"])
@login_required
def wtform():
  form = TaskForm()
  if request.method == "POST":
    if form.validate_on_submit():
      return "Form {} {} {} {}".format(form.name.data, form.description.data, form.completed.data, form.tdate.data)
    else:
      flash("Failure to submit form {}".format(form.errors))
  return render_template("wtform.html", form=form)

@app.route("/login", methods = ["POST", "GET"])
def login():
  form = LoginForm()
  if request.method == "GET":    
    return render_template("login.html", form = form)
  else:
    if form.validate_on_submit():
      user = User.query.filter_by(username = form.username.data).first()
      if user is None: #wrong user
        flash("No such user", category="danger")
        return redirect(url_for('login'))
      elif not user.check_password(form.password.data): #Wrong password
        flash("Wrong Password", category="danger")
        return redirect(url_for('login'))
      else: #authorise login
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
          next_page = url_for('index')
        return redirect(next_page)


@app.route("/signup", methods = ["POST", "GET"])
def signup():
  form = SignupForm()
  if request.method == "GET":    
    return render_template("signup.html", form = form)
  else:
    if form.validate_on_submit():
      user = User(username=form.username.data, email=form.email.data)
      user.set_password(form.password.data)
      db.session.add(user)
      db.session.commit()
      login_user(user, remember=form.remember_me.data)
      next_page = request.args.get("next")
      if not next_page or url_parse(next_page).netloc != "":
        next_page = url_for('index')
      return redirect(next_page)


@app.route("/logout")
def logout():
  logout_user()
  return redirect(url_for("login"))

