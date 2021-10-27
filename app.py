import os
import dotenv

import uuid
import boto3

from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask, render_template, redirect, request
from models import db, connect_db, Image
# from forms import FormName
# from werkzeug.utils import secure_filename

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
# AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']

app.config['SECRET_KEY'] = MY_SECRET
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

connect_db(app)
db.create_all()


# s3 = boto3.resource('s3')
s3 = boto3.client('s3')

# AWS_OBJECT_URL = "https://s3.us-west-2.amazonaws.com/pix.ly-eaa/"

AWS_OBJECT_URL = "https://pixly-alien-j.s3.us-west-1.amazonaws.com/"


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
    file = request.files['image']

    # data = file.read()

    # breakpoint()
    image_title = ("").join(user_title.split())
    image_id = uuid.uuid4()
    image_data = get_image_data(file)

    print(image_data)

    # s3.meta.client.upload_fileobj(
    #     file, "pix.ly-eaa", f"{image_title}-{image_id}", ExtraArgs={"ContentType": "image/jpeg"})
    # breakpoint()
    file.seek(0)
    result = s3.upload_fileobj(
        file, "pixly-alien-j", f"{image_title}-{image_id}",
        ExtraArgs={"ACL": "public-read"})

    #  secure_filename(file.filename)
    # result = s3.upload_file(
    #     secure_filename(
    #         file.filename), "pixly-alien-j", f"{image_title}-{image_id}",
    #     ExtraArgs={"ContentType": file.content_type, "ACL": "public-read"})

    print("after upload", result)

    # ExtraArgs={"Metadata": {"ContentType": "image/jpeg"}}
    # s3.meta.client.upload_fileobj(
    #     file, "pixly-alien-j", f"{image_title}-{image_id}", ExtraArgs={"ContentType": "image/jpeg"})
    # s3.Bucket(
    #     'pix.ly-eaa').put_object(Key=f"{image_title}-{image_id}", Body=file, ContentType="image/jpeg")
    # s3.Bucket(
    #     # 'pixly-alien-j').put_object(Key=f"{image_title}-{image_id}", Body=file)

    image = Image(
        id=image_id,
        title=user_title,
        image_url=f"{AWS_OBJECT_URL}{image_title}-{image_id}",
        meta_data=str(image_data)
    )

    db.session.add(image)
    db.session.commit()

    return redirect("/")


@app.get("/images")
def show_all_images():
    """renders images template"""
    images = Image.query.all()

    return render_template("images.html", images=images)


def get_image_data(path):
    """read metadata from a given image"""

    image = PILImage.open(path)
    exifdata = image.getexif()
    result = {}

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
# pillow image open context manager : with
