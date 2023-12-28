from config import db
from config import db, ma

from datetime import datetime

from marshmallow import Schema, fields

class Item(db.Model):

    __tablename__ = "item"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    description = db.Column(db.String(255))
    rank = db.Column(db.Integer)
    price = db.Column(db.Float)
    timestamp = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class ItemSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Item
        load_instance = True
        sqla_session = db.session

item_schema = ItemSchema()
items_schema = ItemSchema(many=True)
