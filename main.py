from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from scheduler.scheduler import run_scheduler

from settings import API_TOKEN_TG

from tg.handlers import register_handlers_requests


def setup_handler(dispatcher: Dispatcher):
    register_handlers_requests(dispatcher)


def main():
    bot = Bot(token=API_TOKEN_TG)
    dispatcher = Dispatcher(bot, storage=MemoryStorage())
    setup_handler(dispatcher=dispatcher)

    executor.start_polling(dispatcher,
                           skip_updates=True,
                           on_startup=run_scheduler
                           )


if __name__ == '__main__':
    main()
