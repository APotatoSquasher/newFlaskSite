from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
# Creates a Flask Instance
app = Flask(__name__)
#Add database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password123!@localhost/our_users'

app.config['SECRET_KEY'] = "test case i know this is public"
# initalize database
db = SQLAlchemy(app)


# Create Model
class Users(db.Model):
    # creates id, name, email, and date for each person. Primary key automatically makes the id
    id= db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(200),nullable=False) #200 is the max amount of string. Cannot be nothing as per nullable=False
    email=db.Column(db.String(120),nullable=False,unique=True) #only one email per user allowed due to unique=
    date_added=db.Column(db.DateTime, default=datetime.now) # puts current date when they fill out the form
    # Creates a String
    def __repr__(self):
        return '<Name %r>' % self.name
# Creates a Form class
class UserForm(FlaskForm):
    name=StringField("Name: ",validators=[DataRequired()])
    email=StringField("Email: ",validators=[DataRequired()])
    submit=SubmitField("Submit")
# Update database
@app.route('/update/<int:id>',methods=['GET','POST'])
def update(id): # Is <int:id> in this case
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name'] # Getting name and email of the previously submitted form
        name_to_update.email = request.form['email']
        try:
            db.session.commit() # Database can submit name_to_update because it accesses Users, the database
            flash("User Updated Successfully")
            return render_template("update.html",form=form,name_to_update=name_to_update)
        except:
            flash("Error!")
    else:
        return render_template("update.html",form=form,name_to_update=name_to_update)
class NamerForm(FlaskForm):
    # StringField is the box where you type in things. If you didn't fill out the form,
    # validator will pop up and say you didn't fill out the form, datarequired just checks if you put anything in
    # submit is a button that sends the info
    name=StringField("What's Your name?",validators=[DataRequired()])
    submit=SubmitField("Submit")
    #there are many other fields, like BooleanField, DateTimeField, PasswordField, etc.
# Creates a route decorator
if __name__ == "__main__":
    app.run(debug=False) # this runs
@app.route('/user/add',methods=['GET','POST'])
def add_user():
    name=None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first() # Grabs all emails with what was typed in and get the first one. There shouldn't be any, it should return None
        if user is None:
            user= Users(name=form.name.data,email=form.email.data) # sets user to the name and email given
            db.session.add(user) # adds user to the database
            db.session.commit() # commits it
        name = form.name.data 
        form.name.data = "" # Resets the name and email back
        form.email.data = ""
        flash("Welcome to my blog!")
    our_users= Users.query.order_by(Users.date_added) # Gets a list of users by date added
    return render_template("add_user.html",form=form,name=name,our_users=our_users)
@app.route('/')
def index(): #Accessed from the home button and is by default, look in navbar.html (done via {{ url_for('')) }}
    stuff="Homepage"
    toppings=["Cheese","Olives","Pepper",3,15]
    return render_template("index2.html",stuff=stuff,pizza_toppings=toppings)
# localhost:5000/user/John
@app.route('/user/<name>')
def user(name):
    return render_template("index1.html",username=name) #username is the varibale used in index1.html 'name' is the paramater getting passed based on /<name>
@app.route('/info')
def info():
    return "<h1> This is the info page! This is the start of my passion project! Now there's problems, so im sad :(</h1>"
#jinja funcs that are after a |. safe=Allows tages like </strong> to actually work. There is upper,lower,capitalize, title (capitalizes 1st of each letter),
#striptags removes tags. trim removes the last spaces in a sentence.
#You can also access a list item by using. for example: pizzatoppings.0

#Create invalid URL page, it MUST be in this format
@app.errorhandler(404)
def PageNotFound(error):
    return render_template('404.html'), 404
#Creates page for server error
@app.errorhandler(500)
def Bug(error):
    return render_template('500.html'), 500
@app.route('/signin',methods=['GET','POST']) #POST is when you submit something
def SignIn():
    name=None #name is None unless the user submits something
    form = NamerForm() #References the class above NamerForm()
    if form.validate_on_submit(): #Validates form by taking what ever name is on the text box
        # and resetting the box
        name=form.name.data
        form.name.data=''
        flash('Form Submitted Successfully')# flashes a message from the imported flash library
    return render_template('name.html',name=name,form=form) #passes variables to name.html