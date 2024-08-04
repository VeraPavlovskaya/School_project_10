import datetime
import sqlalchemy as db
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Events(SqlAlchemyBase):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.VARCHAR, nullable=False)
    description = db.Column(db.VARCHAR, nullable=False)
    event_picture = db.Column(db.VARCHAR, nullable=True)
    event_date_time = db.Column(db.DateTime, default=datetime.datetime.now)
    created_date = db.Column(db.DateTime, default=datetime.datetime.now)
    school_num = db.Column(db.VARCHAR, nullable=True)
    location = db.Column(db.VARCHAR, nullable=True)
    organizer = db.Column(db.VARCHAR, nullable=True)
    contacts = db.Column(db.VARCHAR, nullable=True)
    # Foreign key
    poster_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    feedbacks = orm.relationship("Feedbacks", backref='event')
    # Association

