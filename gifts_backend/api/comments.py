from flask import make_response,abort
from models import Comment, comment_schema, comments_schema, User, Gift
from config import db


def create(gift_id, comment, user, token_info):
    existing_user = User.query.filter(User.email == user).one_or_none()
    if existing_user is None:
        abort(
            400
        )
    existing_gift = Gift.query.filter(Gift.id == gift_id).one_or_none()
    if existing_gift is None:
        abort(
            404,
            f"Gift with id {gift_id} does not exist"
        )
    if not comment.get("public"):
        existing_giftgroup = existing_gift.giftGroup
        if any(isBeingGifted.user_email == user for isBeingGifted in existing_giftgroup.isBeingGifted):
            abort(
                400,
                "User can't create a comment he can't access afterwards"
            )
    new_comment = Comment(**comment, user_email=user, gift_id=gift_id)
    existing_gift.comment.add(new_comment)
    existing_user.comment.add(new_comment)
    db.session.commit()
    return comment_schema.dump(new_comment), 201


def read_all(gift_id, user, token_info):
    existing_gift = Gift.query.filter(Gift.id == gift_id).one_or_none()
    if existing_gift is None:
        abort(
            404,
            f"Gift with id {gift_id} does not exist"
        )
    comments = existing_gift.comment
    if any(isBeingGifted.user_email == user for isBeingGifted in existing_gift.giftGroup.isBeingGifted):
        comments = [comment for comment in comments if comment.public]
    return comments_schema.dump(comments), 200


def update(gift_id, comment_id, comment, user, token_info):
    existing_gift = Gift.query.filter(Gift.id == gift_id).one_or_none()
    if existing_gift is None:
        abort(
            404,
            f"Gift with id {gift_id} does not exist"
        )
    existing_comment = Comment.query.filter(Comment.id == comment_id).one_or_none()
    if existing_comment is None:
        abort(
            404,
            f"Comment with id {comment_id} does not exist"
        )
    if existing_comment.user_email != user:
        abort(
            403,
            f"User not allowed to update comment {comment_id}"
        )
    if not comment.get("public"):
        existing_giftgroup = existing_gift.giftGroup
        if any(isBeingGifted.user_email == user for isBeingGifted in existing_giftgroup.isBeingGifted):
            abort(
                400,
                "User can't create a comment he can't access afterwards"
            )
    existing_comment.content = comment.get("content")
    existing_comment.publicc = comment.get("public")
    db.session.merge(existing_comment)
    db.session.commit()
    return comment_schema.dump(existing_comment), 200


def delete(gift_id, comment_id, user, token_info):
    existing_gift = Gift.query.filter(Gift.id == gift_id).one_or_none()
    if existing_gift is None:
        abort(
            404,
            f"Gift with id {gift_id} does not exist"
        )
    existing_comment = Comment.query.filter(Comment.id == comment_id).one_or_none()
    if existing_comment is None:
        abort(
            404,
            f"Comment with id {comment_id} does not exist"
        )
    if existing_comment.user_email != user:
        abort(
            403,
            f"User not allowed to update comment {comment_id}"
        )
    db.session.delete(existing_comment)
    db.session.commit()
    return make_response(f"Comment with id {gift_id} succesfully deleted", 204)
