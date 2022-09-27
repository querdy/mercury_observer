import json
from datetime import datetime

import settings
from parser.login.mercury_login import check_cookies
from settings import logger

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from tg import buttons
from tg.decorators import ascii_only_message
from tg.states import UserSingleState, UserPeriodicState, CreateUserState, DeleteUserState
from scheduler import scheduler
from parser.start_parse import start_parse
from tg.utils import save_user_data, delete_user, get_users_data

NOTIFIED_TRANSACTION = []


def register_handlers_requests(dispatcher: Dispatcher):
    dispatcher.register_message_handler(cancel_handler, commands=["cancel"], state="*")

    dispatcher.register_message_handler(cancel_handler, Text(equals='Отмена', ignore_case=True), state="*")

    dispatcher.register_message_handler(get_name_for_single, Text(equals='Получить список активных заявок',
                                                                  ignore_case=True))

    dispatcher.register_message_handler(start_single_parse, state=UserSingleState.user_name)

    dispatcher.register_message_handler(get_name_for_periodic, Text(equals='Запустить периодически',
                                                                    ignore_case=True))

    dispatcher.register_message_handler(start_periodic_parse, state=UserPeriodicState.user_name)

    dispatcher.register_message_handler(cancel_periodic_parse, Text(equals='Остановить',
                                                                    ignore_case=True))

    dispatcher.register_message_handler(help_response, commands=["help"])

    dispatcher.register_message_handler(start_response, commands=["start"])

    dispatcher.register_message_handler(start_user_registration, commands=["adduser"], state=None)

    dispatcher.register_message_handler(load_login, state=CreateUserState.login)

    dispatcher.register_message_handler(load_password, state=CreateUserState.password)

    dispatcher.register_message_handler(load_name, state=CreateUserState.name)

    dispatcher.register_message_handler(delete_user_start, commands=["deleteuser"], state=None)

    dispatcher.register_message_handler(delete_user_confirm, state=DeleteUserState.user_name)

    dispatcher.register_message_handler(delete_user_finish, state=DeleteUserState.confirm)


async def get_name_for_periodic(message: types.Message):
    await UserPeriodicState.user_name.set()
    users_munu = buttons.get_menu_with_users()
    await message.reply('Выберите пользователя', reply_markup=users_munu)


async def get_name_for_single(message: types.Message):
    await UserSingleState.user_name.set()
    users_munu = buttons.get_menu_with_users()
    await message.reply('Выберите пользователя', reply_markup=users_munu)


async def start_periodic_parse(message: types.Message, state: FSMContext):
    await state.update_data(user_name=message.text)
    data = await state.get_data()
    user_name = data.get('user_name')
    user_tasks = scheduler.get_user_tasks(message.from_user.id)
    if user_tasks:
        logger.info('Попытка запуска периодических тасок. Уже запущено')
        await state.finish()
        await message.answer(text="Уже запущено", reply_markup=buttons.main_menu)
    else:
        await scheduler.job_create(function=get_requests, params=[message, user_name, True])
        logger.info(f'Периодические таски запущены, user: {user_name}')
        await message.answer(text=f"Периодическая проверка запущена. user: {user_name}", reply_markup=buttons.main_menu)
        await state.finish()


async def start_single_parse(message: types.Message, state: FSMContext):
    await state.update_data(user_name=message.text)
    data = await state.get_data()
    try:
        await message.reply(text=f"Запуск одиночной проверки. Пользователь: {data.get('user_name')}", reply_markup=buttons.main_menu)
        await get_requests(message, user_name=data.get('user_name'))
    except json.decoder.JSONDecodeError:
        await message.answer("Пользователь не существует")
    finally:
        await state.finish()


async def get_requests(message: types.Message, user_name: str, is_schedule: bool = False):

    def is_good(dataclass_is_verified):
        return '🍚🐈🙍🏻‍♀️' if dataclass_is_verified else '❌'

    sess = check_cookies(user_name=user_name)
    if sess is None:
        await message.answer(text="Не удалось залогиниться")
        return
    enterprises = start_parse(sess)
    if not enterprises:
        if not is_schedule:
            await message.answer(text="Заявки отсутствуют")
            logger.info(f"not is_schedule; user: {user_name}; Заявки отсутствуют")
        else:
            logger.info(f"is_schedule; user: {user_name}; Заявки отсутствуют")

    else:
        for enterprise in enterprises:
            url = f"http://mercury.vetrf.ru/gve/{enterprise.href}"
            answer = f"{enterprise.enterprise_name} \n - <b>количество активных заявок: {enterprise.numbers_of_requests}</b>;\n "
            pk = 1
            for transaction in enterprise.transactions_data:
                if (transaction.date_from - datetime.now()).total_seconds() < 0:
                    NOTIFIED_TRANSACTION.clear()
                if transaction.rq_transaction_pk in NOTIFIED_TRANSACTION and is_schedule:
                    continue
                # pk = 1
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
                    f"{'🍚🐈🙍🏻‍♀️' if transaction.is_expiration() else '❌ '}Срок годности 36ч: {transaction.is_expiration()}\n"\
                    f"{is_good(transaction.bill_of_lading_date.is_verified)}<b>Номер ТТН:</b> {transaction.bill_of_lading} от {transaction.bill_of_lading_date.value};\n"
                if not transaction.is_confirm:
                    answer += f"<b>Выработка:</b> {transaction.date_from}\n"
                answer += f"<b>\n{is_confirm}\n</b>"
                    # f"<b>Получатель:</b> {transaction.recipient_enterprise};\n"\
                    # f"<b>На площадку:</b> {transaction.recipient_company};\n"
                pk += 1
                NOTIFIED_TRANSACTION.append(transaction.rq_transaction_pk)
            logger.debug(answer)
            logger.info(f"Обнаружены заявки. user: {user_name}")
            if "Заявка" not in answer:
                answer = ""
            if answer != "":
                answer += f"\n <a href=\"{url}\">Открыть список заявок</a>; \n"
                await message.answer(text=answer,
                                     parse_mode=types.ParseMode.HTML
                                     )


async def start_user_registration(message: types.Message):
    await CreateUserState.login.set()
    await message.reply('Введите логин', reply_markup=buttons.cancel_menu)


@ascii_only_message
async def load_login(message: types.Message, state: FSMContext):
    await state.update_data(login=message.text)
    await CreateUserState.password.set()
    await message.reply('Введите пароль', reply_markup=buttons.cancel_menu)


@ascii_only_message
async def load_password(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)
    await CreateUserState.name.set()
    await message.reply('Введите отображаемое имя', reply_markup=buttons.cancel_menu)


@ascii_only_message
async def load_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    data = await state.get_data()
    if save_user_data(data.get('name'), **{"login": data.get('login'), "password": data.get('password'), "cookies": {}}):
        await message.reply(f"Пользователь {data.get('name')} добавлен", reply_markup=buttons.main_menu)
    else:
        await message.reply("Не удалось добавить пользователя")
    await state.finish()


async def delete_user_start(message: types.Message):
    await DeleteUserState.user_name.set()
    users_munu = buttons.get_menu_with_users()
    await message.reply('Выберите пользователя', reply_markup=users_munu)


async def delete_user_confirm(message: types.Message, state: FSMContext):
    if message.text in get_users_data():
        await state.update_data(name=message.text)
        await DeleteUserState.confirm.set()
        await message.reply(f"Точно удалить пользователя {message.text}?", reply_markup=buttons.confirm_menu)
    else:
        users_munu = buttons.get_menu_with_users()
        await message.reply(f"Такого пользователя не существует. Введите существующего пользователя", reply_markup=users_munu)


async def delete_user_finish(message: types.Message, state: FSMContext):
    await state.update_data(confirm=message.text)
    data = await state.get_data()
    if data.get("confirm").lower() == "да" or data.get("confirm").lower() == "yes":
        if delete_user(data.get("name")):
            logger.info(f"{data.get('name')} удален(а)")
            await message.reply(f"{data.get('name')} удален(а)", reply_markup=buttons.main_menu)
        else:
            await message.reply(f"Не удалось удалить пользователя: {data.get('name')}")
        await state.finish()
    elif data.get("confirm").lower() == "нет" or data.get("confirm").lower() == "no":
        await state.finish()
        await message.answer("Отмена", reply_markup=buttons.main_menu)
    else:
        await message.reply("Выберите: да(yes) или нет(no)", reply_markup=buttons.confirm_menu)

        
async def cancel_periodic_parse(message: types.Message):
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
                        reply_markup=buttons.main_menu
                        )


async def help_response(message: types.Message):
    help_message = "Парсер наличия заявок для ГВЭ в Меркурии.\n" + \
        "1. \"Получить список активных заявок\" - возвращает список ферм с заявками транзакций; \n" + \
        "2. \"Запустить периодически\" - п.1, проверка раз в несколько минут; \n" + \
        "3. \"Остановить\" - остановка периодического выполнения \n" \
        "/adduser - добавить пользователя \n" \
        "/deleteuser - удалить пользователя \n" \
        "/cancel - сброс состояния \n"
    await message.reply(text=help_message, reply_markup=buttons.main_menu)


async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    logger.info('Сброс состояния')
    if current_state is None:
        return
    await state.finish()
    await message.reply("Ок~", reply_markup=buttons.main_menu)


