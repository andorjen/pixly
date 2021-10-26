import os
# from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask, render_template, redirect, request
from models import db, connect_db, Image
# from forms import FormName
import dotenv 
dotenv.load_dotenv()
import boto3
import uuid
# uses credentials from environment
s3 = boto3.resource('s3')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///pixly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)

# debug = DebugToolbarExtension(app)
# app.config['SECRET_KEY'] = "thisismysecret"
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


# comes from .env file, add to .gitignore
MY_SECRET = os.environ['MY_SECRET']
API_KEY = os.environ['API_SECRET_KEY']

# db.create_all()

AWS_BUCKET_URL = "https://pix.ly-eaa.s3.us-west-2.amazonaws.com/"

@app.get("/")
def show_homepage():
    """renders homepage templates"""

    return render_template("home.html")

@app.get("/upload")
def show_upload_page():
    """renders upload template"""

    return render_template("upload.html")

@app.post("/upload")
def add_image():
    """upload template"""
    user_title = request.form.title
    image_title = ("").join(user_title.split())
    image_id = uuid.uuid4()

    s3.Bucket('pix.ly-eaa').put_object(Key=f"{image_title}-{image_id}", Body=request.files['image'])

    image=Image(
        id=image_id,
        title=user_title,
        img_url= f"{AWS_BUCKET_URL}{image_title}-{image_id}",
        metadata= "?"
    )

    db.session.add(image)
    db.session.commit()

    return redirect(f"/images/{id}")