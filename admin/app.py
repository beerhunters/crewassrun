from flask import Flask, render_template, request, redirect, url_for, flash
import aiohttp
import asyncio
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "your_secret_key_here"
# API_URL = "http://localhost:8000"
API_URL = "http://api:8000"  # Оставляем так, так как внутри сети Docker


async def fetch_data(endpoint):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/{endpoint}") as response:
            data = await response.json()
            logger.debug(f"Данные из API /{endpoint}: {data}")
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


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/users")
def users():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        users = loop.run_until_complete(fetch_data("users/"))
        logger.info(f"Получено пользователей: {len(users)}")
    except Exception as e:
        logger.error(f"Ошибка при загрузке данных: {str(e)}")
        flash("Ошибка при загрузке данных пользователей.", "danger")
        users = []
    finally:
        loop.close()
    return render_template("users.html", users=users)


@app.route("/buns")
def buns():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        buns = loop.run_until_complete(fetch_data("buns/"))
        logger.info(f"Получено булочек: {len(buns)}")
    except Exception as e:
        logger.error(f"Ошибка при загрузке данных: {str(e)}")
        flash("Ошибка при загрузке данных булочек.", "danger")
        buns = []
    finally:
        loop.close()
    return render_template("buns.html", buns=buns)


@app.route("/results")
def results():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        users = loop.run_until_complete(fetch_data("users/"))
        user_buns = loop.run_until_complete(fetch_data("user_buns/"))
        logger.info(f"Получено результатов: {len(user_buns)}")
        user_map = {user["id"]: user["username"] for user in users}
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
    return render_template("results.html", user_buns=user_buns)


@app.route("/delete_user/<int:telegram_id>/<chat_id>")
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
    return redirect(url_for("users"))


@app.route("/add_bun", methods=["POST"])
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
    return redirect(url_for("buns"))


@app.route("/edit_bun/<name>", methods=["POST"])
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
    return redirect(url_for("buns"))


@app.route("/delete_bun/<name>")
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
    return redirect(url_for("buns"))


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
                    f"Результат с ID {id} обновлен. Новые очки: {updated_points}",
                    "success",
                )
                break
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        flash(f"Ошибка при обновлении: {str(e)}", "danger")
    finally:
        loop.close()
    return redirect(url_for("results"))


@app.route("/delete_user_bun/<int:id>")
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
    return redirect(url_for("results"))


if __name__ == "__main__":
    logger.info("Запуск Flask приложения")
    # app.run(debug=True, port=5000)
    app.run(host="0.0.0.0", port=5000, debug=False)
