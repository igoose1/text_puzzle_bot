import telebot
import logging
import os
from hashlib import md5
from time import sleep
from shutil import make_archive


logging.basicConfig(
    format='%(filename)s:%(lineno)d# %(levelname)-8s [%(asctime)s]  %(message)s',
    level=logging.INFO)

bot = telebot.TeleBot('TOKEN_TOKEN_TOKEN')

# telebot.apihelper.proxy = {
#     'https': 'socks5://proxy:e9eM04JNIEZ2@81.2.240.15:1337'}


def get_hash(s, double=True):
    res = md5(str(s).encode()).hexdigest()
    return get_hash(res, False) if double else res


def get_path(chat_code, note_code):
    return 'binds/{}/{}'.format(chat_code, note_code)


def get_note(chat_code, note_code):
    path = get_path(chat_code, note_code)
    title, text = None, None
    try:
        with open(path, 'r') as file:
            all_text = file.read().split('\n')
            title, text = all_text[0], '\n'.join(all_text[1:])
    except FileNotFoundError:
        title = 'Not found'

    res = 'Chat code: `{}`\nNote name: `{}`\n\n*{}*\n\n{}'.format(
        chat_code, note_code, title, text)
    return res


@bot.message_handler(commands=['add'])
def add(message):
    try:
        text = ''
        arguments = message.text.split('\n')
        if len(arguments) < 3:
            with open('messages/help.txt', 'r') as file:
                text = file.read()
        else:
            puzzle = {'name': '', 'text': ''}
            note_code = arguments[0][len('/add '):]
            chat_code = get_hash(message.chat.id)

            puzzle['name'] = arguments[1]
            puzzle['text'] = '\n'.join(arguments[2:])

            path = get_path(chat_code, note_code)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as file:
                file.write('{}\n{}'.format(puzzle['name'], puzzle['text']))

            text = get_note(chat_code, note_code)

        bot.send_message(message.chat.id, text, parse_mode='Markdown')
    except Exception as exception:
        logging.error(exception)


@bot.message_handler(commands=['rm', 'get'])
def get(message):
    try:
        command = message.text.split(' ')[0][1:]
        text = ''
        arguments = message.text.split(' ')
        if len(arguments) < 3:
            with open('messages/help.txt', 'r') as file:
                text = file.read()
        else:
            chat_code, note_code = arguments[1], ' '.join(arguments[2:])
            path = get_path(chat_code, note_code)
            if command == 'rm' and get_hash(message.chat.id) == chat_code:
                os.remove(path) if os.path.exists(path) else None
            text = get_note(chat_code, note_code)

        bot.send_message(message.chat.id, text,
                         reply_to_message_id=message.message_id, parse_mode='Markdown')
    except Exception as exception:
        logging.error(exception)


@bot.message_handler(commands=['get_archive'])
def help_start(message):
    try:
        chat_code = get_hash(message.chat.id)
        text = '{}'.format(chat_code)
        path = 'binds/{}'.format(chat_code)
        make_archive('/tmp/puzzle_bot_archive', 'zip', path)

        file = open('/tmp/puzzle_bot_archive.zip', 'rb')
        bot.send_document(message.chat.id, file, caption=text,
                          reply_to_message_id=message.message_id)
    except Exception as exception:
        logging.error(exception)


@bot.message_handler(commands=['help', 'start'])
def help_start(message):
    try:
        command = message.text.split(' ')[0][1:]
        text = ''
        with open('messages/{}.txt'.format(command), 'r') as file:
            text = file.read()
        bot.send_message(message.chat.id, text,
                         reply_to_message_id=message.message_id, parse_mode='Markdown')
    except Exception as exception:
        logging.error(exception)


if __name__ == '__main__':
    logging.info('Launching')
    while True:
        try:
            bot.polling(True)
        except Exception as exception:
            logging.error(exception)
            sleep(5)
