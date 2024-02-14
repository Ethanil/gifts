from config import db, ma
from typing import Set, Optional
from datetime import datetime
from enum import Enum
from argon2 import PasswordHasher


class GiftStrength(str, Enum):
    OKAY = 1  # Okay
    GOOD = 2  # Gut
    GREAT = 3  # Großartig
    AMAZING = 4  # Erstaunlich
    AWESOME = 5  # Fantastisch


class BaseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        load_instance = True
        sqla_session = db.session


class User(db.Model):
    __tablename__ = "user"

    email: db.Mapped[str] = db.mapped_column(db.VARCHAR(256), primary_key=True)
    firstName: db.Mapped[str] = db.mapped_column(db.VARCHAR(256))
    lastName: db.Mapped[str] = db.mapped_column(db.VARCHAR(256))
    password: db.Mapped[str] = db.mapped_column(db.VARCHAR(256))
    avatar: db.Mapped[Optional[str]] = db.mapped_column(db.TEXT)
    isBeingGifted: db.Mapped[Set["IsBeingGifted"]] = db.relationship(back_populates="user",
                                                                     cascade="all, delete-orphan")
    hasReserved: db.Mapped[Set["HasReserved"]] = db.relationship(back_populates="user", cascade="all, delete-orphan")
    hasRequestedReservationFreeing: db.Mapped[Set["HasRequestedReservationFreeing"]] = db.relationship(
        back_populates="user", cascade="all, delete-orphan")
    gift: db.Mapped[Set["Gift"]] = db.relationship(back_populates="user", cascade="all, delete-orphan")
    comment: db.Mapped[Set["Comment"]] = db.relationship(back_populates="user", cascade="all, delete-orphan")
    event: db.Mapped[Set["Event"]] = db.relationship(back_populates="user", cascade="all, delete-orphan")

    ph = PasswordHasher()

    @db.validates('password')
    def _validate_password(self, key, password):
        return self.ph.hash(password)


class GiftGroup(db.Model):
    __tablename__ = "giftGroup"

    id: db.Mapped[int] = db.mapped_column(db.INTEGER, primary_key=True)
    editable: db.Mapped[bool] = db.mapped_column(db.BOOLEAN, default=True)

    gift: db.Mapped[Set["Gift"]] = db.relationship(back_populates="giftGroup", cascade="all, delete-orphan")
    isBeingGifted: db.Mapped[Set["IsBeingGifted"]] = db.relationship(back_populates="giftGroup",
                                                                     cascade="all, delete-orphan", passive_deletes=True)
    name: db.Mapped[str] = db.mapped_column(db.VARCHAR(256))


class IsBeingGifted(db.Model):
    __tablename__ = "isBeingGifted"

    giftGroup_id: db.Mapped[int] = db.mapped_column(db.INTEGER, db.ForeignKey("giftGroup.id", ondelete="CASCADE"),
                                                    primary_key=True)
    giftGroup: db.Mapped["GiftGroup"] = db.relationship(back_populates="isBeingGifted")
    user_email: db.Mapped[str] = db.mapped_column(db.VARCHAR(256), db.ForeignKey("user.email"), primary_key=True)
    user: db.Mapped["User"] = db.relationship(back_populates="isBeingGifted")


class HasReserved(db.Model):
    __tablename__ = "has_reserved"

    gift_id: db.Mapped[int] = db.mapped_column(db.INTEGER, db.ForeignKey("gift.id", ondelete="CASCADE"),
                                               primary_key=True)
    gift: db.Mapped["Gift"] = db.relationship(back_populates="hasReserved")
    user_email: db.Mapped[str] = db.mapped_column(db.VARCHAR(256), db.ForeignKey("user.email"), primary_key=True)
    user: db.Mapped["User"] = db.relationship(back_populates="hasReserved")


class HasRequestedReservationFreeing(db.Model):
    __tablename__ = "has_requested_reservation_freeing"

    gift_id: db.Mapped[int] = db.mapped_column(db.INTEGER, db.ForeignKey("gift.id", ondelete="CASCADE"),
                                               primary_key=True)
    gift: db.Mapped["Gift"] = db.relationship(back_populates="hasRequestedReservationFreeing")
    user_email: db.Mapped[str] = db.mapped_column(db.VARCHAR(256), db.ForeignKey("user.email"), primary_key=True)
    user: db.Mapped["User"] = db.relationship(back_populates="hasRequestedReservationFreeing")


class Gift(db.Model):
    __tablename__ = "gift"

    id: db.Mapped[int] = db.mapped_column(db.INTEGER, primary_key=True)
    name: db.Mapped[str] = db.mapped_column(db.VARCHAR(256))

    description: db.Mapped[str] = db.mapped_column(db.TEXT)
    price: db.Mapped[float] = db.mapped_column(db.FLOAT)
    link: db.Mapped[str] = db.mapped_column(db.VARCHAR(2083))
    picture: db.Mapped[Optional[str]] = db.mapped_column(db.TEXT)
    giftStrength: db.Mapped[GiftStrength] = db.mapped_column(db.Enum(GiftStrength))
    freeForReservation: db.Mapped[bool] = db.mapped_column(db.Boolean, default=False)

    giftGroup_id: db.Mapped[int] = db.mapped_column(db.Integer, db.ForeignKey("giftGroup.id"))
    user_email: db.Mapped[str] = db.mapped_column(db.VARCHAR(256), db.ForeignKey("user.email"))
    giftGroup: db.Mapped["GiftGroup"] = db.relationship(back_populates="gift")
    user: db.Mapped["User"] = db.relationship(back_populates="gift")
    comment: db.Mapped[Set["Comment"]] = db.relationship(back_populates="gift", cascade="all, delete-orphan")
    hasReserved: db.Mapped[Set["HasReserved"]] = db.relationship(back_populates="gift", cascade="all, delete-orphan",
                                                                 passive_deletes=True)
    hasRequestedReservationFreeing: db.Mapped[Set["HasRequestedReservationFreeing"]] = db.relationship(
        back_populates="gift", cascade="all, delete-orphan", passive_deletes=True)


class Comment(db.Model):
    __tablename__ = "comment"

    comment_id: db.Mapped[int] = db.mapped_column(db.Integer, primary_key=True)
    content: db.Mapped[str] = db.mapped_column(db.Text)
    timestamp: db.Mapped[datetime] = db.mapped_column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    public: db.Mapped[bool] = db.mapped_column(db.Boolean, default=False)

    user_email: db.Mapped[str] = db.mapped_column(db.VARCHAR(256), db.ForeignKey("user.email"))
    user: db.Mapped["User"] = db.relationship(back_populates="comment")
    gift_id: db.Mapped[int] = db.mapped_column(db.INTEGER, db.ForeignKey("gift.id"))
    gift: db.Mapped["Gift"] = db.relationship(back_populates="comment")


class Event(db.Model):
    __tablename__ = "event"

    id: db.Mapped[int] = db.mapped_column(db.Integer, primary_key=True)
    name: db.Mapped[str] = db.mapped_column(db.VARCHAR(256))
    date: db.Mapped[datetime] = db.mapped_column(db.DateTime)

    user_email: db.Mapped[str] = db.mapped_column(db.VARCHAR(256), db.ForeignKey("user.email"))
    user: db.Mapped["User"] = db.relationship(back_populates="event")


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta(BaseSchema.Meta):
        model = User


class UserSchemaWithoutPassword(ma.SQLAlchemySchema):
    class Meta(BaseSchema.Meta):
        model = User

    email = ma.auto_field()
    firstName = ma.auto_field()
    lastName = ma.auto_field()
    avatar = ma.auto_field()


class GiftGroupSchema(ma.SQLAlchemyAutoSchema):
    class Meta(BaseSchema.Meta):
        model = GiftGroup


class IsBeingGiftedSchema(ma.SQLAlchemyAutoSchema):
    class Meta(BaseSchema.Meta):
        model = IsBeingGifted


class GiftSchema(ma.SQLAlchemyAutoSchema):
    class Meta(BaseSchema.Meta):
        model = Gift


class CommentSchema(ma.SQLAlchemyAutoSchema):
    class Meta(BaseSchema.Meta):
        model = Comment


class EventSchema(ma.SQLAlchemyAutoSchema):
    class Meta(BaseSchema.Meta):
        model = Event


class HasReservedSchema(ma.SQLAlchemyAutoSchema):
    class Meta(BaseSchema.Meta):
        model = HasReserved


class HasRequestedReservationFreeingSchema(ma.SQLAlchemyAutoSchema):
    class Meta(BaseSchema.Meta):
        model = HasRequestedReservationFreeing


user_schema = UserSchema()
users_schema = UserSchema(many=True)
user_schema_without_password = UserSchemaWithoutPassword()
users_schema_without_password = UserSchemaWithoutPassword(many=True)
giftGroup_schema = GiftGroupSchema()
giftGroups_schema = GiftGroupSchema(many=True)
isBeingGifted_schema = IsBeingGiftedSchema()
isBeingGifteds_schema = IsBeingGiftedSchema(many=True)
gift_schema = GiftSchema()
gifts_schema = GiftSchema(many=True)
comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)
event_schema = EventSchema()
events_schema = EventSchema(many=True)
hasReserved_schema = HasReservedSchema()
hasReserveds_schema = HasReservedSchema(many=True)
hasRequestedReservationFreeing_schema = HasRequestedReservationFreeingSchema()
hasRequestedReservationFreeings_schema = HasRequestedReservationFreeingSchema(many=True)
