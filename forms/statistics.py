from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired
from flask_ckeditor import CKEditorField

class StatisticsForm(FlaskForm):
    plot_type = SelectField("Вид графика", choices=[(1, 'Круговая диаграмма оценок'),
                                                    (2, 'Гистограмма'),
                                                    (3, 'Ящик с усами'),
                                                    (4, 'График рассеяния')])
    submit = SubmitField('Построить график')
