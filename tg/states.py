from aiogram.dispatcher.filters.state import State, StatesGroup


class UserState(StatesGroup):
    is_perdiodic = State(StatesGroup)
