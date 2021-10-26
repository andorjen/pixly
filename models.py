"""SQLAlchemy models for Pixly"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Image(db.Model):
    """User in the system."""

    __tablename__ = 'images'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.Text,
        nullable=False
    )

    image_url = db.Column(
        db.Text,
        nullable=False
    )

    meta_data = db.Column(
        db.Text,
        nullable=False
    )
