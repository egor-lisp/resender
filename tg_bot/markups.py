from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu_markup(is_work: bool):
    markup = InlineKeyboardMarkup()
    if is_work:
        markup.add(InlineKeyboardButton(text='🔴 Стоп', callback_data='stop_work'))
    else:
        markup.add(InlineKeyboardButton(text='🟢 Запустить', callback_data='start_work'))
    return markup
