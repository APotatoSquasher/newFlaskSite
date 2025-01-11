from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from sqlalchemy.inspection import inspect
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.widgets import TextArea
# Creates a Flask Instance
app = Flask(__name__)
#Add database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password123!@localhost/our_users'

app.config['SECRET_KEY'] = "test case i know this is public"
# initalize database
db = SQLAlchemy(app)
migrate = Migrate(app,db,compare_type=True,render_as_batch=True)
#Create a Blog Post Model
class Posts(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime,default=datetime.now)
    slug=db.Column(db.String(255)) #Changes url from number to a title
# Creates a Post Form
class PostForm(FlaskForm):
    title=StringField("Title: ",validators=[DataRequired()])
    content=StringField("Content: ",validators=[DataRequired()],widget=TextArea())
    author=StringField("Author: ",validators=[DataRequired()])
    slug=StringField("Alternate URL: ",validators=[DataRequired()])
    submit=SubmitField("Submit")
@app.route('/posts')
def posts():
    # Grab all posts from the database
    posts=Posts.query.order_by(Posts.date_posted)
    return render_template('posts.html',posts=posts)
@app.route('/posts/<int:id>') # <int:id> would be like posts/1
def post(id):
    post=Posts.query.get_or_404(id)
    return render_template('post.html',post=post)
@app.route('/posts/edit/<int:id>',methods=['GET','POST']) #Use the methods when you want to get or submit info
def edit_post(id):
    post=Posts.query.get_or_404(id)
    form=PostForm()
    if form.validate_on_submit():
        # Makes title from form to title in database
        post.title=form.title.data
        post.author=form.author.data
        post.slug=form.slug.data
        post.content=form.content.data
        # Update Database
        db.session.add(post)
        db.session.commit()
        flash("Post Has Been Updated!")
        return redirect(url_for('posts',id=post.id))
    form.title.data=post.title # Autofills sections of form from database
    form.author.data=post.author
    form.slug.data=post.slug
    form.content.data=post.content
    return render_template('edit_post.html',form=form)
# Add Post Page
@app.route('/add-post',methods=['GET','POST'])
def add_post():
    form=PostForm()
    if form.validate_on_submit(): # If all of the forms have info in them, and is submitted, then do...
        post=Posts(title=form.title.data,content=form.content.data,slug=form.slug.data,author=form.author.data) #Makes new row of Posts
        form.title.data=''
        form.content.data=''
        form.author.data=''
        form.slug.data=''
        #Add post data to database
        db.session.add(post)
        db.session.commit()
        flash("You have succesfully made a blog post!")
    #Redirect to webpage
    return render_template("add_post.html",form=form)
# Create Model
class Users(db.Model):
    # creates id, name, email, and date for each person. Primary key automatically makes the id
    id= db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(200),nullable=False) #200 is the max amount of string. Cannot be nothing as per nullable=False
    email=db.Column(db.String(120),nullable=False,unique=True) #only one email per user allowed due to unique=
    favorite_food=db.Column(db.String(150))
    date_added=db.Column(db.DateTime, default=datetime.now) # puts current date when they fill out the form
    # do password stuff
    password_hash = db.Column(db.String(120))
    @property
    def password(self): # We define the password here
        raise AttributeError('Password is not a readable attributle!')
    @password.setter
    def password(self, password): #We take the password to make a hash
        self.password_hash = generate_password_hash(password)
    def verify_password(self, password): # It checks if the password is correct
        return check_password_hash(self.password_hash,password)
    # Creates a String
    def __repr__(self):
        return '<Name %r>' % self.name
# Creates a Form class
class UserForm(FlaskForm):
    name=StringField("Name: ",validators=[DataRequired()])
    email=StringField("Email: ",validators=[DataRequired()])
    password_hash = PasswordField("Password: ",validators=[DataRequired(),EqualTo('password_hash2',message='Password Must Match!')])
    password_hash2 = PasswordField("Confirm Password: ",validators=[DataRequired()]) # This doesn't need a EqualTo() because the first one must match with this one
    favorite_food = StringField("Favorite Food: ")
    submit=SubmitField("Submit")
# Update database
@app.route('/update/<int:id>',methods=['GET','POST'])
def update(id): # Is <int:id> in this case
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name'] # Getting name and email of the previously submitted form
        name_to_update.email = request.form['email']
        name_to_update.favorite_food = request.form['favorite_food']
        try:
            db.session.commit() # Database can submit name_to_update because it accesses Users, the database
            flash("User Updated Successfully")
            return render_template("update.html",form=form,name_to_update=name_to_update)
        except:
            flash("Error!")
    else:
        return render_template("update.html",form=form,name_to_update=name_to_update)
class PasswordForm(FlaskForm):
    email= StringField("What is your email? ",validators=[DataRequired()])
    password_hash=PasswordField("What is your password? ",validators=[DataRequired()])
    submit=SubmitField("Submit")
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
            # Hash the password in the sha356 method
            hashed_pw=generate_password_hash(form.password_hash.data,"pbkdf2:sha256")
            user= Users(name=form.name.data,email=form.email.data,favorite_food=form.favorite_food.data,password_hash=hashed_pw) # sets user to the name and email given
            db.session.add(user) # adds user to the database
            db.session.commit() # commits it
        else:
            flash("This name is already in use!")
        name = form.name.data 
        form.name.data = "" # Resets the name and email back
        form.email.data = ""
        form.favorite_food.data = ""
        form.password_hash.data = ""
        flash("Welcome to my blog!")
    our_users= Users.query.order_by(Users.date_added) # Gets a list of users by date added
    return render_template("add_user.html",form=form,name=name,our_users=our_users)
@app.route('/delete/<int:id>')
def delete(id): #Taking id from <int:id>
    name=None
    form=UserForm()
    our_users= Users.query.order_by(Users.date_added)
    user_to_delete = Users.query.get_or_404(id) #Retrives row of person by ID
    try:
        db.session.delete(user_to_delete) #deletes user
        db.session.commit()
        flash("User Deleted Successfully")
        return render_template('add_user.html',form=form,name=name,our_users=our_users)
    except:
        flash("There was a problem. Check if this user actually exists.")
        return render_template('add_user.html',form=form,name=name,our_users=our_users)
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
@app.route('/test_pw',methods=['GET','POST']) #POST is when you submit something
def test_pw():
    email=None
    password=None
    pw_to_check=None
    passed=None #passed is whether the password is correct
    name=None #name is None unless the user submits something
    form = PasswordForm() #References the class above NamerForm()
    if form.validate_on_submit(): #Validates form by taking what ever name is on the text box
        # Get email and password
        email=form.email.data
        password=form.password_hash.data
        #Clear the form
        form.email.data=''
        form.password_hash.data=''
        pw_to_check=Users.query.filter_by(email=email).first() #lookup user
        #Check Hashed PAssword
        if pw_to_check != None:
            flash("Hey!")
        passed = check_password_hash(pw_to_check.password_hash,password)

        #flash('Form Submitted Successfully')# flashes a message from the imported flash library
    return render_template('test_pw.html',email=email,form=form,password=password,pw_to_check=pw_to_check,passed=passed) #passes variables to name.html
