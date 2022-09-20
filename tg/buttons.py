from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


'''--- main menu ---'''
btnGetMilkFarm = KeyboardButton("Получить список активных заявок")
btnGetMilkFarmPeriodic = KeyboardButton("Запустить периодически")
btnGetMilkFarmPeriodicStop = KeyboardButton("Остановить")
mainMenu = ReplyKeyboardMarkup(one_time_keyboard=False,
                               resize_keyboard=True).add(btnGetMilkFarm,
                                                         btnGetMilkFarmPeriodic,
                                                         btnGetMilkFarmPeriodicStop)

mainMenu_1 = ReplyKeyboardMarkup(one_time_keyboard=False,
                                 resize_keyboard=True).add(btnGetMilkFarm,
                                                           btnGetMilkFarmPeriodic)

mainMenu_2 = ReplyKeyboardMarkup(one_time_keyboard=False,
                                 resize_keyboard=True).add(btnGetMilkFarm,
                                                           btnGetMilkFarmPeriodicStop)
