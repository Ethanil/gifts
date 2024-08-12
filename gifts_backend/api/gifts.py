import os.path
from os import getenv

from flask import make_response, abort
from models import Gift, gift_schema, gifts_schema, GiftGroup, IsBeingGifted, HasReserved, \
    HasRequestedReservationFreeing, User
from config import db
from werkzeug.datastructures import FileStorage
import base64
from uuid import uuid4
from typing import List
from enum import Enum
from api.giftgroups import updateLastUpdated

class Actions(str, Enum):
    EDIT = "edit"
    DELETE = "delete"
    RESERVE = "reserve"
    STOP_RESERVE = "stop reserve"
    FREE_RESERVE = "free reserve"
    STOP_FREE_RESERVE = "stop free reserve"
    DENY_FREE_RESERVE = "deny free reserve"
    REQUEST_FREE_RESERVE = "request free reserve"
    STOP_REQUEST_FREE_RESERVE = "stop request free reserve"


def create(giftgroup_id, gift, user, token_info, picture=""):
    gift.pop('id', None)
    if isinstance(picture, FileStorage):
        filename = f"{uuid4()}.{picture.content_type.split('/')[1]}"

        folder_path = getenv("PICTURE_STORAGE")
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
    updateLastUpdated(user, existing_giftGroup)
    db.session.commit()
    return gift_schema.dump(new_gift), 201


def read(giftgroup_id, user, token_info):
    current_user = User.query.filter(User.email == user).one_or_none()
    if current_user is None:
        abort(400, "This user does not exist!")
    if current_user.onlyViewing:
        if giftgroup_id not in [isSpecialUser.giftGroup_id for isSpecialUser in current_user.isSpecialUser]:
            abort(403, "No acces to that group!")
    existing_giftGroup = GiftGroup.query.filter(GiftGroup.id == giftgroup_id).one_or_none()
    if existing_giftGroup is None:
        abort(
            404,
            f"Giftgroup with id {giftgroup_id} does not exist"
        )
    return filter_dump_and_add_fields_to_gifts(existing_giftGroup.gift, user), 200


def read_all(user, token_info):
    current_user = User.query.filter(User.email == user).one_or_none()
    if current_user is None:
        abort(400, "This user does not exist!")
    all_gifts = Gift.query.all()
    if current_user.onlyViewing:
        viewAbleGiftGroups = [giftGroup.id for giftGroup in
                              [isSpecialUser.giftGroup for isSpecialUser in current_user.isSpecialUser]]
        all_gifts = [gift for gift in all_gifts if gift.giftGroup_id in viewAbleGiftGroups]
    gifts = filter_gifts(all_gifts, user)
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
    gift_dict = add_calls_to_action_to_gift(gift_dict, gift, user)
    gift_dict = add_is_secret_gift(gift_dict, gift, user)
    gift_dict = add_image_to_gift(gift_dict)
    gift_dict = add_reserving_users_to_gift(gift_dict, gift, user)
    return gift_dict


def add_reserving_users_to_gift(gift_dict: dict, gift: Gift, user: str) -> dict:
    if user not in [user.user_email for user in gift.giftGroup.isBeingGifted]:
        gift_dict["reservingUsers"] = [hasReserverd.user.email for hasReserverd in gift.hasReserved]
    return gift_dict


def add_is_secret_gift(gift_dict: dict, gift: Gift, user: str) -> dict:
    gift_dict["isSecretGift"] = gift.user_email not in [usr.user_email for usr in gift.giftGroup.isBeingGifted]
    return gift_dict


def add_calls_to_action_to_gift(gift_dict: dict, gift: Gift, user: str) -> dict:
    if Actions.FREE_RESERVE in gift_dict['availableActions']:
        gift_dict['freeForReservationRequest'] = [reservationRequest.user.email for reservationRequest in
                                                  gift.hasRequestedReservationFreeing]
    return gift_dict


def add_actions_to_gift(gift_dict: dict, gift: Gift, user: str) -> dict:
    actions = getActions(gift, user)
    gift_dict["availableActions"] = actions
    return gift_dict


def getActions(gift: Gift, user: str) -> List[Actions]:
    actions: List[Actions] = []
    users_that_are_being_gifted = [isBeingGifted.user_email for isBeingGifted in
                                   gift.giftGroup.isBeingGifted]
    # User that are beeing gifted should be able to edit gifts of their being-gifted-partners
    if user in users_that_are_being_gifted:
        actions.append(Actions.EDIT)
        actions.append(Actions.DELETE)
    else:
        if user == gift.user_email:
            actions.append(Actions.EDIT)
            actions.append(Actions.DELETE)
        users_that_have_gift_reserved = [hasReserved.user_email for hasReserved in
                                         gift.hasReserved]
        users_that_have_requested_reservation_freeing = [hasRequestedReservationFreeing.user_email for
                                                         hasRequestedReservationFreeing in
                                                         gift.hasRequestedReservationFreeing]
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
    if picture is not None and picture != "" and os.path.isfile(picture):
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
        isBeingGiftedList = gift.giftGroup.isBeingGifted
        user_is_part_of_giftgroup = any([user == isBeingGifted.user_email for isBeingGifted in isBeingGiftedList])
        gift_is_created_by_user_of_giftgroup = any(
            [gift.user_email == isBeingGifted.user_email for isBeingGifted in isBeingGiftedList])
        if not (user_is_part_of_giftgroup and not gift_is_created_by_user_of_giftgroup):
            result.append(gift)
    return result


def update(gift_id, giftgroup_id, gift, user, token_info, picture=""):
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
    if Actions.EDIT not in availableActions:
        abort(
            404,
            f"Not allowed to edit gift with id {gift_id}"
        )
    if isinstance(picture, FileStorage):
        if existing_gift.picture is None or existing_gift.picture == "" or not os.path.isfile(existing_gift.picture):
            filename = f"{uuid4()}.{picture.content_type.split('/')[1]}"
            folder_path = getenv("PICTURE_STORAGE")

            # Create the folder if it doesn't exist
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            # Save the image to a file
            image_filename = os.path.join(folder_path, filename)
        else:
            image_filename = existing_gift.picture
        picture.save(image_filename)
        gift['picture'] = image_filename
        existing_gift.picture = gift.get("picture")
    else:
        if existing_gift.picture is not None and existing_gift.picture != "" and os.path.isfile(existing_gift.picture):
            os.remove(existing_gift.picture)
        existing_gift.picture = gift.get("picture")
    existing_gift.name = gift.get("name")
    existing_gift.description = gift.get("description")
    existing_gift.price = gift.get("price")
    existing_gift.link = gift.get("link")
    existing_gift.giftStrength = gift.get("giftStrength")
    updateLastUpdated(user, existing_giftGroup)
    db.session.merge(existing_gift)
    db.session.commit()
    return gift_schema.dump(existing_gift), 200


def delete(gift_id, giftgroup_id, user, token_info):
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
    if Actions.DELETE not in availableActions:
        abort(
            404,
            f"Not allowed to delete gift with id {gift_id}"
        )
    updateLastUpdated(user, existing_giftGroup)
    db.session.delete(existing_gift)
    db.session.commit()
    return make_response(f"Gift with id {gift_id} succesfully deleted from Giftgroup {existing_giftGroup.name}", 204)


def patch(gift_id, giftgroup_id, user, token_info, reserve=None, free_reserve=None, request_free_reserve=None,
          deny_free_reserve=None):
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
    if deny_free_reserve is not None and deny_free_reserve:
        if Actions.FREE_RESERVE not in availableActions:
            abort(
                403,
                "Not Allowed to denyfree reservation"
            )
        for hasRequestedReservationFreeing in existing_gift.hasRequestedReservationFreeing:
            db.session.delete(hasRequestedReservationFreeing)
    elif free_reserve is not None:
        if free_reserve:
            if Actions.FREE_RESERVE not in availableActions:
                abort(
                    403,
                    "Not Allowed to free reservation"
                )
            existing_gift.freeForReservation = True
            for hasRequestedReservationFreeing in existing_gift.hasRequestedReservationFreeing:
                existing_gift.hasReserved.add(HasReserved(user_email=hasRequestedReservationFreeing.user_email))
                db.session.delete(hasRequestedReservationFreeing)
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
            reservation = HasRequestedReservationFreeing.query.filter(HasRequestedReservationFreeing.gift_id == gift_id,
                                                                      HasRequestedReservationFreeing.user_email == user).one_or_none()
            db.session.delete(reservation)
    updateLastUpdated(user, existing_giftGroup)
    db.session.commit()
    return 200
