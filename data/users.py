import datetime
import sqlalchemy
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
    print('class User start')
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.VARCHAR, index=True, unique=True, nullable=True)
    surname = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True)
    fathers_name = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True)
    status = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True)
    school_num = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True)
    class_num = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True)
    city = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    active = sqlalchemy.Column(sqlalchemy.CHAR, nullable=True)
    events = orm.relationship("Events", back_populates='user')
    print('class User end')

    def __repr__(self):
        return f'<User> {self.id} {self.name} {self.email}'

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
