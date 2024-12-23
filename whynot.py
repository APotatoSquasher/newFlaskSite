from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import os
# Creates a Flask Instance
app = Flask(__name__)
app.config['SECRET_KEY'] = "test case i know this is public"
# Creates a Form class
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
@app.route('/')
def index(): #Accessed from the home button and is by default, look in navbar.html (done via {{ url_for('')) }}
    stuff="Chat this is NOT a good idea!"
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