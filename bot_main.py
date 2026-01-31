# import telebot
# from telebot.types import Message
# import requests
#
# API_URL = "http://127.0.0.1:8000/api"
# BOT_TOKEN = "8506817434:AAGL-o2XrOTsZishcIMhOidBcmGj8hhMAE4"
# bot = telebot.TeleBot(BOT_TOKEN)
#
#
# @bot.message_handler(commands=['start'])
# def start_command(message):
#     data = {
#         "user_id": message.from_user.id,
#         "username": message.from_user.username
#     }
#     response = requests.post(API_URL + "/register/", json=data)
#     if not response.status_code == 200:
#         if response.json().get('message'):
#             bot.send_message(message.chat.id, "Вы уже были зарегистрированы ранее!")
#         else:
#             bot.send_message(message.chat.id,
#                              f"Вы успешно зарегистрированы! Ваш уникальный номер: {response.json()['id']}")
#     else:
#         bot.send_message(message.chat.id, f"Произошла ошибка ри регистрации!")
#         print(response.json())
#         print(response.status_code)
#         print(response.text)
#
#
# if __name__ == "__main__":
#     bot.polling(none_stop=True)

import telebot
from telebot.types import Message
import requests
from requests.exceptions import JSONDecodeError, RequestException

API_URL = "http://127.0.0.1:8000/api"
BOT_TOKEN = "8506817434:AAGL-o2XrOTsZishcIMhOidBcmGj8hhMAE4"
bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start_command(message):
    data = {
        "user_id": message.from_user.id,
        "username": message.from_user.username
    }

    try:
        response = requests.post(API_URL + "/register", json=data, timeout=5)

        # Успешная регистрация (201 Created) или уже зарегистрирован (200 OK)
        if response.status_code in (200, 201):
            try:
                json_data = response.json()
                if json_data.get('message') == 'already_registered':
                    bot.send_message(message.chat.id, "Вы уже были зарегистрированы ранее!")
                else:
                    user_id = json_data.get('id', 'неизвестный')
                    bot.send_message(message.chat.id,
                                     f"Вы успешно зарегистрированы! Ваш уникальный номер: {user_id}")
            except JSONDecodeError:
                bot.send_message(message.chat.id, "✅ Регистрация прошла успешно (сервер вернул пустой ответ).")

        # Пользователь уже зарегистрирован (обычно 409 Conflict)
        elif response.status_code == 409:
            bot.send_message(message.chat.id, "Вы уже были зарегистрированы ранее!")

        # Ошибка сервера
        else:
            error_detail = "неизвестная ошибка"
            try:
                error_detail = response.json().get('detail', response.text[:100])
            except JSONDecodeError:
                error_detail = response.text[:100] if response.text else f"статус {response.status_code}"

            bot.send_message(message.chat.id, f"❌ Произошла ошибка при регистрации: {error_detail}")
            print(f"[DEBUG] Ошибка регистрации: статус={response.status_code}, тело={response.text[:200]}")

    except RequestException as e:
        bot.send_message(message.chat.id,
                         "⚠️ Сервер недоступен. Проверьте, запущен ли ваш API на http://127.0.0.1:8000")
        print(f"[DEBUG] Ошибка соединения: {e}")


@bot.message_handler(commands=['myinfo'])
def user_info(message: Message):
    url = f"{API_URL}/user/{message.from_user.id}"  # ← без слеша в конце!
    try:
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            try:
                data = response.json()
                # Форматируем красиво
                info = "\n".join(f"{k}: {v}" for k, v in data.items())
                bot.reply_to(message, f"✅ Ваша информация:\n\n{info}")
            except JSONDecodeError:
                bot.send_message(message.chat.id, "❌ Сервер вернул некорректный ответ (не JSON).")
                print(f"[DEBUG] /myinfo: не JSON, тело={response.text[:200]}")

        elif response.status_code == 404:
            bot.send_message(message.chat.id, "👤 Вы не зарегистрированы.")

        else:
            error_msg = "неизвестная ошибка"
            try:
                error_msg = response.json().get('detail', response.text[:100])
            except JSONDecodeError:
                error_msg = response.text[:100] or f"статус {response.status_code}"
            bot.send_message(message.chat.id, f"⚠️ Ошибка при получении данных: {error_msg}")
            print(f"[DEBUG] /myinfo: статус={response.status_code}, тело={response.text[:200]}")

    except RequestException as e:
        bot.send_message(message.chat.id, "🌐 Не удалось подключиться к серверу API.")
        print(f"[DEBUG] /myinfo: ошибка соединения: {e}")



if __name__ == "__main__":
    print("Бот запущен. Убедитесь, что сервер API работает на http://127.0.0.1:8000")
    bot.polling(none_stop=True)