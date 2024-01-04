from flask import make_response,abort
from models import Gift, gift_schema, gifts_schema, giftGroup_schema, GiftGroup
from config import db


def create(giftgroup_id, gift, user, token_info):
    existing_giftGroup = GiftGroup.query.filter(GiftGroup.id == giftgroup_id).one_or_none()
    if existing_giftGroup is None:
        abort(
            404,
            f"Giftgroup with id {giftgroup_id} does not exist"
        )
    gift.pop("picture", None)
    new_gift = Gift(**gift, user_email=user)
    existing_giftGroup.gift.add(new_gift)
    db.session.commit()
    return gift_schema.dump(new_gift), 201


def read_all(giftgroup_id, user, token_info):
    existing_giftGroup = GiftGroup.query.filter(GiftGroup.id == giftgroup_id).one_or_none()
    if existing_giftGroup is None:
        abort(
            404,
            f"Giftgroup with id {giftgroup_id} does not exist"
        )
    gift_set = existing_giftGroup.gift
    isBeingGifted_set = existing_giftGroup.isBeingGifted
    user_set = [isBeingGifted.user_email for isBeingGifted in isBeingGifted_set]
    if user in user_set:
        result_gifts = [gift for gift in gift_set if gift.user_email in user_set]
        return gifts_schema.dump(result_gifts)
    return gifts_schema.dump(gift_set), 200


def update(gift_id, giftgroup_id, gift, user, token_info):
    existing_giftGroup = GiftGroup.query.filter(GiftGroup.id == giftgroup_id).one_or_none()
    if existing_giftGroup is None:
        abort(
            404,
            f"Giftgroup with id {giftgroup_id} does not exist"
        )
    existing_gift_set = existing_giftGroup.gift
    existing_gift = None
    for _gift in existing_gift_set:
        if _gift.id == gift_id and _gift.user_email == user:
            existing_gift = _gift
            break
    if existing_gift is None:
        abort(
           401,
           f"Gift with id {gift_id} can't be updated"
        )
    existing_gift.name = gift.get("name")
    existing_gift.description = gift.get("description")
    existing_gift.price = gift.get("price")
    existing_gift.link = gift.get("link")
    existing_gift.giftStrength = gift.get("giftStrength")
    db.session.merge(existing_gift)
    db.session.commit()
    return gift_schema.dump(existing_gift), 200


def delete(gift_id, giftgroup_id, user, token_info):
    existing_giftGroup = GiftGroup.query.filter(GiftGroup.id == giftgroup_id).one_or_none()
    if existing_giftGroup is None:
        abort(
            404,
            f"Giftgroup with id {giftgroup_id} does not exist"
        )
    existing_gift_set = existing_giftGroup.gift
    existing_gift = None
    for _gift in existing_gift_set:
        if _gift.id == gift_id and _gift.user_email == user:
            existing_gift = _gift
            break
    if existing_gift is None:
        abort(
           401,
           f"Gift with id {gift_id} can't be deleted"
        )
    db.session.delete(existing_gift)
    db.session.commit()
    return make_response(f"Gift with id {gift_id} succesfully deleted from Giftgroup {existing_giftGroup.name}", 204)
