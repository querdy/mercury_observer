from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import json


'''--- main menu ---'''
main_menu = ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
main_menu.insert(KeyboardButton("Получить список активных заявок"))
main_menu.insert(KeyboardButton("Запустить периодически"))
main_menu.insert(KeyboardButton("Остановить"))

'''--- users menu ---'''
users_menu = ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
try:
    open("parser/login/users.json", "x").close()
except FileExistsError:
    pass
try:
    with open("parser/login/users.json", "r") as f:
        users = json.load(f).keys()
        for user in users:
            users_menu.insert(KeyboardButton(user))
    users_menu.insert(KeyboardButton("Отмена"))
except json.decoder.JSONDecodeError:
    pass

'''--- cancel menu ---'''
cancel_menu = ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
cancel_menu.insert("Отмена")

'''--- confirm menu ---'''
confirm_menu = ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
confirm_menu.insert("Да")
confirm_menu.insert("Нет")
