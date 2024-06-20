from flask import make_response, abort
from models import GiftGroup, giftGroup_schema, giftGroups_schema, User, IsBeingGifted, IsInvited, IsSpecialUser, \
    HasRequestedReservationFreeing, HasReserved
from config import db
from api.users import delete


def read_all(user, token_info):
    all_users = User.query.all()
    current_user = None
    for u in all_users:
        if u.email == user:
            current_user = u
            break
    giftGroups = []
    if current_user.onlyViewing:
        giftGroups = [isSpecialUser.giftGroup for isSpecialUser in current_user.isSpecialUser]
        if len(giftGroups) == 0:
            abort(500, "This only viewing user has no giftgroup they can view!")
        pass
    else:
        giftGroups = GiftGroup.query.all()
    # decorate giftGroups with Ownership-value
    decorated_gift_groups: list[tuple[GiftGroup, int | float]] = []
    for giftGroup in giftGroups:
        if giftGroup.isSecretGroup and user in [isBeingGifted.user.email for isBeingGifted in giftGroup.isBeingGifted]:
            continue
        emails_of_usersBeinggifted = [isBeinggifted.user_email for isBeinggifted in giftGroup.isBeingGifted]
        if user in emails_of_usersBeinggifted:
            if not giftGroup.editable:
                decorated_gift_groups.append((giftGroup, 1))
            else:
                decorated_gift_groups.append((giftGroup, 2))
        else:
            decorated_gift_groups.append((giftGroup, float('inf')))
    # sort on Ownershipvalue, then groupname
    decorated_gift_groups = sorted(sorted(decorated_gift_groups, key=lambda tuple: tuple[0].name),
                                   key=lambda tuple: tuple[1])
    giftGroups = [giftGroup for giftGroup, _ in decorated_gift_groups]
    res = giftGroups_schema.dump(giftGroups)
    for index, entry in enumerate(res):
        entry["usersBeingGifted"] = [isBeingGifted.user.email for isBeingGifted in giftGroups[index].isBeingGifted]
        entry["isBeingGifted"] = user in entry["usersBeingGifted"]
        entry["invitations"] = [isInvited.user.email for isInvited in giftGroups[index].isInvited]
        entry["isInvited"] = user in entry["invitations"]
        entry["isSpecialUser"] = [isSpecialUser.user_email for isSpecialUser in giftGroups[index].isSpecialUser]
        entry["invitableUsers"] = [invitableUser.email
                                   for invitableUser in all_users
                                   if entry["editable"]
                                   and invitableUser not in [isInvited.user for isInvited in
                                                             giftGroups[index].isInvited]
                                   and invitableUser not in [isBeingGifted.user for isBeingGifted in
                                                             giftGroups[index].isBeingGifted]]
    return res, 200


def create(giftgroup, user, token_info):
    if giftgroup.get('name') == "":
        abort(400,
              "empty name is not allowed")
    currentUser = User.query.filter(User.email == user).one_or_none()
    if currentUser is None or currentUser.onlyViewing:
        abort(403,
              "The user can't create new Lists")
    sanitized_giftgroup = {}
    sanitized_giftgroup['name'] = giftgroup['name']
    sanitized_giftgroup['isSecretGroup'] = giftgroup['isSecretGroup']
    sanitized_giftgroup['editable'] = True
    new_giftGroup = giftGroup_schema.load(sanitized_giftgroup, session=db.session)
    db.session.add(new_giftGroup)
    if giftgroup.get('invitations') is not None:
        for invited_user in giftgroup.get('invitations'):
            existing_user = User.query.filter(User.email == invited_user).one_or_none()
            if existing_user is None:
                abort(
                    404,
                    f"User with email {invited_user} not found"
                )
            new_giftGroup.isInvited.add(IsInvited(user=existing_user))
    if giftgroup.get('usersBeingGifted') is not None:
        for gifted_user in giftgroup.get('usersBeingGifted'):
            existing_user = User.query.filter(User.email == gifted_user).one_or_none()
            if existing_user is None:
                abort(
                    404,
                    f"User with email {gifted_user} not found"
                )
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
    existing_relations = existing_giftGroup.isBeingGifted
    if not any(isBeingGifted.user_email == user for isBeingGifted in
               existing_relations) and not existing_giftGroup.isSecretGroup:
        abort(
            403,
            f"User {user} is not allowed to update Giftgroup with id {giftgroup_id}"
        )
    if not existing_giftGroup.editable:
        abort(
            403,
            "That giftgroup can't be edited"
        )
    existing_giftGroup.name = giftgroup['name']
    invitationEmails = [usr for usr in giftgroup.get('invitations')]
    existing_giftGroup.isInvited = set(
        filter(lambda isInvited: isInvited.user_email in invitationEmails, existing_giftGroup.isInvited))
    invitedUser = [isInvited.user for isInvited in existing_giftGroup.isInvited]
    if giftgroup.get('invitations') is not None:
        for invited_user in giftgroup.get('invitations'):
            existing_user = User.query.filter(User.email == invited_user).one_or_none()
            if existing_user is None:
                abort(
                    404,
                    f"User with email {invited_user} not found"
                )
            if existing_user not in invitedUser:
                existing_giftGroup.isInvited.add(IsInvited(user=existing_user))
    if giftgroup.get('usersBeingGifted') is not None:
        isBeingGiftedEmails = [usr for usr in giftgroup.get('usersBeingGifted')]
    else:
        isBeingGiftedEmails = []
    existing_giftGroup.isBeingGifted = set(
        filter(lambda isBeingGifted: isBeingGifted.user_email in isBeingGiftedEmails, existing_giftGroup.isBeingGifted))
    if len(existing_giftGroup.isBeingGifted) == 0:
        db.session.delete(existing_giftGroup)
    else:
        db.session.merge(existing_giftGroup)
    db.session.commit()
    return giftGroup_schema.dump(existing_giftGroup), 201


def addUserToGroup(giftgroup_id, user, token_info, decline=None, specialUserEmail=""):
    if decline is not None and specialUserEmail != "":
        abort(400, "Bad request")
    existing_giftGroup = GiftGroup.query.filter(GiftGroup.id == giftgroup_id).one_or_none()
    existing_user = User.query.filter(User.email == user).one_or_none()
    if specialUserEmail != "":
        specialUser = User.query.filter(User.email == specialUserEmail).one_or_none()
        if not specialUser.onlyViewing:
            abort(400, "This user is not a special User")
        if specialUser in existing_giftGroup.isSpecialUser:
            abort(403, "This user is already a special user for that group")
        if not existing_giftGroup.isSecretGroup and existing_user not in [isBeingGifted.user for isBeingGifted in
                                                                          existing_giftGroup.isBeingGifted]:
            abort(403, "The User is not allowed to edit that group")
        existing_giftGroup.isSpecialUser.add(IsSpecialUser(user=specialUser))
    else:
        existing_relation = IsBeingGifted.query.filter(IsBeingGifted.giftGroup_id == giftgroup_id,
                                                       IsBeingGifted.user_email == user).one_or_none()
        if existing_relation is not None:
            abort(
                409,
                f"Giftgroup Relation between {giftgroup_id} und {user} already exists."
            )
        if existing_giftGroup is None:
            abort(404,
                  f"Giftgroup with the id {giftgroup_id} does not exist")
        if not existing_giftGroup.editable and specialUserEmail == "":
            abort(403,
                  "Main-Giftgroups can't have more than one member")
        if existing_user is None:
            abort(404,
                  f"User with email {user} does not exist")

        if decline is None:
            existing_giftGroup.isBeingGifted.add(IsBeingGifted(user=existing_user))
        if decline is None or decline:
            existing_giftGroup.isInvited = set(filter(lambda invitation: invitation.user_email != user,
                                                      GiftGroup.query.filter(
                                                          GiftGroup.id == giftgroup_id).one_or_none().isInvited))
    db.session.merge(existing_giftGroup)
    db.session.commit()
    return make_response(f"Giftgroup {giftgroup_id} linked with user_email {user}", 201)


def removeUserFromGroup(email, giftgroup_id, user, token_info):
    userWithThatEmail = User.query.filter(User.email == email).one_or_none()
    if userWithThatEmail is None:
        abort(404, f"User with the email {email} does not exist")
    existing_giftGroup = GiftGroup.query.filter(GiftGroup.id == giftgroup_id).one_or_none()
    if user not in [isBeingGifted.user_email for isBeingGifted in
                    existing_giftGroup.isBeingGifted] and not existing_giftGroup.isSecretGroup:
        abort(403, f"User {user} does not have the correct access")
    if userWithThatEmail.onlyViewing:
        if email not in [isSpecialUser.user_email for isSpecialUser in existing_giftGroup.isSpecialUser]:
            abort(404, f"User with email {email} can't be removed from that group")
        existing_relation = \
            [isSpecialUser for isSpecialUser in existing_giftGroup.isSpecialUser if isSpecialUser.user_email == email][
                0]
        if len(userWithThatEmail.isSpecialUser) <= 1:
            delete(email, email, user)
            db.session.commit()
            return make_response(f"User with email {email} succesfully deleted", 204)
        else:
            has_requested_reservation_freeing = HasRequestedReservationFreeing.query.filter(
                HasRequestedReservationFreeing.user_email == email).all()
            has_requested_reservation_freeing = [requested for requested in has_requested_reservation_freeing if
                                                 requested.gift.giftGroup_id == giftgroup_id]
            has_reserved = HasReserved.query.filter(HasReserved.user_email == email).all()
            has_reserved = [reserved for reserved in has_reserved if reserved.gift.giftGroup_id == giftgroup_id]
            is_invited = IsInvited.query.filter(IsInvited.user_email == email,
                                                IsInvited.giftGroup_id == giftgroup_id).all()
            is_special_user = IsSpecialUser.query.filter(IsSpecialUser.user_email == email,
                                                         IsSpecialUser.giftGroup_id == giftgroup_id).all()
            for entry in has_requested_reservation_freeing + has_reserved + is_invited + is_special_user:
                db.session.delete(entry)
            db.session.commit()
            return make_response(f"User with email {email} succesfully removed from that group", 204)
    else:
        existing_relation = IsBeingGifted.query.filter(IsBeingGifted.giftGroup_id == giftgroup_id,
                                                       IsBeingGifted.user_email == email).one_or_none()
        if not existing_giftGroup.editable:
            abort(
                403,
                f"User with email {email} can't be removed from Giftgroup {existing_giftGroup.name} because that is his main Giftgroup"
            )
        if existing_relation is None:
            abort(
                404,
                f"User with email {email} is not being gifted in Giftgroup {giftgroup_id}"
            )
    db.session.delete(existing_relation)
    db.session.commit()
    return make_response(f"User with email {email} succesfully deleted from Giftgroup {existing_giftGroup.name}", 204)
