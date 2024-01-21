from flask import Flask, url_for, render_template, redirect, request, abort
# 255 248 220 rgb
# Выполним первоначальную настройку модуля. Сначала импортируем нужный класс:
from flask_login import LoginManager
from flask_login import login_user
from flask_login import login_required
from flask_login import logout_user
from flask_login import current_user
#from forms.diagram import Event
from forms.events import EventsForm
from forms.user import RegisterForm, LoginForm
from data.events import Events
from data.users import User
from data import db_session

app = Flask(__name__)

# Затем сразу после создания приложения flask инициализируем LoginManager:
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'myschoolproject_secret_key'


# Для верной работы flask-login у нас должна быть
# функция load_user для получения пользователя
# украшенная декоратором login_manager.user_loader. Добавим ее:
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


# Кроме того, наша модель для пользователей
# должна содержать ряд методов
# для корректной работы flask-login,
# но мы не будем создавать их руками,
# а воспользуемся множественным наследованием.
# см. файл: \data\users.py

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/events', methods=['GET', 'POST'])
@login_required
def add_events():
    form = EventsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        events = Events()
        events.title = form.title.data
        events.content = form.content.data
        events.is_private = form.is_private.data
        current_user.events.append(events)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/events')
    return render_template('events.html', title='Добавление новости', form=form)


@app.route('/events_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def events_delete(id):
    db_sess = db_session.create_session()
    events = db_sess.query(Events).filter(Events.id == id, Events.user == current_user).first()
    if events:
        db_sess.delete(events)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/events')


@app.route('/events/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_events(id):
    form = EventsForm()
    db_sess = db_session.create_session()
    events = db_sess.query(Events).filter(Events.id == id, Events.user == current_user).first()
    if request.method == "GET":
        if events:
            form.title.data = events.title
            form.content.data = events.content
            form.is_private.data = events.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        if events:
            events.title = form.title.data
            events.content = form.content.data
            events.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/events')
        else:
            abort(404)
    return render_template('events.html', title='Редактирование заметки', form=form)



@app.route("/events")
def events():
    db_sess = db_session.create_session()
    #if current_user.is_authenticated:
    print(current_user)
    events = db_sess.query(Events).filter((Events.user == current_user) | (Events.is_private != True))
    #else:
    #   events = db_sess.query(Events).filter(Events.is_private != True)
    return render_template("notes.html", events=events)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    print('before validate')
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        print('creating db session')
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        print('will now create a user')
        user = User(
            name=form.name.data,
            email=form.email.data,
            fathers_name=form.fathers_name.data,
            #status=form.status.data,
            school_num=form.school_num.data,
            class_num=form.class_num.data,
            city=form.city.data,
            about=form.about.data,
            #hashed_password=form.hashed_password.data,
            #created_date=form.created_date.data,
            #active=form.active.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    #
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/profile', methods=['GET', 'POST'])
def edit_profile():
    form = RegisterForm()
    db_sess = db_session.create_session()
    print(f'current_user= {current_user}')
    users = db_sess.query(User).filter(User.id == current_user.id).first()
    if request.method == "GET":
        if users:
            form.name.data = users.name
            form.last_name.data = users.surname
            form.fathers_name.data = users.fathers_name
        else:
            abort(404)
    if form.validate_on_submit():
        print('validation')
        if users:
            users.name = form.name.data
            users.surname = form.last_name.data
            users.fathers_name = form.fathers_name.data
            db_sess.commit()
            return redirect('/profile')
        else:
            abort(404)
    else:
        print('validation not succesful')
    return render_template('profile_edit.html', title='Редактирование профиля', form=form)
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


# Сделаем обработчик адреса /Subjects:
@app.route('/upcoming_events')
def subjects():
    return render_template("upcoming_events.html", name='subjects')

# Сделаем обработчик адреса /Future_works (страничка с будущими доработками):
@app.route('/text_admin')
def future_works():
    return render_template("text_admin.html", name='future_works')

# Также сделаем обработчик адреса /About_me (страничка о себе):
@app.route('/my_events')
def about_me():
    return render_template("my_events.html", name='about_me')

# Также сделаем обработчик адреса /About_me (страничка о себе):
@app.route('/statistics')
def definitions():
    return render_template("dashboard.html", name='definitions')

# Также сделаем обработчик адреса /Contur_maps (страничка с контурными картами):
@app.route('/past_events')
def contur_maps():
    return render_template("past_events.html", name='contur_maps')

# Обязательно сделаем обработчик адреса / /sentinel (т.к. это главная страница):
@app.route('/')
@app.route('/sentinel')
def Sentinel():
    return render_template("index.html")

#@app.route('/dashboard')
#def dashboard():
#    return render_template('dashboard.html')
def main():
    db_session.global_init("db/blogs.db")
    app.run(port=8080, host='127.0.0.1')

# def home():
#    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#    return render_template('clock.html', current_time=current_time)

if __name__ == '__main__':
    main()
