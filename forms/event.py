from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, FileField, DateTimeField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField

class EventForm(FlaskForm):
    title = StringField('Название мероприятия', validators=[DataRequired()])
    #description = TextAreaField("Описание мероприятия", validators=[DataRequired()], widget=TextArea)
    description = CKEditorField("Описание мероприятия", validators=[DataRequired()])
    event_picture = FileField("Фото")
    event_date_time = DateTimeField("Дата и время мероприятия", validators=[DataRequired()])
    submit = SubmitField('Сохранить')

# Create a search form
class SearchForm(FlaskForm):
    searched = StringField('Searched', validators=[DataRequired()])
    submit = SubmitField('Сохранить')