from settings import logger
import asyncio
import aioschedule
from datetime import datetime

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text

from tg import buttons
from scheduler import scheduler
from parser.start_parse import start_parse


def register_handlers_requests(dispatcher: Dispatcher):

    dispatcher.register_message_handler(get_requests,
                                        Text(equals='Получить список активных заявок',
                                             ignore_case=True)
                                        )

    dispatcher.register_message_handler(create_schedule_task,
                                        Text(equals='Запустить периодически',
                                             ignore_case=True)
                                        )

    dispatcher.register_message_handler(cancel_schedule_task,
                                        Text(equals='Остановить',
                                             ignore_case=True)
                                        )

    dispatcher.register_message_handler(help_response,
                                        commands=["help"],
                                        )

    dispatcher.register_message_handler(start_response,
                                        commands=["start"],
                                        )


async def get_requests(message: types.Message, is_schedule: bool = False):

    def is_good(dataclass_is_verified):
        return '🍚🐈🙍🏻‍♀️' if dataclass_is_verified else '❌'

    enterprises = start_parse()
    if not enterprises:
        if not is_schedule:
            await message.answer(text="Заявки отсутствуют")
            logger.info("not is_schedule; Заявки отсутствуют")
        else:
            logger.info("is_schedule; Заявки отсутствуют")

    else:
        for enterprise in enterprises:
            url = f"http://mercury.vetrf.ru/gve/{enterprise.href}"
            answer = f"{enterprise.enterprise_name} \n - <b>количество активных заявок: {enterprise.numbers_of_requests}</b>;\n "
            for transaction in enterprise.transactions_data:
                pk = 1
                car_num = transaction.car_number.value
                if transaction.trailer_number:
                    trailer_num = transaction.trailer_number.value
                    trailer_string = f"{is_good(transaction.trailer_number.is_verified)} <b>Номер прицепа:</b> {trailer_num};\n"
                else:
                    trailer_string = ""
                is_confirm = "Оформлено" if transaction.is_confirm else "Не оформлено"
                bill_of_lading = transaction.bill_of_lading
                transaction_type = transaction.transaction_type
                product = transaction.product
                answer += f"\n<b>Заявка {pk}:</b>\n" \
                    f"{is_good(transaction.car_number.is_verified)} <b>Номер авто:</b> {car_num};\n"\
                    f"{trailer_string}"\
                    f"{is_good(transaction_type.is_verified)} <b>Способ хранения при перевозке:</b> {transaction_type.value};\n"\
                    f"{is_good(product.is_verified)}<b>Продукт:</b> {product.value};\n"\
                    f"{is_good(transaction.bill_of_lading_date.is_verified)}<b>Номер ТТН:</b> {transaction.bill_of_lading} от {transaction.bill_of_lading_date.value};\n"\
                    f"<b>{is_confirm}</b>"
                    # f"<b>Получатель:</b> {transaction.recipient_enterprise};\n"\
                    # f"<b>На площадку:</b> {transaction.recipient_company};\n"
                pk += 1
            answer += f"\n <a href=\"{url}\">Открыть список заявок</a>; \n"
            logger.info('Обнаружены заявки')
            logger.debug(answer)
            await message.answer(text=answer,
                                 parse_mode=types.ParseMode.HTML
                                 )


async def create_schedule_task(message: types.Message):
    user_tasks = scheduler.get_user_tasks(message.from_user.id)
    if user_tasks:
        logger.info('Попытка запуска периодических тасок. Уже запущено')
        await message.answer(text="Уже запущено")
    else:
        await scheduler.job_create(function=get_requests, params=[message, True])
        logger.info('Периодические таски запущены')
        await message.answer(text="Запустилось")
        
        
async def cancel_schedule_task(message: types.Message):
    user_tasks = scheduler.get_user_tasks(message.from_user.id)
    if len(user_tasks) > 0:
        scheduler.job_remove(user_tasks)
        logger.info('Периодические таски остановлены')
        await message.answer(text="Остановлено")
    else:
        logger.info('Попытка остановки периодических тасок. Периодические таски не запущены')
        await message.answer(text="Не запущено")


async def start_response(message: types.Message):
    await message.reply("/help, чтобы прочитать описание",
                        reply_markup=buttons.mainMenu
                        )


async def help_response(message: types.Message):
    help_message = "Парсер наличия заявок для ГВЭ в Меркурии.\n" + \
        "1. \"Получить список активных заявок\" - возвращает список ферм с новыми заявками транзакций; \n" + \
        "2. \"Запустить периодически\" - п.1, проверка раз в несколько минут; \n" + \
        "3. \"Остановить\" - остановка периодического выполнения"
    await message.reply(text=help_message,
                        reply_markup=buttons.mainMenu,
                        )


async def random_message(message: types.Message):
    """Обработка случайного сообщения для вывода клавиатуры"""

    answer = "Я даже не знаю, что ответить~"
    await message.answer(answer,
                         reply_markup=buttons.mainMenu)

