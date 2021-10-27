import os
import dotenv

import uuid
import boto3

from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask, render_template, redirect, request
from models import db, connect_db, Image
# from forms import FormName

from PIL import Image as PILImage
from PIL.ExifTags import TAGS

# uses credentials from environment
dotenv.load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///pixly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

# comes from .env file, add to .gitignore
MY_SECRET = os.environ['MY_SECRET']
API_KEY = os.environ['API_SECRET_KEY']


app.config['SECRET_KEY'] = MY_SECRET
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

connect_db(app)
db.create_all()


s3 = boto3.resource('s3')
# AWS_BUCKET_URL = "https://pix.ly-eaa.s3.us-west-2.amazonaws.com/"

AWS_BUCKET_URL = "https://pixly-alien-j.s3.us-west-1.amazonaws.com/"


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

    user_title = request.form['title']
    image_title = ("").join(user_title.split())
    image_id = uuid.uuid4()

    image_data = get_image_data(request.files['image'])
    # print(image_data)

    # s3.Bucket(
    #     'pix.ly-eaa').put_object(Key=f"{image_title}-{image_id}", Body=request.files['image'])
    s3.Bucket(
        'pixly-alien-j').put_object(Key=f"{image_title}-{image_id}", Body=request.files['image'])

    image = Image(
        id=image_id,
        title=user_title,
        image_url=f"{AWS_BUCKET_URL}{image_title}-{image_id}",
        meta_data=str(image_data)
    )

    db.session.add(image)
    db.session.commit()

    return redirect("/")


def get_image_data(path):
    """read metadata from a given image"""
    # breakpoint()
    image = PILImage.open(path)
    exifdata = image.getexif()
    result = {}
    # breakpoint()
    for tag_id in exifdata:
        # print("in the tag_id decode")
        # get the tag name, instead of human unreadable tag id
        tag = TAGS.get(tag_id, tag_id)
        data = exifdata.get(tag_id)
        # decode bytes
        if isinstance(data, bytes):
            data = data.decode()
        # print(f"{tag:25}: {data}")
        result[tag] = data

    return result
