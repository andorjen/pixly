"""SQLAlchemy models for Pixly"""
from flask_sqlalchemy import SQLAlchemy
from ts_vector import TSVector
from sqlalchemy import Index

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

    __ts_vector__ = db.Column(
        TSVector(),
        db.Computed(
        "to_tsvector('english', title || ' ' || meta_data)",
        persisted=True))

    __table_args__ = (Index(
        'ix_image___ts_vector__',
        __ts_vector__, postgresql_using='gin'),)


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)
