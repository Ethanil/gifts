import os.path

from flask import make_response, abort
from models import Gift, gift_schema, gifts_schema, GiftGroup, IsBeingGifted, HasReserved, \
    HasRequestedReservationFreeing, hasReserved_schema
from config import db
from werkzeug.datastructures import FileStorage
import base64
from uuid import uuid4
from typing import List
from enum import Enum


class Actions(str, Enum):
    EDIT = "edit"
    DELETE = "delete"
    RESERVE = "reserve"
    STOP_RESERVE = "stop reserve"
    FREE_RESERVE = "free reserve"
    STOP_FREE_RESERVE = "stop free reserve"
    REQUEST_FREE_RESERVE = "request free reserve"
    STOP_REQUEST_FREE_RESERVE = "stop request free reserve"


def create(giftgroup_id, gift, user, token_info, picture=""):
    gift.pop('id', None)
    if isinstance(picture, FileStorage):
        # filename = werkzeug.utils.secure_filename(picture.filename)
        filename = f"{uuid4()}.{picture.content_type.split('/')[1]}"

        # Specify the path to your pictures folder
        folder_path = "pictures"

        # Create the folder if it doesn't exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Save the image to a file
        image_filename = os.path.join(folder_path, filename)
        picture.save(image_filename)
        gift['picture'] = image_filename
    existing_giftGroup = GiftGroup.query.filter(GiftGroup.id == giftgroup_id).one_or_none()
    if existing_giftGroup is None:
        abort(
            404,
            f"Giftgroup with id {giftgroup_id} does not exist"
        )
    new_gift = Gift(**gift, user_email=user)
    existing_giftGroup.gift.add(new_gift)
    db.session.commit()
    return gift_schema.dump(new_gift), 201


def read(giftgroup_id, user, token_info):
    existing_giftGroup = GiftGroup.query.filter(GiftGroup.id == giftgroup_id).one_or_none()
    if existing_giftGroup is None:
        abort(
            404,
            f"Giftgroup with id {giftgroup_id} does not exist"
        )
    return filter_dump_and_add_fields_to_gifts(existing_giftGroup.gift, user), 200


def read_all(user, token_info):
    gifts = filter_gifts(Gift.query.all(), user)
    dumpedGifts = gifts_schema.dump(gifts)
    res = {}
    for index, entry in enumerate(dumpedGifts):
        gift = gifts[index]
        entry = add_fields_to_gift(entry, gifts[index], user)
        # Sort the answer in an array for each giftGroup for easy access
        if res.get(gift.giftGroup_id) is None:
            res[gift.giftGroup_id] = [entry]
        else:
            res[gift.giftGroup_id].append(entry)
        entry["isAllowedToEdit"] = False
    return res, 200


def filter_dump_and_add_fields_to_gifts(gifts: List[Gift], user: str) -> List[dict]:
    return [add_fields_to_gift(gift_schema.dump(gift), gift, user) for gift in gifts if
            user == gift.user_email or
            IsBeingGifted.query.filter(IsBeingGifted.user_email == gift.user_email,
                                       IsBeingGifted.giftGroup_id == gift.giftGroup_id).one_or_none() is not None]


def add_fields_to_gift(gift_dict: dict, gift: Gift, user: str) -> dict:
    gift_dict = add_actions_to_gift(gift_dict, gift, user)
    gift_dict = add_image_to_gift(gift_dict)
    return gift_dict


def add_actions_to_gift(gift_dict: dict, gift: Gift, user: str) -> dict:
    actions = getActions(gift, user)
    gift_dict["availableActions"] = actions
    return gift_dict


def getActions(gift: Gift, user: str) -> List[Actions]:
    actions: List[Actions] = []
    users_that_are_being_gifted = [isBeingGifted.user_email for isBeingGifted in
                                   IsBeingGifted.query.filter(IsBeingGifted.giftGroup_id == gift.giftGroup_id).all()]
    # User that are beeing gifted should be able to edit gifts of their being-gifted-partners
    if user in users_that_are_being_gifted or user == gift.user_email:
        actions.append(Actions.EDIT)
        actions.append(Actions.DELETE)
        pass
    if user not in users_that_are_being_gifted:
        users_that_have_gift_reserved = [hasReserved.user_email for hasReserved in
                                         HasReserved.query.filter(HasReserved.gift_id == gift.id).all()]
        users_that_have_requested_reservation_freeing = [hasRequestedReservationFreeing.user_email for
                                                         hasRequestedReservationFreeing in
                                                         HasRequestedReservationFreeing.query.filter(
                                                             HasRequestedReservationFreeing.gift_id == gift.id).all()]
        if user not in users_that_have_gift_reserved:
            if len(users_that_have_gift_reserved) == 0 or gift.freeForReservation:
                actions.append(Actions.RESERVE)
            elif not gift.freeForReservation:
                if user not in users_that_have_requested_reservation_freeing:
                    actions.append(Actions.REQUEST_FREE_RESERVE)
                else:
                    actions.append(Actions.STOP_REQUEST_FREE_RESERVE)
        else:
            actions.append(Actions.STOP_RESERVE)
            if gift.freeForReservation:
                actions.append(Actions.STOP_FREE_RESERVE)
            else:
                actions.append(Actions.FREE_RESERVE)
    return actions


# get picture from storage and send it parsed as base64, cause i am to dumb to do this as a blob :(
def add_image_to_gift(gift: dict) -> dict:
    picture = gift.get('picture')
    if picture is not None and picture != "":
        with open(picture, "rb") as img_file:
            image_data = img_file.read()
        base64_image = base64.b64encode(image_data).decode("utf-8")
        image_format = picture.split('.')[1]
        base64_string = f"data:image/{image_format};base64,{base64_image}"
        gift['picture'] = base64_string
    return gift


def filter_gifts(gifts: List[Gift], user: str) -> List[Gift]:
    result: List[Gift] = []
    for gift in gifts:
        isBeingGiftedList = IsBeingGifted.query.filter(IsBeingGifted.giftGroup_id == gift.giftGroup_id).all()
        user_is_part_of_giftgroup = any([user == isBeingGifted.user_email for isBeingGifted in isBeingGiftedList])
        gift_is_created_by_user_of_giftgroup = any(
            [gift.user_email == isBeingGifted.user_email for isBeingGifted in isBeingGiftedList])
        if not (user_is_part_of_giftgroup and not gift_is_created_by_user_of_giftgroup):
            result.append(gift)
    return result


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


def patch(gift_id, giftgroup_id, user, token_info, reserve=None, free_reserve=None, request_free_reserve=None):
    # if len([i for i in [reserve, free_reserve, request_free_reserve] if i is not None]) > 1:
    #     abort(
    #         400,
    #         "Malformed request, too many query parameters set at once"
    #     )
    existing_giftGroup = GiftGroup.query.filter(GiftGroup.id == giftgroup_id).one_or_none()
    if existing_giftGroup is None:
        abort(
            403,
            f"Giftgroup with id {giftgroup_id} does not exist"
        )
    existing_gift = Gift.query.filter(Gift.id == gift_id).one_or_none()
    if existing_gift is None:
        abort(
            403,
            f"Gift with id {gift_id} does not exist"
        )
    availableActions = getActions(existing_gift, user)
    if reserve is not None:
        if reserve:
            if Actions.RESERVE not in availableActions:
                abort(
                    403,
                    "Not Allowed to reserve"
                )
            reservation = HasReserved(gift_id=gift_id, user_email=user)
            db.session.add(reservation)
        else:
            if Actions.STOP_RESERVE not in availableActions:
                abort(
                    403,
                    "Not Allowed to cancel reservation"
                )
            reservation = HasReserved.query.filter(HasReserved.gift_id == gift_id,
                                                   HasReserved.user_email == user).one_or_none()
            db.session.delete(reservation)
    if free_reserve is not None:
        if free_reserve:
            if Actions.FREE_RESERVE not in availableActions:
                abort(
                    403,
                    "Not Allowed to free reservation"
                )
            existing_gift.freeForReservation = True
            db.session.merge(existing_gift)

        else:
            if Actions.STOP_FREE_RESERVE not in availableActions:
                abort(
                    403,
                    "Not Allowed to stop free reservation"
                )
            existing_gift.freeForReservation = False
            db.session.merge(existing_gift)

    if request_free_reserve is not None:
        if request_free_reserve:
            if Actions.REQUEST_FREE_RESERVE not in availableActions:
                abort(
                    403,
                    "Not Allowed to request free reservation"
                )
            reservation_request = HasRequestedReservationFreeing(gift_id=gift_id, user_email=user)
            db.session.add(reservation_request)
        else:
            if Actions.STOP_REQUEST_FREE_RESERVE not in availableActions:
                abort(
                    403,
                    "Not Allowed to stop requesting free reservation"
                )
            reservation = HasRequestedReservationFreeing.query.filter(HasReserved.gift_id == gift_id,
                                                                      HasReserved.user_email == user).one_or_none()
            db.session.delete(reservation)
    db.session.commit()
    return 200
