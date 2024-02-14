from flask import make_response, abort
from models import GiftGroup, giftGroup_schema, giftGroups_schema, User, IsBeingGifted, isBeingGifted_schema
from config import db


def read_all(user, token_info):
    giftGroups = GiftGroup.query.all()
    # decorate giftGroups with Ownership-value
    decorated_gift_groups = [(giftGroup,
                              [len(giftGroup.isBeingGifted) if beingGifted.user_email == user else float('inf') for
                               beingGifted in giftGroup.isBeingGifted]) for giftGroup in giftGroups]
    # sort on Ownershipvalue, then groupname
    decorated_gift_groups = sorted(sorted(decorated_gift_groups, key=lambda tuple: tuple[0].name),
                                   key=lambda tuple: tuple[1])
    giftGroups = [giftGroup for giftGroup, _ in decorated_gift_groups]
    res = giftGroups_schema.dump(giftGroups)
    for entry in res:
        existing_relation = IsBeingGifted.query.filter(IsBeingGifted.giftGroup_id == entry.get("id"),
                                                       IsBeingGifted.user_email == user).one_or_none()
        entry["isBeingGifted"] = existing_relation is not None
    return res, 200


def create(giftgroup, user, token_info):
    existing_user = User.query.filter(User.email == user).one_or_none()
    new_giftGroup = giftGroup_schema.load(giftgroup, session=db.session)
    db.session.add(new_giftGroup)
    new_giftGroup.isBeingGifted.add(IsBeingGifted(user=existing_user))
    db.session.commit()
    return giftGroup_schema.dump(new_giftGroup), 201


def update(giftgroup_id, giftgroup, user, token_info):
    existing_giftGroup = GiftGroup.query.filter(GiftGroup.id == giftgroup_id).one_or_none()
    if existing_giftGroup is None:
        abort(
            404,
            f"Giftgroup with id {giftgroup_id} not found"
        )
    existing_relation = existing_giftGroup.isBeingGifted
    if not any(isBeingGifted.user_email == user for isBeingGifted in existing_relation):
        abort(
            403,
            f"User {user} is not allowed to update Giftgroup with id {giftgroup_id}"
        )
    updated_giftGroup = giftGroup_schema.load(giftgroup, session=db.session)
    existing_giftGroup.name = updated_giftGroup.name
    db.merge(existing_giftGroup)
    db.commit()
    return giftGroup_schema.dump(existing_giftGroup), 201


def addUserToGroup(email, giftgroup_id, user, token_info):
    existing_relation = IsBeingGifted.query.filter(IsBeingGifted.giftGroup_id == giftgroup_id,
                                                   IsBeingGifted.user_email == email).one_or_none()
    if existing_relation is not None:
        abort(
            409,
            f"Giftgroup Relation between {giftgroup_id} und {email} already exists."
        )
    existing_giftGroup = GiftGroup.query.filter(GiftGroup.id == giftgroup_id).one_or_none()
    existing_user = User.query.filter(User.email == email).one_or_none()
    if existing_user is not None:
        if existing_giftGroup is not None:
            if existing_giftGroup.editable:
                existing_giftGroup.isBeingGifted.add(IsBeingGifted(user=existing_user))
                db.session.commit()
                return make_response(f"Giftgroup {giftgroup_id} linked with user_email {email}", 201)
            else:
                abort(403,
                      "Main-Giftgroups can't have more than one member")
        else:
            abort(404,
                  f"Giftgroup with the id {giftgroup_id} does not exist")
    else:
        abort(404,
              f"User with email {email} does not exist")


def removeUserOffGroup(email, giftgroup_id, user, token_info):
    existing_relation = IsBeingGifted.query.filter(IsBeingGifted.giftGroup_id == giftgroup_id,
                                                   IsBeingGifted.user_email == email).one_or_none()
    if existing_relation is None:
        abort(
            404,
            f"User with email {email} is not being gifted in Giftgroup {giftgroup_id}"
        )
    existing_giftGroup = GiftGroup.query.filter(GiftGroup.id == giftgroup_id).one_or_none()
    if not existing_giftGroup.editable:
        abort(
            403,
            f"User with email {email} can't be removed from Giftgroup {existing_giftGroup.name} because that is his main Giftgroup"
        )
    db.session.delete(existing_relation)
    db.session.commit()
    return make_response(f"User with email {email} succesfully deleted from Giftgroup {existing_giftGroup.name}", 204)
