# from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask, render_template
# from models import db, connect_db
# from forms import FormName
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///pixly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

# connect_db(app)

# debug = DebugToolbarExtension(app)
# app.config['SECRET_KEY'] = "thisismysecret"
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


# comes from .env file, add to .gitignore
MY_SECRET = os.environ['MY_SECRET']
API_KEY = os.environ['API_SECRET_KEY']

# db.create_all()


@app.get("/")
def show_homepage():
    """renders homepage templates"""

    return render_template("home.html")
