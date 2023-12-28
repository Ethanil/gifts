from flask import abort

from config import db
from models import Item, item_schema, items_schema


def read_all():
    items = Item.query.all()
    return items_schema.dump(items)


def create(item):
    if item is None:
        item = {}
        print("item was none?!?!")
        item["name"] = "TestItem"
        item["description"] = "TestDescription"
        item["rank"] = 4
        item["price"] = 12.4
    name = item.get("name")
    description = item.get("description")
    rank = item.get("rank")
    price = item.get("price")

    existing_item = Item.query.filter(Item.name == name).one_or_none()

    if existing_item is None:
        new_item = item_schema.load(item, session=db.session)
        db.session.add(new_item)
        db.session.commit()
        return item_schema.dump(new_item), 201
    else:

        abort(

            406,

            f"Item with name {name} already exists",

        )