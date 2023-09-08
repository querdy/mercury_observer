from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from tg import utils


'''--- main menu ---'''
main_menu = ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
main_menu.insert(KeyboardButton("Получить список активных заявок"))
main_menu.insert(KeyboardButton("Запустить периодически"))
main_menu.insert(KeyboardButton("Остановить"))

'''--- users menu ---'''
def get_menu_with_users() -> ReplyKeyboardMarkup:
    users = utils.get_users_data()
    users_menu = ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
    [users_menu.insert(KeyboardButton(user)) for user in users]
    users_menu.insert(KeyboardButton("Отмена"))
    return users_menu


'''--- cancel menu ---'''
cancel_menu = ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
cancel_menu.insert("Отмена")

'''--- confirm menu ---'''
confirm_menu = ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
confirm_menu.insert("Да")
confirm_menu.insert("Нет")
