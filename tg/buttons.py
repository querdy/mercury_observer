from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


'''--- main menu ---'''
btnGetMilkFarm = KeyboardButton("Получить список активных заявок")
btnGetMilkFarmPeriodic = KeyboardButton("Запустить периодически")
btnGetMilkFarmPeriodicStop = KeyboardButton("Остановить")
mainMenu = ReplyKeyboardMarkup(one_time_keyboard=False,
                               resize_keyboard=True).add(btnGetMilkFarm,
                                                         btnGetMilkFarmPeriodic,
                                                         btnGetMilkFarmPeriodicStop)
