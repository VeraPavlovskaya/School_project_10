import datetime
import sqlalchemy as db
from flask_login import UserMixin
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase


# Наша модель для пользователей
# должна содержать ряд методов
# для корректной работы flask-login,
# но мы не будем создавать их руками,
# а воспользуемся множественным наследованием.
# Далее см. в файле: forms/user.py
class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.VARCHAR, nullable=True)
    email = db.Column(db.VARCHAR, index=True, unique=True, nullable=True)
    last_name = db.Column(db.VARCHAR, nullable=True)
    fathers_name = db.Column(db.VARCHAR, nullable=True)
    occupation = db.Column(db.VARCHAR, nullable=True)
    school_num = db.Column(db.VARCHAR, nullable=True)
    class_num = db.Column(db.VARCHAR, nullable=True)
    city = db.Column(db.VARCHAR, nullable=True)
    about = db.Column(db.VARCHAR, nullable=True)
    hashed_password = db.Column(db.VARCHAR, nullable=True)
    created_date = db.Column(db.DateTime, default=datetime.datetime.now)
    is_active = db.Column(db.CHAR, nullable=True)
    profile_picture = db.Column(db.VARCHAR, nullable=True)
    # A user can create many events
    events = orm.relationship("Events", backref='event_poster')
    feedbacks = orm.relationship("Feedbacks", backref='feedback_poster')

    def __repr__(self):
        return f'<User> {self.id} {self.name} {self.email}'

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
