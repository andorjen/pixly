"""SQLAlchemy models for Pixly"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Image(db.Model):
    """User in the system."""

    __tablename__ = 'images'

    id = db.Column(
        db.Text,
        primary_key=True,
    )

    title = db.Column(
        db.Text,
        nullable=False
    )

    image_url = db.Column(
        db.Text,
        nullable=False
    )

    meta_data = db.Column(
        db.Text,
        nullable=False,
        default=""
    )


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)
