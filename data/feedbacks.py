import datetime
import sqlalchemy as db
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Feedbacks(SqlAlchemyBase):
    __tablename__ = 'feedbacks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    feedback = db.Column(db.VARCHAR, nullable=False)
    user_score = db.Column(db.VARCHAR, nullable=True)
    sentiment_score = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, default=datetime.datetime.now)
    is_anonymous = db.Column(db.Boolean, default=False)
    # Foreign keys
    poster_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"))
