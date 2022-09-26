from aiogram.dispatcher.filters.state import State, StatesGroup


class UserSingleState(StatesGroup):
    user_name = State()


class UserPeriodicState(StatesGroup):
    user_name = State()


class CreateUserState(StatesGroup):
    login = State()
    password = State()
    name = State()


class DeleteUserState(StatesGroup):
    name = State()
