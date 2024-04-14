#2024-03-29_1
from flask import Flask, url_for, render_template, redirect, request, abort, flash, jsonify
# Импортируем нужные классы:
from flask_login import LoginManager
from flask_login import login_user
from flask_login import login_required
from flask_login import logout_user
from flask_login import current_user
from flask_ckeditor import CKEditor
from forms.event import EventForm, SearchForm
from forms.user import RegisterForm, LoginForm
from forms.feedback import FeedbackForm
from forms.statistics import StatisticsForm
from data.events import Events
from data.users import User
from data.feedbacks import Feedbacks
from data import db_session
import uuid as uuid
import os
from dostoevsky.tokenization import RegexTokenizer
from dostoevsky.models import FastTextSocialNetworkModel
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import logging
import json
import traceback
from werkzeug.exceptions import HTTPException
from sqlalchemy import func, or_

app = Flask(__name__)
ckeditor = CKEditor(app)

# Глобальные переменные. Путь к картинкам
USER_IMAGE_FOLDER = "static/images/users/"
EVENT_IMAGE_FOLDER = "static/images/events/"
GRAPHS_FOLDER = "static/images/graphs/"
app.config["USER_IMAGE_FOLDER"] = USER_IMAGE_FOLDER
app.config["EVENT_IMAGE_FOLDER"] = EVENT_IMAGE_FOLDER

# Инициализируем LoginManager:
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'myschoolproject_secret_key'
app.config['DEBUG'] = True

#logging.basicConfig(filename='./app.log', level=logging.INFO, format=f'%(asctime)s %(levelname)s %(name)s : %(message)s')


# Для верной работы flask-login у нас должна быть
# функция load_user для получения пользователя
# украшенная декоратором login_manager.user_loader
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

# Обработчик адреса logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


########################################################################################################################
## Функции работы с мероприятиями
########################################################################################################################

# Переход на страницу со списком мероприятий
@app.route('/events', methods=['GET', 'POST'])
def events():
    log("Rendering Events page")
    try:
        db_sess = db_session.create_session()
        log("created DB session")

        # Выберем все мероприятия из БД
        if request.method == "POST":
            srch_txt = "%{}%".format(request.form['searched'])
            srch_txt_cml = "%{}%".format(request.form['searched'].capitalize())
            srch_txt_upr = "%{}%".format(request.form['searched'].upper())
        else:
            srch_txt = srch_txt_cml = srch_txt_upr = "%"
        #form = SearchForm()
        #if form.validate_on_submit():
            # event.searched = form.searched.data
        #    events = db_sess.query(Events).filter(form.searched.data).first()
        print('searched_text=', srch_txt)
        print('searched_text_lower=', srch_txt_cml)
        events = db_sess.query(Events).filter(
                    or_(Events.title.ilike(srch_txt),
                        Events.description.ilike(srch_txt),
                        Events.title.ilike(srch_txt_cml),
                        Events.description.ilike(srch_txt_cml),
                        Events.title.ilike(srch_txt_upr),
                        Events.description.ilike(srch_txt_upr)
                        )
                    ).order_by(Events.event_date_time)
    except Exception as e:
        with open('error_events.log', 'a') as f:
            traceback.print_exc(file=f)
        log("Error rendering events:"+str(e))
        return str(e)
    return render_template('events.html', events=events)


# Отображение мероприятия с заданным id
@app.route('/events/<int:id>')
def event(id):
    db_sess = db_session.create_session()
    # Выберем мероприятие с заданным id из БД
    event = db_sess.query(Events).filter(Events.id == id).first()
    return render_template('event.html', title='Просмотр мероприятия', event=event)


# Добавление мероприятия
@app.route('/events/add', methods=['GET', 'POST'])
def add_event():
    form = EventForm()
    db_sess = db_session.create_session()
    # Обработка метода POST
    if form.validate_on_submit():
        # Сохраним картинку на сервере
        if request.files['event_picture']:
            pic_filename = 'evt_' + str(uuid.uuid1()) + '.pic'
            event_pic = request.files['event_picture']
            event_pic.save(os.path.join(app.config["EVENT_IMAGE_FOLDER"], pic_filename))
        else:
            pic_filename = "default_event.pic"
        # Сформируем объект мероприятия для добавления в БД из данных формы
        event = Events(title=form.title.data,
                       description=form.description.data,
                       event_date_time=form.event_date_time.data,
                       event_picture=pic_filename,
                       poster_id=current_user.id)
        # Очистим поля формы
        form.title.data = ''
        form.description.data = ''
        form.event_date_time.data = ''
        # form.event_picture = ''
        # Сохраним запись в БД
        db_sess.add(event)
        db_sess.commit()

        flash("Новое мероприятие создано успешно")
    # Обработчик метода GET
    return render_template("add_event.html", form=form)


# Редактирование мероприятия c заданным id
@app.route('/events/edit/<int:id>', methods=['GET', 'POST'])
def edit_event(id):
    db_sess = db_session.create_session()
    # Выбираем мероприятие с заданным id из БД
    event = db_sess.query(Events).filter(Events.id == id).first()
    form = EventForm()
    # Обработка метода POST
    if form.validate_on_submit():
        # Заполняем объект мероприятия данными из формы
        event.title = form.title.data
        event.description = form.description.data
        event.event_date_time = form.event_date_time.data
        # Если добавлена картинка, сохраним её на сервере, а имя файла запишем в БД
        if request.files['event_picture']:
            pic_filename = 'evt_' + str(uuid.uuid1()) + '.pic'
            event_pic = request.files['event_picture']
            event_pic.save(os.path.join(app.config["EVENT_IMAGE_FOLDER"], pic_filename))
            event.event_picture = pic_filename
        # Сохраним изменения в БД
        db_sess.add(event)
        db_sess.commit()
        flash("Мероприятие обновлено успешно")
        # Перейдём на страницу просмотра мероприятия
        return redirect(url_for('event', id=event.id))

    # Обработка метода GET
    # Разрешим редактировать только свои мероприятия
    if current_user.id == event.poster_id or current_user.id == 1:
        form.title.data = event.title
        form.description.data = event.description
        form.event_date_time.data = event.event_date_time
        return render_template('edit_event.html', form=form)


# Удаление мероприятия с соответствующим id
@app.route('/events/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_event(id):
    db_sess = db_session.create_session()
    event = db_sess.query(Events).filter(Events.id == id).first()
    # Если id пользователя совпадает с id мероприятия или текущий пользователь - администратор, удаляем мероприятие
    if current_user.id == event.poster_id or current_user.id == 1:
        try:
            db_sess.delete(event)
            db_sess.commit()
            flash("Мероприятие удалено успешно.")
            # Запрос к базе данных для выбора всех записей из таблицы Events и упорядочивания по полю event_date_time
            events = db_sess.query(Events).order_by(Events.event_date_time)
            return render_template('events.html', events=events)
        except:
            # Если возникает проблема при удалении, выведем текст ошибки
            flash("При удалении мероприятия возникла ошибка.")
            events = db_sess.query(Events).order_by(Events.event_date_time)
            return render_template('events.html', events=events)
    else:
        # Если пользователь постарается удалить чужое мероприятие, то выведется ошибка
        flash("Мероприятие создано другим пользователем, удаление невозможно.")
        events = db_sess.query(Events).order_by(Events.event_date_time)
        return render_template('events.html', events=events)


########################################################################################################################
## Функции работы с отзывами
########################################################################################################################
# Определение тональности отзыва при помощи библиотеки Dostoevsky
def get_sentiment_score(message):
    log("testing message: " + message)
    # Здесь создается объект токенизатора RegexTokenizer.
    tokenizer = RegexTokenizer()
    model = FastTextSocialNetworkModel(tokenizer=tokenizer)
    # текст, переданный в функцию как message добавляем в список
    msg_list = list()
    msg_list.append(message)
    results = model.predict(msg_list, k=2)
    log('predicted_result:' + str(results[0]))
    # вызовем функцию sentiment_to_text, чтобы преобразовать полученный результат в удобной для пользователя форме
    translated_result = sentiment_to_text(str(results[0]))
    log('translated_result:' + translated_result)

    return translated_result


def sentiment_to_text(sentiment_str):
    translation = {'positive': 'позитивный',
                   'neutral': 'нейтральный',
                   'negative': 'негативный',
                   'skip': 'неопределенный',
                   'speech': 'другой'}
    sentiment_dict = json.loads(sentiment_str.replace("'", '"'))
    msg = ""
    for key, val in sentiment_dict.items():
        if key in translation:
            ru_key = translation[key]
        else:
            ru_key = key
        val_rnd = round(val, 5)
        val_rnd = round(val * 100, 2)
        msg += f"{str(val_rnd)}% - {ru_key}, "
    msg = msg[:-2]

    return msg


# Обработчик страницы отзывов для мероприятия с заданным id
@app.route('/events/<int:event_id>/feedbacks')
def feedbacks(event_id):
    db_sess = db_session.create_session()
    # Выбираем мероприятия с заданным id из БД
    event = db_sess.query(Events).filter(Events.id == event_id).first()
    # Выбираем отзывы по мероприятию из БД
    feedbacks = db_sess.query(Feedbacks).filter(Feedbacks.event_id == event_id).order_by(Feedbacks.created_date)
    # print("*** event.id =", event.id)
    return render_template('feedbacks.html', event=event, feedbacks=feedbacks)


# Добавление отзыва по мероприятию
@app.route('/events/<int:event_id>/feedbacks/add/', methods=['GET', 'POST'])
def add_feedback(event_id):
    form = FeedbackForm()
    db_sess = db_session.create_session()
    event = db_sess.query(Events).filter(Events.id == event_id).first()
    # Обработка метода POST
    if form.validate_on_submit():
        txt = form.feedback.data
        # txt = txt.replace('<p>', '').replace('</p>', '')
        feedback_score = get_sentiment_score(txt)
        feedback = Feedbacks(feedback=form.feedback.data,
                             user_score=form.user_score.data,
                             sentiment_score=feedback_score,
                             is_anonymous=form.is_anonymous.data,
                             poster_id=current_user.id,
                             event_id=event_id)
        form.feedback.data = ''
        form.user_score.data = ''
        form.is_anonymous.data = False
        db_sess.add(feedback)
        db_sess.commit()

        flash("Отзыв о мероприятии сохранен успешно")
    # Обработка метода GET
    return render_template("add_feedback.html", form=form, event=event)


#
@app.route('/feedbacks/edit/<int:id>', methods=['GET', 'POST'])
def edit_feedback(id):
    # Обработка метода Post
    form = FeedbackForm()
    db_sess = db_session.create_session()
    feedback = db_sess.query(Feedbacks).filter(Feedbacks.id == id).first()
    if form.validate_on_submit():
        feedback.feedback = form.feedback.data
        feedback.user_score = form.user_score.data
        # Вызов функции нейросети для оценки тональности
        feedback_score = get_sentiment_score(form.feedback.data)
        # Обновление оценки тональности текста отзыва
        feedback.sentiment_score = feedback_score
        feedback.is_anonymous = form.is_anonymous.data
        db_sess.add(feedback)
        db_sess.commit()
        flash("Отзыв о мероприятии обновлен успешно")
        # Обработка метода GET
        return redirect(url_for('feedbacks', event_id=feedback.event.id))

    if id == feedback.poster_id or current_user.id == 1:
        form.feedback.data = feedback.feedback
        form.user_score.data = feedback.user_score
        form.is_anonymous.data = feedback.is_anonymous
    else:
        flash("Нельзя редактировать отзывы других пользователей")

    return render_template("edit_feedback.html", form=form, event=feedback.event)


# Удаление отзыва по мероприятию с выбранным id
@app.route('/feedbacks/delete/<int:id>', methods=['GET', 'POST'])
def delete_feedback(id):
    # Обработка метода Post
    db_sess = db_session.create_session()
    feedback = db_sess.query(Feedbacks).filter(Feedbacks.id == id).first()
    event = db_sess.query(Events).filter(Events.id == feedback.event_id).first()
    if current_user.id == feedback.poster_id or current_user.id == 1:
        try:
            db_sess.delete(feedback)
            db_sess.commit()
            flash("Отзыв удален успешно.")
        except:
            flash("При удалении отзыва возникла ошибка.")
    else:
        flash("Нельзя удалять отзывы других пользователей.")
    return redirect(url_for('feedbacks', event_id=event.id))


########################################################################################################################
## Функции работы с пользователями
########################################################################################################################
# Реализация регистрации с помощью формы
@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    # Обработка метода POST
    if form.validate_on_submit():
        if not form.password.data:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Задайте пароль")
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже существует")
        pic_filename = form.email.data.replace("@", "_") + ".pic"
        profile_pic = request.files['profile_picture']
        profile_pic.save(os.path.join(app.config["USER_IMAGE_FOLDER"], pic_filename))
        user = User(
            name=form.name.data,
            email=form.email.data,
            last_name=form.last_name.data,
            fathers_name=form.fathers_name.data,
            occupation=form.occupation.data,
            school_num=form.school_num.data,
            class_num=form.class_num.data,
            city=form.city.data,
            about=form.about.data,
            is_active='Y',
            profile_picture=pic_filename
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    # Обработка метода GET
    return render_template('register.html', title='Регистрация', form=form)


# Редактирование профиля
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = RegisterForm()
    db_sess = db_session.create_session()
    log(f'current_user= {current_user}')
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    #
    if request.method == "GET":
        if user:
            form.email.data = user.email
            form.name.data = user.name
            form.last_name.data = user.last_name
            form.fathers_name.data = user.fathers_name
            form.occupation.data = user.occupation
            form.school_num.data = user.school_num
            form.class_num.data = user.class_num
            form.city.data = user.city
            form.about.data = user.about
            # form.password = "dummy"
            # form.password_again = "dummy"
        else:
            abort(404)
    #
    if form.validate_on_submit():
        if user:
            user.email = form.email.data
            user.name = form.name.data
            user.surname = form.last_name.data
            user.fathers_name = form.fathers_name.data
            user.occupation = form.occupation.data
            user.school_num = form.school_num.data
            user.class_num = form.class_num.data
            user.city = form.city.data
            user.about = form.about.data
            pic_filename = form.email.data.replace("@", "_") + ".pic"
            if request.files['profile_picture']:
                profile_pic = request.files['profile_picture']
                profile_pic.save(os.path.join(app.config["USER_IMAGE_FOLDER"], pic_filename))
            user.profile_picture = pic_filename
            # Сохраняем изменения в таблице БД
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    else:
        # print('validation not succesful')
        log(form.errors)
    return render_template('register.html', title='Редактирование профиля', form=form)


# def edit():
#    return render_template("profile_edit.html", name='edit')

# Сделаем обработчик адреса /login:
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Не забудьте импортировать класс LoginForm и метод login_user из модуля flask-login.
    form = LoginForm()
    # Если форма логина прошла валидацию,
    if form.validate_on_submit():
        # Создаем сессию для работы БД:
        db_sess = db_session.create_session()
        # Находим в БД пользователя по введенной почте:
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        # Проверяем, введен ли для него правильный пароль, если да, вызываем функцию login_user модуля flask-login
        if user and user.check_password(form.password.data):
            #  и передаем туда объект нашего пользователя, а также значение галочки «Запомнить меня»:
            login_user(user, remember=form.remember_me.data)
            # После чего перенаправляем пользователя на главную страницу нашего приложения:
            return redirect("/")
        # Если пароль неправильный:
        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    # Если авторизация не пройдена, то возвращаемся на начало авторизации:
    return render_template('login.html', title='Авторизация', form=form)


########################################################################################################################
## Функции для работы с аналитикой
########################################################################################################################
@app.route('/graphics', methods=['GET', 'POST'])
def graphics():
    # CONNECTION comes from db_session module
    plt.clf()
    df = pd.read_sql_query("SELECT * FROM feedbacks", db_session.CONNECTION)
    y = pd.DataFrame((df["user_score"].value_counts(normalize=True) * 100))
    plt.pie(y['proportion'], autopct='%1.1f%%', labels=y.index)
    plot_file_name = 'feedbacks_pie.png'
    plt.savefig(GRAPHS_FOLDER + plot_file_name)

    form = StatisticsForm()
    # метод POST
    if form.validate_on_submit():
        # Круговая диаграмма
        if form.plot_type.data == "1":
            plt.clf()
            df = pd.read_sql_query("SELECT * FROM feedbacks", db_session.CONNECTION)
            y = pd.DataFrame((df["user_score"].value_counts(normalize=True) * 100))
            plt.pie(y['proportion'], autopct='%1.1f%%', labels=y.index)
            plot_file_name = 'feedbacks_pie.png'
            plt.savefig(GRAPHS_FOLDER + plot_file_name)
        # Гистограмма
        elif form.plot_type.data == "2":
            plt.clf()
            df = pd.read_sql_query("SELECT * FROM feedbacks", db_session.CONNECTION)
            y = pd.DataFrame((df["user_score"]))
            plt.hist(y['user_score'])
            plot_file_name = 'feedbacks_hist.png'
            plt.savefig(GRAPHS_FOLDER + plot_file_name)
        log("form.plot_type.data=" + form.plot_type.data)
        log("plot_file_name=" + plot_file_name)
        return render_template('statistics.html', form=form, plot_file_name=plot_file_name)

    return render_template('statistics.html', form=form, plot_file_name=plot_file_name)


########################################################################################################################
## Other stuff
########################################################################################################################
@app.route('/events/add', methods=['GET', 'POST'])
def add_message():
    form = EventForm()
    db_sess = db_session.create_session()
    # Обработка метода POST
    if form.validate_on_submit():
        # Сформируем объект мероприятия для добавления в БД из данных формы
        event = Events(title=form.title.data,
                       description=form.description.data,
                       event_date_time=form.event_date_time.data,
                       poster_id=current_user.id)
        # Очистим поля формы
        form.title.data = ''
        form.description.data = ''
        form.event_date_time.data = ''
        # form.event_picture = ''
        # Сохраним запись в БД
        db_sess.add(event)
        db_sess.commit()

        flash("Новое письмо отправлено успешно, ожидайте ответа администратора")
    # Обработчик метода GET
    return render_template("add_event.html", form=form)

def log(message, level='INFO'):
    if level == 'INFO':
        app.logger.info(message)
    elif level == 'ERROR':
        app.logger.exception(message)


# Сделаем обработчик адреса /Future_works (страничка с будущими доработками):
@app.route('/text_admin')
def future_works():
    return render_template("text_admin.html", name='future_works')


# Обязательно сделаем обработчик адреса / /sentiment (т.к. это главная страница):
@app.route('/')
@app.route('/sentiment')
def sentiment():
    log("rendering main page")
    db_session.global_init("db/sentiment.db")
    log("Initialized DB")

    #   music_playing = False

    #    if request.method == 'POST':
    #       if 'toggle_music' in request.form:
    #          music_playing = not music_playing

    return render_template("index.html")


@app.route('/toggle_music', methods=['POST'])
def toggle_music():
    global music_on
    music_on = not music_on
    return jsonify({'music_on': music_on})


@app.errorhandler(500)
def server_error(error):
    app.logger.exception('An exception occurred during a request.')
    return 'Internal Server Error', 500


@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)


# Create search function
@app.route('/search', methods=["POST"])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        print('validating in search')
        event.searched = form.searched.data
    return render_template("events.html", form=form, searched=event.searched)


def main():
    try:
        log('Starting main app')
        #db_session.global_init("db/sentiment.db")
        # app.run(port=8080, host='127.0.0.1')
        app.run()
    except Exception as E:
        log('Starting main app failed: ' + str(E), 'ERROR')
        return 'Internal Error Occurred'


if __name__ == '__main__':
    main()
