from tg import buttons


def ascii_only_message(function):
    async def inner_ascii_only_message(message, state):
        if message.text.isascii():
            await function(message, state)
        else:
            await message.reply('Неверный формат ввода (ascii characters only). Введите корректные данные',
                                reply_markup=buttons.cancel_menu
                                )
    return inner_ascii_only_message
