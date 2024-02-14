from flask import make_response, abort
from config import db
import time
import jwt
from models import User, user_schema, user_schema_without_password, users_schema_without_password, giftGroup_schema, IsBeingGifted


def create(user):
    email = user.get("email")
    existing_user = User.query.filter(User.email == email).one_or_none()
    if existing_user is None:
        user.pop("avatar", None)
        new_user = user_schema.load(user, session=db.session)
        db.session.add(new_user)
        # TODO internationalisation?
        new_giftGroup = giftGroup_schema.load(
            {"name": f"{user.get('firstName')} {user.get('lastName')}'s Liste", "editable": False}, session=db.session)
        db.session.add(new_giftGroup)
        new_user.isBeingGifted.add(IsBeingGifted(giftGroup=new_giftGroup))
        db.session.commit()
        return user_schema.dump(new_user), 201
    else:
        abort(
            406,
            f"User with email {email} already exists",
        )


def read_all(user, token_info):
    users = User.query.all()
    return users_schema_without_password.dump(users), 200


def get_session(user, token_info):
    exisiting_user = User.query.filter(User.email == user).one_or_none()
    if exisiting_user is None:
        abort(
            404,
            f"User with email {user} not found"
        )
    return user_schema_without_password.dump(exisiting_user), 200


def delete(email, user, token_info):
    if email != user:
        abort(403,
              "not authorized to delete other users")
    exisiting_user = User.query.filter(User.email == email).one_or_none()
    if exisiting_user:
        db.session.delete(exisiting_user)
        db.session.commit()
        return make_response(f"User with email {email} succesfully deleted", 204)


def update(email, new_user_data, user, token_info):
    if email != user:
        abort(
            403,
            "Not allowed to update another user"
        )
    exisiting_user = User.query.filter(User.email == email).one_or_none()
    if exisiting_user is None:
        abort(
            404,
            f"User with email {email} not found"
        )
    another_user = User.query.filter(User.email == new_user_data.get("email")).one_or_none()
    if another_user:
        abort(
            406,
            f"User with email {new_user_data.get('email')} already exists"
        )
    updated_user = user_schema.load(new_user_data, session=db.session)
    exisiting_user.email = updated_user.email
    exisiting_user.password = updated_user.password
    # exisiting_user.avatar = updated_user.avatar
    db.session.merge(exisiting_user)
    db.session.commit()
    return user_schema.dump(exisiting_user), 201


key = "CrazySecretString"
algorithm = "HS256"
tokenLifeTimeSeconds = 60 * 60 * 24 * 3
issuer = "theIssuerOfTheToken"


def login(authentication):
    email = authentication["email"]
    password = authentication["password"]
    # check if credentials are correct
    existing_user = User.query.filter(User.email == email).one_or_none()
    if existing_user is None:
        abort(
            401,
            f"User with email {email} does not exist"
        )
    try:
        existing_user.ph.verify(existing_user.password, password)
    except:
        abort(
            403,
            f"Password is not correct"
        )
    if existing_user.ph.check_needs_rehash(existing_user.password):
        existing_user.password = password
        db.session.merge(existing_user)
        db.session.commit()
    timestamp = int(time.time())
    payload = {
        "active": True,
        "iss": issuer,
        "iat": timestamp,
        "exp": timestamp + tokenLifeTimeSeconds,
        "sub": email,
        "username": email
    }
    return make_response({
        "access_token": jwt.encode(payload, key, algorithm=algorithm),
        "token_type": "JWT",
        "expires_in": tokenLifeTimeSeconds
    }), 200



def decode_token(token):
    return jwt.decode(token, key, issuer=issuer, algorithms=algorithm)
