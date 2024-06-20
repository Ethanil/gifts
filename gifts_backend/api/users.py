import os
import random
import string
import smtplib
from flask import make_response, abort
from config import db
import time
import jwt
from models import User, user_schema, user_schema_without_password, users_schema_without_password, giftGroup_schema, \
    IsBeingGifted, GiftGroup, IsSpecialUser
from os import getenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import email.utils as utils
from uuid import uuid4
import base64


def create(user):
    # TODO add avatar
    email = user.get("email").lower()
    existing_user = User.query.filter(User.email == email).one_or_none()
    if existing_user is None:
        if user.get("avatar") is None or user.get("avatar") == "":
            user["avatar"] = email
        userWithoutSpecialGiftGroup = {'firstName': user.get("firstName"), 'lastName': user.get("lastName"),
                                       'email': user.get("email"), 'avatar': user.get("avatar"),
                                       'password': user.get("password")}
        new_user = user_schema.load(userWithoutSpecialGiftGroup, session=db.session)
        db.session.add(new_user)
        if user.get("onlyViewing") is not None and user.get("startViewingGroup"):
            specialGiftGroup = GiftGroup.query.filter(GiftGroup.id == user.get("startViewingGroup")).one_or_none()
            if specialGiftGroup is None:
                abort(400, "Giftgroup with that id does not exist!")
            new_user.onlyViewing = True
            new_user.isSpecialUser.add(IsSpecialUser(giftGroup=specialGiftGroup))
        else:
            # TODO internationalisation?
            if user.get('lastName') != "":
                listname = f"{user.get('firstName')} {user.get('lastName')}'s Liste"
            else:
                listname = f"{user.get('firstName')}'s Liste"
            new_giftGroup = giftGroup_schema.load(
                {"name": listname, "editable": False}, session=db.session)
            db.session.add(new_giftGroup)
            new_user.isBeingGifted.add(IsBeingGifted(giftGroup=new_giftGroup))
        db.session.commit()
        return user_schema.dump(new_user), 201
    else:
        abort(
            406,
            f"User with email {email} already exists",
        )


def read_all(user, token_info, giftgroup_id=-1):
    users = User.query.all()
    if giftgroup_id == -1:
        return users_schema_without_password.dump(users), 200
    existing_giftGroup = GiftGroup.query.filter(GiftGroup.id == giftgroup_id).one_or_none()
    if existing_giftGroup is None:
        abort(
            404,
            f"Giftgroup with id {giftgroup_id} not found"
        )
    users_that_are_being_gifted = [isBeingGifted.user for isBeingGifted in existing_giftGroup.isBeingGifted]
    users = [user for user in users if user not in users_that_are_being_gifted]
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
    exisiting_user = User.query.filter(User.email == email).one_or_none()
    if exisiting_user is None:
        abort(403,
              "not authorized to delete other users")
    if not (exisiting_user.onlyViewing or email == user):
        if email != user:
            abort(403,
                  "not authorized to delete other users")
    elif exisiting_user.onlyViewing:
        if len(exisiting_user.isSpecialUser) > 1:
            abort(403,
                  "not authorized to delete this user")
    db.session.delete(exisiting_user)
    db.session.commit()
    return make_response(f"User with email {email} succesfully deleted", 204)


def update(email, new_user_data, user, token_info):
    if email != user:
        abort(
            403,
            "Not allowed to update another user"
        )
    existing_user = User.query.filter(User.email == email).one_or_none()
    if existing_user is None:
        abort(
            404,
            f"User with email {email} not found"
        )
    try:
        existing_user.ph.verify(existing_user.password, new_user_data.get("oldPassword"))
    except:
        abort(
            403,
            f"Password is not correct"
        )
    new_user_data["email"] = new_user_data.get("email").lower()
    if new_user_data["email"] != email:
        another_user = User.query.filter(User.email == new_user_data.get("email")).one_or_none()
        if another_user:
            abort(
                406,
                f"User with email {new_user_data.get('email')} already exists"
            )
    password = ""
    if new_user_data.get("newPassword") is not None:
        existing_user.password = new_user_data.get("newPassword")
    else:
        pass
    if existing_user.firstName != new_user_data.get("firstName") or existing_user.lastName != new_user_data.get(
            "lastName"):
        ownGiftgroup = [isBeingGifted.giftGroup for isBeingGifted in existing_user.isBeingGifted if
                        not isBeingGifted.giftGroup.editable][0]
        if new_user_data.get('lastName') != "":
            ownGiftgroup.name = f"{new_user_data.get('firstName')} {new_user_data.get('lastName')}'s Liste"
        else:
            ownGiftgroup.name = f"{new_user_data.get('firstName')}'s Liste"
    existing_user.firstName = new_user_data.get("firstName")
    existing_user.lastName = new_user_data.get("lastName")
    existing_user.avatar = saveAvatar(new_user_data.get("avatar"), existing_user.avatar)
    db.session.merge(existing_user)
    db.session.commit()
    return user_schema.dump(existing_user), 201


def saveAvatar(newAvatar, oldAvatar):
    splitted_new_avatar = newAvatar.split(";")
    if len(splitted_new_avatar) and splitted_new_avatar[0].startswith("data:image/"):
        folder_path = getenv("PICTURE_STORAGE")
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        filePath = oldAvatar
        if not os.path.isfile(oldAvatar):
            filename = f"{uuid4()}.{splitted_new_avatar[0].split('/')[1]}"
            filePath = os.path.join(folder_path, filename)
        with open(filePath, "wb") as fh:
            fh.write(base64.decodebytes(bytes(splitted_new_avatar[1].split(",")[1], "utf-8")))
        return filePath
    return newAvatar


key = getenv('JWT_SECRET_KEY')
algorithm = getenv('HASHING_ALGORITHM')
tokenLifeTimeSeconds = int(getenv('TOKEN_LIFE_IN_SECONDS'))
issuer = getenv('JWT_TOKEN_ISSUER')


def login(authentication):
    email = authentication["email"].lower()
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


def sendPasswordResetEmail(email):
    existing_user = User.query.filter(User.email == email).one_or_none()
    if existing_user is None:
        abort(
            401,
            f"User with email {email} does not exist"
        )
    resetCode = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    existing_user.resetCode = resetCode
    sendResetEmail(resetCode, email)
    db.session.merge(existing_user)
    db.session.commit()


def sendResetEmail(resetCode, email):
    smtp_server = os.getenv('SMTP_SERVER')
    port = 587
    if os.getenv("USE_SSL") == "True":
        port = 465
    server = smtplib.SMTP(smtp_server, port)
    server.starttls()

    sender_email = os.getenv("SENDER_EMAIL")
    password = os.getenv("EMAIL_PASSWORD")
    server.login(sender_email, password)
    subject = f"Passwort Rücksetzungscode für {os.getenv('JWT_TOKEN_ISSUER')}"
    body = f"""
        <html>
            <body>
                <h1 style="margin-bottom: 10px;">Hallo,</h1>
                dein Passwort-Reset-Code lautet:
                <div style="font-size: 40px; margin: 20px;">{resetCode}</div> 
                Mithilfe dieses codes kannst du dein Passwort neu setzen!<br><br>
                Viel Spaß beim Schenken und beschenkt werden!
            </body>
        </html>
    """
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = email
    message["Subject"] = subject
    message["message-id"] = utils.make_msgid(domain=os.getenv("DOMAIN_FOR_MESSAGEID"))
    message.attach(MIMEText(body, "html"))
    text = message.as_string()
    server.sendmail(sender_email, email, text)
    server.quit()


def resetPassword(email, password_and_code):
    existing_user = User.query.filter(User.email == email).one_or_none()
    if existing_user is None:
        abort(
            401,
            f"User with email {email} does not exist"
        )
    if existing_user.resetCode is None:
        abort(
            403,
            f"Wrong code"
        )
    try:
        existing_user.ph.verify(existing_user.resetCode, password_and_code["code"])
    except:
        abort(
            403,
            f"Wrong code"
        )
    existing_user.password = password_and_code["password"]
    existing_user.resetCode = None
    db.session.merge(existing_user)
    db.session.commit()
    return "Password set", 200
