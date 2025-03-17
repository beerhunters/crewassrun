# from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash
# import aiohttp
# import asyncio
# import logging
# from math import ceil
#
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)
#
# app = Flask(__name__, template_folder="templates", static_folder="static")
# app.secret_key = "your_secret_key_here"
# API_URL = "http://localhost:8000"
# # API_URL = "http://api:8000"  # Оставляем так, так как внутри сети Docker
#
# # Создаем Blueprint с префиксом /crewassrun
# admin_bp = Blueprint("admin", __name__, url_prefix="/crewassrun")
#
#
# async def fetch_data(endpoint):
#     async with aiohttp.ClientSession() as session:
#         async with session.get(f"{API_URL}/{endpoint}") as response:
#             data = await response.json()
#             # logger.debug(f"Данные из API /{endpoint}: {data}")
#             return data
#
#
# async def delete_data(endpoint):
#     async with aiohttp.ClientSession() as session:
#         async with session.delete(f"{API_URL}/{endpoint}") as response:
#             return response.status == 200
#
#
# async def post_data(endpoint, data):
#     async with aiohttp.ClientSession() as session:
#         async with session.post(f"{API_URL}/{endpoint}", json=data) as response:
#             return await response.json()
#
#
# async def put_data(endpoint, data):
#     async with aiohttp.ClientSession() as session:
#         async with session.put(f"{API_URL}/{endpoint}", json=data) as response:
#             return await response.json()
#
#
# def paginate(data, page, per_page):
#     total = len(data)
#     total_pages = ceil(total / per_page)
#     start = (page - 1) * per_page
#     end = start + per_page
#     return data[start:end], total_pages
#
#
# @admin_bp.route("/")
# def index():
#     return render_template("index.html")
#
#
# @admin_bp.route("/users")
# def users():
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     try:
#         users = loop.run_until_complete(fetch_data("users/"))
#         # logger.info(f"Получено пользователей: {len(users)}")
#     except Exception as e:
#         logger.error(f"Ошибка при загрузке данных: {str(e)}")
#         flash("Ошибка при загрузке данных пользователей.", "danger")
#         users = []
#     finally:
#         loop.close()
#
#     page = int(request.args.get("page", 1))
#     per_page = int(request.args.get("per_page", 10))
#     paginated_users, total_pages = paginate(users, page, per_page)
#     return render_template(
#         "users.html",
#         users=paginated_users,
#         page=page,
#         per_page=per_page,
#         total_pages=total_pages,
#     )
#
#
# @admin_bp.route("/buns")
# def buns():
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     try:
#         buns = loop.run_until_complete(fetch_data("buns/"))
#         # logger.info(f"Получено булочек: {len(buns)}")
#     except Exception as e:
#         logger.error(f"Ошибка при загрузке данных: {str(e)}")
#         flash("Ошибка при загрузке данных булочек.", "danger")
#         buns = []
#     finally:
#         loop.close()
#
#     page = int(request.args.get("page", 1))
#     per_page = int(request.args.get("per_page", 10))
#     paginated_buns, total_pages = paginate(buns, page, per_page)
#     return render_template(
#         "buns.html",
#         buns=paginated_buns,
#         page=page,
#         per_page=per_page,
#         total_pages=total_pages,
#     )
#
#
# @admin_bp.route("/results")
# def results():
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     try:
#         users = loop.run_until_complete(fetch_data("users/"))
#         user_buns = loop.run_until_complete(fetch_data("user_buns/"))
#         # logger.info(f"Получено результатов: {len(user_buns)}")
#         user_map = {user["id"]: user["username"] for user in users}
#         for ub in user_buns:
#             ub["username"] = user_map.get(
#                 ub["user_id"], f"Неизвестный (ID: {ub['user_id']})"
#             )
#     except Exception as e:
#         logger.error(f"Ошибка при загрузке данных: {str(e)}")
#         flash("Ошибка при загрузке данных результатов.", "danger")
#         user_buns = []
#     finally:
#         loop.close()
#
#     page = int(request.args.get("page", 1))
#     per_page = int(request.args.get("per_page", 10))
#     paginated_user_buns, total_pages = paginate(user_buns, page, per_page)
#     return render_template(
#         "results.html",
#         user_buns=paginated_user_buns,
#         page=page,
#         per_page=per_page,
#         total_pages=total_pages,
#     )
#
#
# @admin_bp.route("/delete_user/<int:telegram_id>/<chat_id>")
# def delete_user(telegram_id, chat_id):
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     try:
#         success = loop.run_until_complete(delete_data(f"users/{telegram_id}/{chat_id}"))
#         if success:
#             flash(f"Пользователь {telegram_id} удален из чата {chat_id}.", "success")
#         else:
#             flash("Ошибка при удалении пользователя.", "danger")
#     except Exception as e:
#         logger.error(f"Ошибка: {str(e)}")
#         flash(f"Ошибка: {str(e)}", "danger")
#     finally:
#         loop.close()
#     return redirect(url_for("admin.users"))
#
#
# @admin_bp.route("/add_bun", methods=["POST"])
# def add_bun():
#     name = request.form["name"]
#     points = int(request.form["points"])
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     try:
#         loop.run_until_complete(post_data("buns/", {"name": name, "points": points}))
#         flash(f"Булочка '{name}' добавлена.", "success")
#     except Exception as e:
#         logger.error(f"Ошибка: {str(e)}")
#         flash(f"Ошибка при добавлении булочки: {str(e)}", "danger")
#     finally:
#         loop.close()
#     return redirect(url_for("admin.buns"))
#
#
# @admin_bp.route("/edit_bun/<name>", methods=["POST"])
# def edit_bun(name):
#     points = int(request.form["points"])
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     try:
#         loop.run_until_complete(
#             put_data(f"buns/{name}", {"name": name, "points": points})
#         )
#         flash(f"Булочка '{name}' обновлена.", "success")
#     except Exception as e:
#         logger.error(f"Ошибка: {str(e)}")
#         flash(f"Ошибка при обновлении: {str(e)}", "danger")
#     finally:
#         loop.close()
#     return redirect(url_for("admin.buns"))
#
#
# @admin_bp.route("/delete_bun/<name>")
# def delete_bun(name):
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     try:
#         success = loop.run_until_complete(delete_data(f"buns/{name}"))
#         if success:
#             flash(f"Булочка '{name}' удалена.", "success")
#         else:
#             flash("Ошибка при удалении булочки.", "danger")
#     except Exception as e:
#         logger.error(f"Ошибка: {str(e)}")
#         flash(f"Ошибка: {str(e)}", "danger")
#     finally:
#         loop.close()
#     return redirect(url_for("admin.buns"))
#
#
# @admin_bp.route("/edit_user_bun/<int:id>", methods=["POST"])
# def edit_user_bun(id):
#     count = int(request.form["count"])
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     try:
#         user_buns = loop.run_until_complete(fetch_data("user_buns/"))
#         buns = loop.run_until_complete(fetch_data("buns/"))
#         bun_map = {bun["name"]: bun["points"] for bun in buns}
#         for ub in user_buns:
#             if ub["id"] == id:
#                 bun_points = bun_map.get(ub["bun"], 0)
#                 updated_points = count * bun_points
#                 updated_data = {
#                     "id": ub["id"],
#                     "user_id": ub["user_id"],
#                     "bun": ub["bun"],
#                     "chat_id": ub["chat_id"],
#                     "count": count,
#                     "points": updated_points,
#                 }
#                 loop.run_until_complete(put_data(f"user_buns/{id}", updated_data))
#                 flash(
#                     f"Результат с ID {id} обновлен. Новые очки: {updated_points}",
#                     "success",
#                 )
#                 break
#     except Exception as e:
#         logger.error(f"Ошибка: {str(e)}")
#         flash(f"Ошибка при обновлении: {str(e)}", "danger")
#     finally:
#         loop.close()
#     return redirect(url_for("admin.results"))
#
#
# @admin_bp.route("/delete_user_bun/<int:id>")
# def delete_user_bun(id):
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     try:
#         success = loop.run_until_complete(delete_data(f"user_buns/{id}"))
#         if success:
#             flash(f"Результат с ID {id} удален.", "success")
#         else:
#             flash("Ошибка при удалении результата.", "danger")
#     except Exception as e:
#         logger.error(f"Ошибка: {str(e)}")
#         flash(f"Ошибка: {str(e)}", "danger")
#     finally:
#         loop.close()
#     return redirect(url_for("admin.results"))
#
#
# # Регистрируем Blueprint в приложении
# app.register_blueprint(admin_bp)
#
# if __name__ == "__main__":
#     logger.info("Запуск Flask приложения")
#     app.run(debug=True, port=5000)
#     # app.run(host="0.0.0.0", port=5000, debug=False)
from flask import (
    Flask,
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from flask_bcrypt import Bcrypt
import aiohttp
import asyncio
import logging
from math import ceil

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "your_secret_key_here"  # Замените на безопасный ключ
API_URL = "http://localhost:8000"
# API_URL = "http://api:8000"  # Оставляем так, так как внутри сети Docker

# Инициализация Flask-Login и Bcrypt
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # Маршрут для страницы логина
bcrypt = Bcrypt(app)


# Простая модель пользователя (в будущем можно заменить на БД)
class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


# Фиктивный пользователь (замените на свои данные)
admin_users = {
    "admin": User(
        id=1,
        username="admin",
        password_hash=bcrypt.generate_password_hash("admin123").decode("utf-8"),
    )
}


@login_manager.user_loader
def load_user(user_id):
    return admin_users.get("admin") if user_id == "1" else None


# Blueprint для админки
admin_bp = Blueprint("admin", __name__, url_prefix="/crewassrun")


async def fetch_data(endpoint):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/{endpoint}") as response:
            data = await response.json()
            # logger.debug(f"Данные из API /{endpoint}: {data}")
            return data


async def delete_data(endpoint):
    async with aiohttp.ClientSession() as session:
        async with session.delete(f"{API_URL}/{endpoint}") as response:
            return response.status == 200


async def post_data(endpoint, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{API_URL}/{endpoint}", json=data) as response:
            return await response.json()


async def put_data(endpoint, data):
    async with aiohttp.ClientSession() as session:
        async with session.put(f"{API_URL}/{endpoint}", json=data) as response:
            return await response.json()


def paginate(data, page, per_page):
    total = len(data)
    total_pages = ceil(total / per_page)
    start = (page - 1) * per_page
    end = start + per_page
    return data[start:end], total_pages


# Маршрут логина (вне Blueprint, чтобы был на /login)
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.index"))
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = admin_users.get(username)
        if user and user.check_password(password):
            login_user(user)
            flash("Вы успешно вошли!", "success")
            return redirect(url_for("admin.index"))
        else:
            flash("Неверный логин или пароль.", "danger")
    return render_template("login.html")


# Маршрут логаута
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из системы.", "success")
    return redirect(url_for("login"))


@admin_bp.route("/")
@login_required
def index():
    return render_template("index.html")


@admin_bp.route("/users")
@login_required
def users():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        users_data = loop.run_until_complete(fetch_data("users/"))
        # logger.info(f"Получено пользователей: {len(users_data)}")
    except Exception as e:
        logger.error(f"Ошибка при загрузке данных: {str(e)}")
        flash("Ошибка при загрузке данных пользователей.", "danger")
        users_data = []
    finally:
        loop.close()

    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    paginated_users, total_pages = paginate(users_data, page, per_page)
    return render_template(
        "users.html",
        users=paginated_users,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@admin_bp.route("/buns")
@login_required
def buns():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        buns = loop.run_until_complete(fetch_data("buns/"))
        # logger.info(f"Получено булочек: {len(buns)}")
    except Exception as e:
        logger.error(f"Ошибка при загрузке данных: {str(e)}")
        flash("Ошибка при загрузке данных булочек.", "danger")
        buns = []
    finally:
        loop.close()

    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    paginated_buns, total_pages = paginate(buns, page, per_page)
    return render_template(
        "buns.html",
        buns=paginated_buns,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@admin_bp.route("/results")
@login_required
def results():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        users_data = loop.run_until_complete(fetch_data("users/"))
        user_buns = loop.run_until_complete(fetch_data("user_buns/"))
        # logger.info(f"Получено результатов: {len(user_buns)}")
        user_map = {user["id"]: user["username"] for user in users_data}
        for ub in user_buns:
            ub["username"] = user_map.get(
                ub["user_id"], f"Неизвестный (ID: {ub['user_id']})"
            )
    except Exception as e:
        logger.error(f"Ошибка при загрузке данных: {str(e)}")
        flash("Ошибка при загрузке данных результатов.", "danger")
        user_buns = []
    finally:
        loop.close()

    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    paginated_user_buns, total_pages = paginate(user_buns, page, per_page)
    return render_template(
        "results.html",
        user_buns=paginated_user_buns,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@admin_bp.route("/delete_user/<int:telegram_id>/<chat_id>")
@login_required
def delete_user(telegram_id, chat_id):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        success = loop.run_until_complete(delete_data(f"users/{telegram_id}/{chat_id}"))
        if success:
            flash(f"Пользователь {telegram_id} удален из чата {chat_id}.", "success")
        else:
            flash("Ошибка при удалении пользователя.", "danger")
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        flash(f"Ошибка: {str(e)}", "danger")
    finally:
        loop.close()
    return redirect(url_for("admin.users"))


@admin_bp.route("/add_bun", methods=["POST"])
@login_required
def add_bun():
    name = request.form["name"]
    points = int(request.form["points"])
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(post_data("buns/", {"name": name, "points": points}))
        flash(f"Булочка '{name}' добавлена.", "success")
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        flash(f"Ошибка при добавлении булочки: {str(e)}", "danger")
    finally:
        loop.close()
    return redirect(url_for("admin.buns"))


@admin_bp.route("/edit_bun/<name>", methods=["POST"])
@login_required
def edit_bun(name):
    points = int(request.form["points"])
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(
            put_data(f"buns/{name}", {"name": name, "points": points})
        )
        flash(f"Булочка '{name}' обновлена.", "success")
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        flash(f"Ошибка при обновлении: {str(e)}", "danger")
    finally:
        loop.close()
    return redirect(url_for("admin.buns"))


@admin_bp.route("/delete_bun/<name>")
@login_required
def delete_bun(name):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        success = loop.run_until_complete(delete_data(f"buns/{name}"))
        if success:
            flash(f"Булочка '{name}' удалена.", "success")
        else:
            flash("Ошибка при удалении булочки.", "danger")
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        flash(f"Ошибка: {str(e)}", "danger")
    finally:
        loop.close()
    return redirect(url_for("admin.buns"))


@admin_bp.route("/edit_user_bun/<int:id>", methods=["POST"])
@login_required
def edit_user_bun(id):
    count = int(request.form["count"])
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        user_buns = loop.run_until_complete(fetch_data("user_buns/"))
        buns = loop.run_until_complete(fetch_data("buns/"))
        bun_map = {bun["name"]: bun["points"] for bun in buns}
        for ub in user_buns:
            if ub["id"] == id:
                bun_points = bun_map.get(ub["bun"], 0)
                updated_points = count * bun_points
                updated_data = {
                    "id": ub["id"],
                    "user_id": ub["user_id"],
                    "bun": ub["bun"],
                    "chat_id": ub["chat_id"],
                    "count": count,
                    "points": updated_points,
                }
                loop.run_until_complete(put_data(f"user_buns/{id}", updated_data))
                flash(
                    f"Результат с ID {id} обновлен. Новые очки: {updated_points}",
                    "success",
                )
                break
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        flash(f"Ошибка при обновлении: {str(e)}", "danger")
    finally:
        loop.close()
    return redirect(url_for("admin.results"))


@admin_bp.route("/delete_user_bun/<int:id>")
@login_required
def delete_user_bun(id):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        success = loop.run_until_complete(delete_data(f"user_buns/{id}"))
        if success:
            flash(f"Результат с ID {id} удален.", "success")
        else:
            flash("Ошибка при удалении результата.", "danger")
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        flash(f"Ошибка: {str(e)}", "danger")
    finally:
        loop.close()
    return redirect(url_for("admin.results"))


# Регистрируем Blueprint
app.register_blueprint(admin_bp)

if __name__ == "__main__":
    logger.info("Запуск Flask приложения")
    app.run(debug=True, port=5000)
    # app.run(debug=True, host="0.0.0.0", port=5000)
