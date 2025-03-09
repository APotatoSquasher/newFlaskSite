from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, EqualTo
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField
#Create a Search form
class SearchForm(FlaskForm):
    searched=StringField("Searched ",validators=[DataRequired()])
    submit=SubmitField("Submit")
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
#hello?
class LoginForm(FlaskForm):
    username=StringField("Username: ",validators=[DataRequired()])
    password=PasswordField("Password: ",validators=[DataRequired()])
    submit=SubmitField("Submit")
class PostForm(FlaskForm):
    title=StringField("Title: ",validators=[DataRequired()])
    #content=StringField("Content: ",validators=[DataRequired()],widget=TextArea())
    #Adds CKEditor to the form
    content=CKEditorField('Content', validators=[DataRequired()])
    #author=StringField("Author: ",validators=[DataRequired()])
    slug=StringField("Alternate URL: ",validators=[DataRequired()])
    submit=SubmitField("Submit")
class UserForm(FlaskForm):
    name=StringField("Name: ",validators=[DataRequired()])
    username=StringField("Username:",validators=[DataRequired()])
    email=StringField("Email: ",validators=[DataRequired()])
    password_hash = PasswordField("Password: ",validators=[DataRequired(),EqualTo('password_hash2',message='Password Must Match!')])
    password_hash2 = PasswordField("Confirm Password: ",validators=[DataRequired()]) # This doesn't need a EqualTo() because the first one must match with this one
    favorite_food = StringField("Favorite Food: ")
    profile_pic = FileField("Profile Pic")  
    about_author = TextAreaField("About Author: ")
    submit=SubmitField("Submit")