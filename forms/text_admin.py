'''from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, FileField, DateTimeField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField


class TextForm(FlaskForm):
    title = StringField('Название письма', validators=[DataRequired()])
    description = CKEditorField("Содержание письма", validators=[DataRequired()])
    event_picture = FileField("Фото")
    submit = SubmitField('Отправить')'''
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class MessageForm(FlaskForm):
    subject = StringField('Тема письма', validators=[DataRequired()])
    text = TextAreaField('Текст письма', validators=[DataRequired()])
    submit = SubmitField('Отправить администратору')
