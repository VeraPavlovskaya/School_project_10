from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired
# from flask_ckeditor import CKEditorField

class FeedbackForm(FlaskForm):
    feedback = TextAreaField("Отзыв", validators=[DataRequired()])
    user_score = SelectField("Оценка пользователя", choices=[(2, 'Нормально'), (3, 'Неплохо'), (4, 'Хорошо'), (5, 'Великолепно')])
    is_anonymous = BooleanField("Оставить отзыв анонимно")
    submit = SubmitField('Сохранить')
