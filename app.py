from flask import (
    Flask,
    render_template,
    url_for,
    request,
    flash,
    session,
    redirect,
    abort,
    g,
    make_response,
)
import sqlite3
import os
from FDataBase import FDataBase

# конфигурация

DATABASE = "/tmp/blog.db"
DEBUG = True
SECRET_KEY = "thisisasecretkey"

app = Flask(__name__)
# app.config["SECRET_KEY"] = "yandexlyceum_secret_key"
app.config.from_object(
    __name__
)  # Загрузка конфигурации из этого модуля

app.config.update(
    dict(DATABASE=os.path.join(app.root_path, "blog.db"))
)  # Переопределяем путь к базе данных


def connect_db():
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    """Создание таблиц в базе данных"""
    db = connect_db()
    with app.open_resource("sq_db.sql", mode="r") as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    """Соединение с БД, если оно еще не установлено"""
    if not hasattr(g, "link_db"):
        g.link_db = connect_db()
    return g.link_db


menu = [
    {"title": "Установка", "url": "/install-flask"},
    {"title": "Первое приложение", "url": "/first-app"},
    {"title": "Обратная связь", "url": "/contact"},
]


# menu = ["Установка", "Первое приложение", "Обратная связь"]


# @app.route("/index")
@app.route("/")
def index():
    db = get_db()
    dbase = FDataBase(db)
    return render_template(
        "index.html",
        menu=dbase.getMenu(),
        posts=dbase.getPostsAnonce(),
    )
    # print(url_for("index"))
    # return render_template("index.html", menu=menu)


# Вывод неотформатированного кода страницы
@app.route("/make_response_sample")
def index2():
    content = render_template("index.html", menu=menu, posts=[])
    res = make_response(content)
    res.headers["Content-Type"] = "text/plain"
    res.headers["Server"] = "flasksite"
    return res


# Вывод изображения
@app.route("/make_response_sample_2")
def index3():
    img = None
    with app.open_resource(
        app.root_path + "/static/images/ava.png", mode="rb"
    ) as f:
        img = f.read()

    if img is None:
        return "None image"
    res = make_response(img)
    res.headers["Content-Type"] = "image/png"
    return res


@app.route("/add_post", methods=["POST", "GET"])
def addPost():
    db = get_db()
    dbase = FDataBase(db)
    if request.method == "POST":
        if (
            len(request.form["name"]) > 4
            and len(request.form["post"]) > 10
        ):
            res = dbase.addPost(
                request.form["name"],
                request.form["post"],
                request.form["url"],
            )
            if not res:
                flash("Ошибка добавления поста", category="error")
            else:
                flash("Пост добавлен", category="success")
        else:
            flash("Ошибка добавления поста", category="error")
    return render_template(
        "add_post.html",
        menu=dbase.getMenu(),
        title="Добавление поста",
    )


# Отображение поста
# @app.route("/post/<int:id_post>")
@app.route("/post/<alias>")
def showPost(alias):
    db = get_db()
    dbase = FDataBase(db)
    title, post = dbase.getPost(alias)
    if not title:
        abort(404)
    return render_template(
        "post.html", menu=dbase.getMenu(), title=title, post=post
    )


# Закрытие соединения с БД
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, "link_db"):
        g.link_db.close()


@app.route("/about")
def about():
    print(url_for("about"))
    return render_template("about.html", title="О сайте", menu=menu)


@app.route("/contact", methods=["POST", "GET"])
def contact():
    if request.method == "POST":
        if len(request.form["username"]) > 2:
            flash("Сообщение отправлено", category="success")
        else:
            flash("Ошибка отправки", category="error")
        # print(request.form)
        print(request.form["username"])
        # print(request.form["email"])
        # print(request.form["message"])
    # print(url_for("contact"))
    return render_template(
        "contact.html", title="Обратная связь", menu=menu
    )


@app.route("/profile/<username>")
def profile(username):
    if (
        "userLogged" not in session
        or session["userLogged"] != username
    ):
        abort(401)

    return f"Пользователь: {username}"

    # Тестовый контекст запроса


# with app.test_request_context():
#     print(url_for("index"))
#     print(url_for("about"))
#     print(url_for("profile", username="admin"))


# Обработчик перенаправления перехода на главную при авторизации


@app.route("/login", methods=["POST", "GET"])
def login():
    if "userLogged" in session:
        return redirect(
            url_for("profile", username=session["userLogged"])
        )
    elif (
        request.method == "POST"
        and request.form["username"] == "admin"
        and request.form["psw"] == "admin"
    ):
        session["userLogged"] = request.form["username"]
        return redirect(
            url_for("profile", username=session["userLogged"])
        )
    return render_template(
        "login.html", title="Авторизация", menu=menu
    )


# Отлавливание ошибок


@app.errorhandler(404)
def page_not_found(error):
    return (
        render_template(
            "page404.html", title="Страница не найдена", menu=menu
        ),
        404,
    )


@app.route("/transfer")
def transfer():
    return redirect(url_for("index"), 301)


# Не работает. Разобраться. Нет метода в библиотеке.
# @app.before_first_request
# def before_first_request():
#     print("before_first_request() called")


@app.before_request
def before_request():
    print("before_request() called")


@app.after_request
def after_request(response):
    print("after_request() called")
    return response


@app.teardown_request
def teardown_request(response):
    print("teardown_request() called")
    return response


if __name__ == "__main__":
    app.run(debug=True)
