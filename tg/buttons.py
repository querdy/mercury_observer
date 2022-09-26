from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import json


'''--- main menu ---'''
btnGetMilkFarm = KeyboardButton("Получить список активных заявок")
btnGetMilkFarmPeriodic = KeyboardButton("Запустить периодически")
btnGetMilkFarmPeriodicStop = KeyboardButton("Остановить")
main_menu = ReplyKeyboardMarkup(one_time_keyboard=False,
                                resize_keyboard=True).add(btnGetMilkFarm,
                                                          btnGetMilkFarmPeriodic,
                                                          btnGetMilkFarmPeriodicStop)

users_menu = ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
try:
    with open("parser/login/users.json", "r") as f:
        users = json.load(f).keys()
        for user in users:
            users_menu.insert(KeyboardButton(user))
except json.decoder.JSONDecodeError:
    pass
