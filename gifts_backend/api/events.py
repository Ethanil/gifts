from flask import make_response,abort
from models import Event, event_schema, events_schema, User
from config import db


def create(event, user, token_info):
    existing_user = User.query.filter(User.email == user).one_or_none()
    if existing_user is None:
        abort(
            400
        )
    new_event = Event(**event, user_email=user)
    existing_user.event.add(new_event)
    db.session.commit()
    return event_schema.dump(new_event), 201


def read_all(user, token_info):
    events = Event.query.all()
    return events_schema.dump(events), 200


def update(event, event_id, user, token_info):
    existing_event = Event.query.filter(Event.id == event_id).one_or_none()
    if existing_event is None:
        abort(
            404,
            f"There is no event with id {event_id}"
        )
    if  existing_event.user_email != user:
        abort(
            403,
            f"User not allowed to update event {event_id}"
        )
    existing_event.name = event.get("name")
    existing_event.date = event.get("date")
    db.session.merge(existing_event)
    db.session.commit()
    return event_schema.dump(existing_event), 200


def delete(event_id, user, token_info):
    existing_event = Event.query.filter(Event.id == event_id).one_or_none()
    if existing_event is None:
        abort(
            404,
            f"There is no event with id {event_id}"
        )
    if  existing_event.user_email != user:
        abort(
            403,
            f"User not allowed to update event {event_id}"
        )
    db.session.delete(existing_event)
    db.session.commit()
    return make_response(f"Event with id {event_id} succesfully deleted", 204)
