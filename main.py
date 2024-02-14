from flask import Flask, url_for, render_template, redirect, request, abort, flash
# Импортируем нужные классы:
from flask_login import LoginManager
from flask_login import login_user
from flask_login import login_required
from flask_login import logout_user
from flask_login import current_user
from flask_ckeditor import CKEditor
from forms.event import EventForm
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

app = Flask(__name__)
ckeditor = CKEditor(app)

tokenizer = RegexTokenizer()
model = FastTextSocialNetworkModel(tokenizer=tokenizer)

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
@app.route('/events')
def events():
    db_sess = db_session.create_session()
    # Выберем все мероприятия из БД
    events = db_sess.query(Events).order_by(Events.event_date_time)
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
            pic_filename = 'evt_'+str(uuid.uuid1())+'.pic'
            event_pic = request.files['event_picture']
            event_pic.save(os.path.join(app.config["EVENT_IMAGE_FOLDER"], pic_filename))
        # Сформируем объект мероприятия для добавления в БД из данных формы
        event = Events(title = form.title.data,
                       description = form.description.data,
                       event_date_time = form.event_date_time.data,
                       event_picture = pic_filename,
                       poster_id = current_user.id)
        # Очистим поля формы
        form.title.data = ''
        form.description.data = ''
        form.event_date_time.data = ''
        #form.event_picture = ''
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
            pic_filename = 'evt_'+str(uuid.uuid1())+'.pic'
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
            #? Grab all the posts from the database
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
    results = model.predict(message, k=2)
    #results="1"
    print("testing message: ", message)
    print("Model predicted results: ", results)
    return str(results)


# Обработчик страницы отзывов для мероприятия с заданным id
@app.route('/events/<int:event_id>/feedbacks')
def feedbacks(event_id):
    db_sess = db_session.create_session()
    # Выбираем мероприятия с заданным id из БД
    event = db_sess.query(Events).filter(Events.id == event_id).first()
    # Выбираем отзывы по мероприятию из БД
    feedbacks = db_sess.query(Feedbacks).filter(Feedbacks.event_id == event_id).order_by(Feedbacks.created_date)
    print("*** event.id =", event.id)
    return render_template('feedbacks.html', event=event, feedbacks = feedbacks)


# Добавление отзыва по мероприятию
@app.route('/events/<int:event_id>/feedbacks/add/', methods=['GET', 'POST'])
def add_feedback(event_id):
    form = FeedbackForm()
    db_sess = db_session.create_session()
    event = db_sess.query(Events).filter(Events.id == event_id).first()
    # Обработка метода POST
    if form.validate_on_submit():
        txt = form.feedback.data
        txt = txt.replace('<p>', '').replace('</p>', '')
        feedback_score = get_sentiment_score(txt)
        print('creating feedback. sentiment_score is', feedback_score)
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
        feedback.user_score=form.user_score.data
        feedback_score = get_sentiment_score(form.feedback.data)

        print(f'feedback_score_edit_feedback: {feedback_score}')
        feedback.sentiment_score=feedback_score
        feedback.is_anonymous=form.is_anonymous.data
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
    if id == feedback.poster_id or current_user.id == 1:
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
        pic_filename = form.email.data.replace("@","_") + ".pic"
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
    print(f'current_user= {current_user}')
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
            #form.password = "dummy"
            #form.password_again = "dummy"
        else:
            abort(404)
    #
    if form.validate_on_submit():
        print('validated profile edit form')
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
        print('validation not succesful')
        print(form.errors)
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
    df = pd.read_sql_query("SELECT * FROM feedbacks", db_session.CONNECTION)
    y = pd.DataFrame((df["user_score"].value_counts(normalize=True) * 100))
    plt.pie(y['proportion'], autopct='%1.1f%%', labels=y.index)
    plot_file_name = 'feedbacks_pie.png'
    plt.savefig(GRAPHS_FOLDER+plot_file_name)

    form = StatisticsForm()
    # post
    if form.validate_on_submit():
        # Pie chart
        if form.plot_type.data == "1":
            plt.clf()
            df = pd.read_sql_query("SELECT * FROM feedbacks", db_session.CONNECTION)
            y = pd.DataFrame((df["user_score"].value_counts(normalize=True) * 100))
            plt.pie(y['proportion'], autopct='%1.1f%%', labels=y.index)
            plot_file_name = 'feedbacks_pie.png'
            plt.savefig(GRAPHS_FOLDER + plot_file_name)
        # hist
        elif form.plot_type.data == "2":
            plt.clf()
            df = pd.read_sql_query("SELECT * FROM feedbacks", db_session.CONNECTION)
            y = pd.DataFrame((df["user_score"]))
            plt.hist(y['user_score'])
            plot_file_name = 'feedbacks_hist.png'
            plt.savefig(GRAPHS_FOLDER + plot_file_name)
        print("form.plot_type.data=", form.plot_type.data)
        print("plot_file_name=", plot_file_name)
        return render_template('statistics.html', form=form, plot_file_name=plot_file_name)
    print("statistincs.get")

    return render_template('statistics.html', form=form, plot_file_name=plot_file_name)




########################################################################################################################
## Other stuff
########################################################################################################################



@app.route('/upcoming_events')
def subjects():
    return render_template("upcoming_events.html", name='subjects')

@app.route('/text_admin')
def future_works():
    return render_template("text_admin.html", name='future_works')

@app.route('/my_events')
def about_me():
    return render_template("my_events.html", name='about_me')

@app.route('/statistics')
def definitions():
    return render_template("dashboard.html", name='definitions')

@app.route('/past_events')
def contur_maps():
    return render_template("past_events.html", name='contur_maps')


# Обязательно сделаем обработчик адреса / /sentiment (т.к. это главная страница):
@app.route('/')
@app.route('/sentiment')
def sentiment():
    return render_template("index.html")

#@app.route('/dashboard')
#def dashboard():
#    return render_template('dashboard.html')
def main():
    db_session.global_init("db/sentiment.db")
    app.run(port=8080, host='127.0.0.1')

# def home():
#    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#    return render_template('clock.html', current_time=current_time)

if __name__ == '__main__':
    main()
