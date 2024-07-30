import datetime

import sqlalchemy as db
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Messages(SqlAlchemyBase):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject = db.Column(db.VARCHAR, nullable=False)
    text = db.Column(db.VARCHAR, nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.datetime.now)
    # Foreign key
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    # Association