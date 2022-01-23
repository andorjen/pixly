import os
import dotenv
import shutil

import uuid
import boto3

from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask, render_template, redirect, request
from models import db, connect_db, Image
import urllib.request


from PIL import Image as PILImage
from PIL import ImageEnhance, ImageOps
from PIL.ExifTags import TAGS

dotenv.load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ['DATABASE_URL'].replace("postgres://", "postgresql://"))

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
    """upload image to s3, and redirect to edit page on successful upload, 
    otherwise redirect to show all images"""

    user_title = request.form['title']
    file = request.files['image']
    file_types = ["image/jpg", "image/png", "image/jpeg"]
    file_ext = file.mimetype.replace("image/", "")
    if file and (file.mimetype in file_types):

        image_title = ("").join(user_title.split())
        image_id = uuid.uuid4()
        image_data = get_image_data(file)

        file.seek(0)

        original_file = PILImage.open(file)
        original_file.thumbnail((400, 400))
        original_file.save(f"./temp/resized_file.{file_ext}")

        s3.upload_file(
            f"./temp/resized_file.{file_ext}", "pixly-alien-j", f"{image_title}-{image_id}",
            ExtraArgs={"ACL": "public-read"})

        # s3.upload_file(
        #     f"./temp/resized_file.{file_ext}", "pix.ly-eaa", f"{image_title}-{image_id}",
        #     ExtraArgs={"ACL": "public-read"})

        image = Image(
            id=image_id,
            title=user_title,
            image_url=f"{AWS_OBJECT_URL}{image_title}-{image_id}",
            meta_data=str(image_data)
        )

        db.session.add(image)
        db.session.commit()
        return redirect(f"/images/{image_id}")

    return redirect("/images")


@app.get("/images")
def show_all_images():
    """renders images template"""

    if "search" in request.args.keys():

        search_term = request.args["search"]
        alnum_search_term = ''.join(e for e in search_term if e.isalnum())

        images = Image.query.filter(
            Image.__ts_vector__.match(alnum_search_term)).all()
    else:
        images = Image.query.all()

    return render_template("images.html", images=images)


@app.get("/images/<id>")
def show_image(id):
    """renders page to edit an image"""

    image_data = Image.query.get_or_404(id)
    form_data = request.args.to_dict()

    newpath = f"./temp/{id}"

    debug
    if not os.path.exists(newpath):

        shutil.rmtree("./temp")
        os.makedirs("./temp")
        os.makedirs(newpath)
        urllib.request.urlretrieve(
            image_data.image_url, f"./temp/{id}/original.jpeg")
        urllib.request.urlretrieve(
            image_data.image_url, f"./temp/{id}/edited.jpeg")

    if "filter" in form_data:
        image = PILImage.open(f"./temp/{id}/edited.jpeg")

        image_rot_90 = image.convert('L')
        image_rot_90.save(f"./temp/{id}/edited.jpeg")

    if "rotate" in form_data:
        image = PILImage.open(f"./temp/{id}/edited.jpeg")

        image_rot_90 = image.rotate(90, expand=True)
        image_rot_90.save(f"./temp/{id}/edited.jpeg")

    if "mirror" in form_data:
        image = PILImage.open(f"./temp/{id}/edited.jpeg")
        flipped_image = image.transpose(PILImage.FLIP_LEFT_RIGHT)
        flipped_image.save(f"./temp/{id}/edited.jpeg")

    if "contrast" in form_data:
        image = PILImage.open(f"./temp/{id}/edited.jpeg")
        contrast = ImageEnhance.Contrast(image)
        contrast.enhance(1.5).save(f"./temp/{id}/edited.jpeg")

    if "border" in form_data:
        image = PILImage.open(f"./temp/{id}/edited.jpeg")
        border_image = ImageOps.expand(
            image, border=(10, 10, 10, 10), fill="black")
        border_image.save(f"./temp/{id}/edited.jpeg")

    if "revert" in form_data:
        urllib.request.urlretrieve(
            image_data.image_url, f"./temp/{id}/edited.jpeg")

    return render_template("image.html", image=image_data)


# @app.get("/images/<id>/<action>")
# def edit_image(id, action):
#     """sends post request to edit an image"""
#     image_data = Image.query.get_or_404(id)
#     # form_data = request.form.to_dict()

#     if action == "filter":
#         image = PILImage.open(f"./temp/{id}/edited.jpeg")

#         image_rot_90 = image.convert('L')
#         image_rot_90.save(f"./temp/{id}/edited.jpeg")

#     if action == "rotate":
#         image = PILImage.open(f"./temp/{id}/edited.jpeg")

#         image_rot_90 = image.rotate(90, expand=True)
#         image_rot_90.save(f"./temp/{id}/edited.jpeg")

#     if action == "mirror":
#         image = PILImage.open(f"./temp/{id}/edited.jpeg")
#         flipped_image = image.transpose(PILImage.FLIP_LEFT_RIGHT)
#         flipped_image.save(f"./temp/{id}/edited.jpeg")

#     if action == "contrast":
#         image = PILImage.open(f"./temp/{id}/edited.jpeg")
#         contrast = ImageEnhance.Contrast(image)
#         contrast.enhance(1.5).save(f"./temp/{id}/edited.jpeg")

#     if action == "border":
#         image = PILImage.open(f"./temp/{id}/edited.jpeg")
#         border_image = ImageOps.expand(
#             image, border=(10, 10, 10, 10), fill="black")
#         border_image.save(f"./temp/{id}/edited.jpeg")

#     if action == "revert":
#         urllib.request.urlretrieve(
#             image_data.image_url, f"./temp/{id}/edited.jpeg")

#     # return redirect(f"/images/{id}")
#     return render_template("image.html", image=image_data)


############################# HELPER FUNCTIONS #######################################################################


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
        result[tag] = data

    return result

############################# FURTHER STUDIES #######################################################################
# frontend js, ajax request
# add revert back one step feature
# allow more customizable edits with simple image
# add tags for images for full text search
# pillow image open context manager : with
