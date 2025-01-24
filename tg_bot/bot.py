from telebot import TeleBot
from telebot.types import Message, CallbackQuery
from worker import Worker
from config import ConfigManager
from tg_bot.markups import main_menu_markup

cm = ConfigManager()

bot = TeleBot(token=cm.tg_bot_token)
worker = Worker()


def users_filter(mc: Message or CallbackQuery):
    if isinstance(mc, Message):
        return mc.chat.id in cm.tg_admin_ids
    else:
        return mc.message.chat.id in cm.tg_admin_ids


@bot.message_handler(commands=['start'], func=users_filter)
def start_handler(message: Message):
    cm.read_config()

    text = f'{"Пересылка постов запущена" if worker.is_work else "Перессылка постов остановлена"}\n\n'
    if cm.vk_group_id:
        text += f'Группа вк: https://vk.com/club{cm.vk_group_id}\n\n'
    else:
        text += f'Группа в вк: не указана\n'

    text += f'Пересылка в ОК: {"Включено [выкл команда: /disable_ok]" if cm.ok_resend else "Выключено [вкл команда: /en_ok]"}\n'
    markup = main_menu_markup(worker.is_work)

    if message.from_user.id == bot.bot_id:
        bot.edit_message_text(
            chat_id=message.chat.id, message_id=message.message_id,
            text=text, reply_markup=markup
        )
    else:
        bot.send_message(
            chat_id=message.chat.id, text=text, reply_markup=markup
        )


@bot.message_handler(commands=['disable_ok', 'en_ok'], func=users_filter)
def manage_socials(message: Message):
    if message.text == '/disable_ok':
        cm.ok_resend = False
    if message.text == '/en_ok':
        cm.ok_resend = True
    cm.save_config()
    start_handler(message)


@bot.callback_query_handler(func=users_filter)
def main_callback_handler(call: CallbackQuery):

    if call.data == 'start_work':
        result = worker.start()
        if not result.get('start'):
            bot.answer_callback_query(call.id, text=result['message'], show_alert=True)
            return
        start_handler(call.message)

    if call.data == 'stop_work':
        worker.stop()
        start_handler(call.message)
