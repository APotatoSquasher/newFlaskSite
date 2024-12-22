from flask import Flask, render_template
import os
# Creates a Flask Instance
app = Flask(__name__)
# Creates a route decorator
if __name__ == "__main__":
    app.run(debug=False) # this runs
@app.route('/')
def index():
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

#Create invalid URL page
@app.errorhandler(404)
def PageNotFound(error):
    return render_template('404.html'), 404
#@app.errorhandler(500)
#def Bug():
#    return "<h1> It appears you have found a bug in my code! Feel free to email me! (Or this could be me and I'm telling myself I'm an idiot...)<h1/>"