# admin/app.py
from flask import Flask, render_template, request, redirect, url_for, flash
import aiohttp
import asyncio
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "your_secret_key_here"
API_URL = "http://localhost:8000"


async def fetch_data(endpoint):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/{endpoint}") as response:
            data = await response.json()
            # logger.debug(f"Данные из API /{endpoint}: {data}")
            return data


async def delete_data(endpoint):
    async with aiohttp.ClientSession() as session:
        async with session.delete(f"{API_URL}/{endpoint}") as response:
            if response.status == 200:
                # logger.info(f"Удаление /{endpoint} выполнено успешно")
                return True
            else:
                logger.error(
                    f"Ошибка удаления /{endpoint}: {response.status} - {await response.text()}"
                )
                return False


async def post_data(endpoint, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{API_URL}/{endpoint}", json=data) as response:
            result = await response.json()
            # logger.info(f"Добавление /{endpoint}: {result}")
            return result


async def put_data(endpoint, data):
    async with aiohttp.ClientSession() as session:
        async with session.put(f"{API_URL}/{endpoint}", json=data) as response:
            result = await response.json()
            # logger.info(f"Обновление /{endpoint}: {result}")
            return result


@app.route("/")
def index():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        users = loop.run_until_complete(fetch_data("users/"))
        buns = loop.run_until_complete(fetch_data("buns/"))
        user_buns = loop.run_until_complete(fetch_data("user_buns/"))
        # logger.info(
        #     f"Получено пользователей: {len(users)}, булочек: {len(buns)}, результатов: {len(user_buns)}"
        # )
        user_map = {user["id"]: user["username"] for user in users}
        for ub in user_buns:
            ub["username"] = user_map.get(
                ub["user_id"], f"Unknown (ID: {ub['user_id']})"
            )
    except Exception as e:
        logger.error(f"Ошибка при загрузке данных: {str(e)}")
        flash("Ошибка при загрузке данных. Проверьте логи.", "danger")
        users, buns, user_buns = [], [], []
    finally:
        loop.close()
    # Получаем параметр tab из запроса, по умолчанию "users"
    active_tab = request.args.get("tab", "users")
    return render_template(
        "index.html", users=users, buns=buns, user_buns=user_buns, active_tab=active_tab
    )


@app.route("/delete_user/<int:telegram_id>/<chat_id>")
def delete_user(telegram_id, chat_id):
    # logger.debug(
    #     f"Маршрут delete_user вызван для telegram_id={telegram_id}, chat_id={chat_id}"
    # )
    try:
        chat_id_int = int(chat_id)
    except ValueError:
        logger.error(f"Некорректный chat_id: {chat_id}")
        flash("Некорректный chat_id", "danger")
        return redirect(url_for("index"))
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        endpoint = f"users/{telegram_id}/{chat_id_int}"
        # logger.debug(f"Попытка удаления пользователя: {endpoint}")
        success = loop.run_until_complete(delete_data(endpoint))
        if success:
            flash(
                f"Пользователь {telegram_id} успешно удален из чата {chat_id_int}",
                "success",
            )
        else:
            flash(
                f"Не удалось удалить пользователя {telegram_id} из чата {chat_id_int}. Возможно, он не существует.",
                "danger",
            )
    except Exception as e:
        logger.error(
            f"Исключение при удалении пользователя {telegram_id}/{chat_id}: {str(e)}"
        )
        flash(f"Ошибка при удалении пользователя: {str(e)}", "danger")
    finally:
        loop.close()
    return redirect(url_for("index"))


@app.route("/add_bun", methods=["POST"])
def add_bun():
    name = request.form["name"]
    points = int(request.form["points"])
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(post_data("buns/", {"name": name, "points": points}))
        flash(f"Булочка '{name}' успешно добавлена", "success")
    except Exception as e:
        logger.error(f"Ошибка при добавлении булочки: {str(e)}")
        flash(f"Ошибка при добавлении булочки: {str(e)}", "danger")
    finally:
        loop.close()
    return redirect(url_for("index", tab="buns"))


@app.route("/edit_bun/<name>", methods=["POST"])
def edit_bun(name):
    points = int(request.form["points"])
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(
            put_data(f"buns/{name}", {"name": name, "points": points})
        )
        flash(f"Булочка '{name}' успешно обновлена", "success")
    except Exception as e:
        logger.error(f"Ошибка при обновлении булочки: {str(e)}")
        flash(f"Ошибка при обновлении булочки: {str(e)}", "danger")
    finally:
        loop.close()
    return redirect(url_for("index", tab="buns"))


@app.route("/delete_bun/<name>")
def delete_bun(name):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        success = loop.run_until_complete(delete_data(f"buns/{name}"))
        if success:
            flash(f"Булочка '{name}' успешно удалена", "success")
        else:
            flash(
                f"Не удалось удалить булочку '{name}'. Возможно, она не существует.",
                "danger",
            )
    except Exception as e:
        logger.error(f"Ошибка при удалении булочки: {str(e)}")
        flash(f"Ошибка при удалении булочки: {str(e)}", "danger")
    finally:
        loop.close()
    return redirect(url_for("index", tab="buns"))


@app.route("/edit_user_bun/<int:id>", methods=["POST"])
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
                    f"Результат с ID {id} успешно обновлен. Новые очки: {updated_points}",
                    "success",
                )
                break
    except Exception as e:
        logger.error(f"Ошибка при обновлении результата: {str(e)}")
        flash(f"Ошибка при обновлении результата: {str(e)}", "danger")
    finally:
        loop.close()
    return redirect(url_for("index", tab="results"))


@app.route("/delete_user_bun/<int:id>")
def delete_user_bun(id):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        success = loop.run_until_complete(delete_data(f"user_buns/{id}"))
        if success:
            flash(f"Результат с ID {id} успешно удален", "success")
        else:
            flash(
                f"Не удалось удалить результат с ID {id}. Возможно, он не существует.",
                "danger",
            )
    except Exception as e:
        logger.error(f"Ошибка при удалении результата: {str(e)}")
        flash(f"Ошибка при удалении результата: {str(e)}", "danger")
    finally:
        loop.close()
    # Перенаправляем на главную страницу с параметром tab=results
    return redirect(url_for("index", tab="results"))


if __name__ == "__main__":
    logger.info("Запуск Flask приложения")
    # logger.info(f"Зарегистрированные маршруты: {app.url_map}")
    app.run(debug=True, port=5000)
