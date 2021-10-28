import os
import dotenv

import uuid
import boto3

from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask, render_template, redirect, request
from models import db, connect_db, Image
import urllib.request
# from forms import FormName
# from werkzeug.utils import secure_filename

from PIL import Image as PILImage
from PIL import ImageEnhance
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

s3 = boto3.client('s3')

AWS_OBJECT_URL = "https://s3.us-west-2.amazonaws.com/pix.ly-eaa/"

# AWS_OBJECT_URL = "https://pixly-alien-j.s3.us-west-1.amazonaws.com/"

# importing modules


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
    if file:
        image_title = ("").join(user_title.split())
        image_id = uuid.uuid4()
        image_data = get_image_data(file)

        file.seek(0)
        # breakpoint()
        original_file = PILImage.open(file)
        original_file.thumbnail((400, 400))
        original_file.save('./static/resized_file.jpeg')

        # s3.upload_file(
        #     "./static/resized_file.jpeg", "pixly-alien-j", f"{image_title}-{image_id}",
        #     ExtraArgs={"ACL": "public-read"})

        s3.upload_file(
            "./static/resized_file.jpeg", "pix.ly-eaa", f"{image_title}-{image_id}",
            ExtraArgs={"ACL": "public-read"})

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
    # breakpoint()
    if "search" in request.args.keys():
        search_term = request.args["search"]
        # do search
        images = Image.query.filter(Image.__ts_vector__.match(search_term)).all()
    else:
        images = Image.query.all()

    return render_template("images.html", images=images)


@app.get("/images/<id>")
def show_image(id):
    """renders images template"""

    image_data = Image.query.get_or_404(id)
    urllib.request.urlretrieve(image_data.image_url, "./static/original.jpeg")
    urllib.request.urlretrieve(image_data.image_url, "./static/edited.jpeg")

    return render_template("image.html", image=image_data)


@app.post("/images/<id>")
def edit_image(id):
    """sends post request to edit an image"""
    image_data = Image.query.get_or_404(id)
    form_data = request.form.to_dict()
    # breakpoint()
    # if request.form["filter"]:
    if "filter" in form_data.keys():
        image = PILImage.open("./static/edited.jpeg")

        image_rot_90 = image.convert('L')
        image_rot_90.save("./static/edited.jpeg")

    if "rotate" in form_data.keys():
        image = PILImage.open("./static/edited.jpeg")

        image_rot_90 = image.rotate(90)
        image_rot_90.save("./static/edited.jpeg")

    if "mirror" in form_data.keys():
        image = PILImage.open("./static/edited.jpeg")
        flipped_image = image.transpose(PILImage.FLIP_LEFT_RIGHT)
        flipped_image.save("./static/edited.jpeg")
    
    if "contrast" in form_data.keys():
        image = PILImage.open("./static/edited.jpeg")
        contrast = ImageEnhance.Contrast(image)
        contrast.enhance(1.5).save("./static/edited.jpeg")

    if "revert" in form_data.keys():
        urllib.request.urlretrieve(
            image_data.image_url, "./static/edited.jpeg")
    return render_template("image.html", image=image_data)


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
