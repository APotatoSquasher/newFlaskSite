from flask import Flask, render_template, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from sqlalchemy.inspection import inspect
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from webforms import *
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid as uuid
import os

# Creates a Flask Instance
app = Flask(__name__)
#Add CKEditor
ckeditor = CKEditor(app)
#Add database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password123!@localhost/our_users'

app.config['SECRET_KEY'] = "test case i know this is public"
UPLOAD_FOLDER = 'static/images/' # Where the images are stored
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# initalize database
db = SQLAlchemy(app)
migrate = Migrate(app,db,compare_type=False,render_as_batch=True)
#Create a Blog Post Model
#Flask Login Stuff
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='login' #redirects user to login.html if not logged in
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))
#Pass stuff into navbar by putting it into base.html, which includes navbar.html
@app.context_processor
def base():
    form=SearchForm()
    return dict(form=form)
#Create Admin Page
@app.route('/admin')
@login_required
def admin():
    id=current_user.id
    return render_template("admin.html",id=id)
@app.route('/search',methods=["POST"])
def search():
    form = SearchForm()
    #Get data from submitted form
    if form.validate_on_submit():
        post.searched=form.searched.data
        #Query the database
        #posts=posts.filter(Posts.content)
        return render_template("search.html",form=form,searched=post.searched)
    else:
        flash("Please enter a search term!")
        return "<h11>Invalid form</h1>"
#create login page
@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user= Users.query.filter_by(username=form.username.data).first() # grab first instance of username in the database from the form
        if user:
            #Check the hash
            if check_password_hash(user.password_hash,form.password.data): # Returns true if the password from the form matcehs the hash
                login_user(user) #Logs user in
                return redirect(url_for('dashboard'))
            else:
                flash("Password is incorrect. Please try again!")
        else:
            flash("That user doesn't exist. Please try again! ")
    return render_template('login.html',form=form)
#Create Log Out Page
@app.route('/logout',methods=['GET','POST'])
@login_required
def logout():
    logout_user() #Flask_login already has a function for logging someone out
    flash("You have been logged out.")
    return redirect(url_for('login'))
@app.route('/dashboard',methods=['GET','POST'])
@login_required #must be logged in to view dashboard
def dashboard():
    form = LoginForm()
    return render_template('dashboard.html')
class Users(db.Model,UserMixin):
    # creates id, name, email, and date for each person. Primary key automatically makes the id
    id= db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(20))
    name=db.Column(db.String(200),nullable=False) #200 is the max amount of string. Cannot be nothing as per nullable=False
    email=db.Column(db.String(120),nullable=False,unique=True) #only one email per user allowed due to unique=
    favorite_food=db.Column(db.String(150))
    about_author=db.Column(db.Text(500),nullable=True)
    date_added=db.Column(db.DateTime, default=datetime.now) # puts current date when they fill out the form
    profile_pic=db.Column(db.String(150),nullable=True)
    # do password stuff
    password_hash = db.Column(db.String(120))
    posts=db.relationship('Posts',backref='poster')
    # User can have many posts
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
    
class Posts(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    #author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime,default=datetime.now)
    slug=db.Column(db.String(255)) #Changes url from number to a title
    #Foreign Key to Link Users (refer to primary key)
    poster_id=db.Column(db.Integer, db.ForeignKey('users.id'))
    # User can have many posts (one to many posts)
# Creates a Post Form

@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    pid=current_user.id
    try:
        if pid == post_to_delete.poster.id or post_to_delete == None or pid == 12:
            try:
                db.session.delete(post_to_delete) #deletes post
                db.session.commit()
                posts=Posts.query.order_by(Posts.date_posted)
                flash("Blog post was deleted.")
                return render_template('posts.html',posts=posts)
            except:
                posts=Posts.query.order_by(Posts.date_posted)
                flash("Blog does not exist or an error may have occured.")
                return render_template('posts.html',posts=posts)
        else:
            posts=Posts.query.order_by(Posts.date_posted)
            flash("Blog does not exist or an error may have occured.")
            return render_template('posts.html',posts=posts)         
    except AttributeError:
        posts=Posts.query.order_by(Posts.date_posted)
        flash("You cannot delete this post!")
        return render_template('posts.html',posts=posts)         
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
@login_required
def edit_post(id):
    post=Posts.query.get_or_404(id)
    form=PostForm()
    if form.validate_on_submit():
        # Makes title from form to title in database
        post.title=form.title.data
        #post.author=form.author.data
        post.slug=form.slug.data
        post.content=form.content.data
        # Update Database
        db.session.add(post)
        db.session.commit()
        flash("Post Has Been Updated!")
        return redirect(url_for('posts',id=post.id))
    if current_user.id == post.poster_id or current_user.id == 12:
        form.title.data=post.title # Autofills sections of form from database
        #form.author.data=post.author
        form.slug.data=post.slug
        form.content.data=post.content
        return render_template('edit_post.html',form=form)
    else:
        flash("You aren't authorized to edit this post.")
        post=Posts.query.get_or_404(id)
        return render_template('post.html',post=post)
# Add Post Page
@app.route('/add-post',methods=['GET','POST'])
@login_required
def add_post():
    form=PostForm()
    if form.validate_on_submit(): # If all of the forms have info in them, and is submitted, then do...
        poster=current_user.id
        post=Posts(title=form.title.data,content=form.content.data,slug=form.slug.data,poster_id=poster) #Makes new row of Posts
        form.title.data=''
        form.content.data=''
        #form.author.data=''
        form.slug.data=''
        #Add post data to database
        db.session.add(post)
        db.session.commit()
        flash("You have succesfully made a blog post!")
    #Redirect to webpage
    return render_template("add_post.html",form=form)
# Create Model

# Creates a Form class

# Update database
@app.route('/update/<int:id>',methods=['GET','POST'])
@login_required
def update(id): # Is <int:id> in this case
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name'] # Getting name and email of the previously submitted form
        name_to_update.email = request.form['email']
        name_to_update.favorite_food = request.form['favorite_food']
        name_to_update.username=request.form['username']
        name_to_update.about_author=request.form['about_author']
        #name_to_update.profile_pic=request.files['profile_pic']
        # Check for profile picture
        if request.files['profile_pic']:
            name_to_update.profile_pic=request.files['profile_pic']
            # Saves the image
            #name_to_update.profile_pic.save(os.path.join(app.root_path,'static/images',pic_name))
            # Grab image name securely
            pic_filename=secure_filename(name_to_update.profile_pic.filename)
            # Set UUID, changing name of file
            pic_name=str(uuid.uuid1())+'_'+pic_filename
            saver = request.files['profile_pic']
            #saver.save(os.path.join(app.root_path,'static/images',pic_name))

            name_to_update.profile_pic=pic_name
            try:
                db.session.commit() # Database can submit name_to_update because it accesses Users, the database
                saver.save(os.path.join(app.config['UPLOAD_FOLDER'],pic_name))
                flash("User Updated Successfully")
                return render_template("update.html",form=form,name_to_update=name_to_update)
            except:
                flash("Error!")
        else:
            db.session.commit()
            flash("User Updated Successfully")
            return render_template("dashboard.html",form=form,name_to_update=name_to_update)
    else:
        return render_template("update.html",form=form,name_to_update=name_to_update,id=id)
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
            user= Users(username=form.username.data,name=form.name.data,email=form.email.data,favorite_food=form.favorite_food.data,password_hash=hashed_pw) # sets user to the name and email given
            db.session.add(user) # adds user to the database
            db.session.commit() # commits it
        else:
            flash("This name is already in use!")
        name = form.name.data 
        form.name.data = "" # Resets the name and email back
        form.email.data = ""
        form.username.data=""
        form.favorite_food.data = ""
        form.password_hash.data = ""
        flash("Welcome to my blog!")
    our_users= Users.query.order_by(Users.date_added) # Gets a list of users by date added
    return render_template("add_user.html",form=form,name=name,our_users=our_users)
@app.route('/delete/<int:id>')
@login_required
def delete(id): #Taking id from <int:id>
    if id == current_user.id:
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
    else:
        flash("You can't delete that user!")
        return redirect(url_for('dashboard'))
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
