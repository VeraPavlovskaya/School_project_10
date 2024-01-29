from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, BooleanField, RadioField, FileField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired

class RegisterForm(FlaskForm):
    email = EmailField('Электронная почта', validators=[DataRequired()])
    password = PasswordField('Пароль')
    password_again = PasswordField('Повторите пароль')
    name = StringField('Имя пользователя', validators=[DataRequired()])
    last_name = StringField('Фамилия', validators=[DataRequired()])
    fathers_name = StringField('Отчество')  # , validators=[DataRequired()])
    #status = RadioField('Статус')  # , validators=[DataRequired()])
    occupation = RadioField('Тип пользователя', choices=[('Учитель', 'Учитель'),
                                           ('Ученик', 'Ученик'),
                                           ('Родитель', 'Родитель'),
                                           ('Другое', 'Другое')])
    school_num = StringField('Номер учебного заведения', validators=[DataRequired()])
    class_num = StringField('Номер класса') #, validators=[DataRequired()])
    city = StringField('Город') #, validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    profile_picture = FileField("Фото профиля")
    submit = SubmitField('Создать')
    save = SubmitField('Сохранить изменения')


# Сделаем форму авторизации пользователя, назовем ее LoginForm.
# Далее сделаем к ней шаблон login.html
# И, наконец, сделаем обработчик адреса /login: см файл main.py
class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
