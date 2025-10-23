from telebot_token import token
from logging import *
import sqlite3
import time
import telebot
from telebot import types
from datetime import datetime, timezone, timedelta
import datetime
from telebot.types import ReplyKeyboardRemove, CallbackQuery
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
import os

log_dir = '/var/log/reminder_log'
log = "reminder.log"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)


file_handler = FileHandler(f"{log_dir}/{log}", mode='a')
console = StreamHandler()
console.setLevel(ERROR)
file_handler.setLevel(DEBUG)
basicConfig(level='INFO', filename='/var/log/reminder_log/reminder.log',
            format='%(levelname)s (%(asctime)s): %(message)s (Line: %(lineno)d) [%(filename)s]',
            datefmt='%d/%m/%Y %H:%M:%S', filemode='a')
#form = '%(levelname)s (%(asctime)s): %(message)s (Line: %(lineno)d) [%(filename)s]'
# basicConfig(level='DEBUG', format=form,
#             datefmt='%d/%m/%Y %I:%M:%S', filename='reminder.log', filemode='w', encoding='utf-8')
logger = getLogger(__name__)

getLogger('urllib3').setLevel('ERROR')
logger.addHandler(console)
logger.addHandler(file_handler)


# logger.addHandler(file_handler)

def get_connection():
    connection = sqlite3.connect('bot_db')
    #logger.info('Connection get!')
    return connection


def init_db(force: bool = False):
    conn = get_connection()
    c = conn.cursor()
    if force:
        c.execute('drop table if exists user_message')
        c.execute('drop table if exists remind')
    c.execute('''
        create table if not exists user_message (
            id          integer primary key,
            user_id     integer not Null,
            user_name   varchar(50),
            text        TEXT not Null,
            date_time   TEXT not Null
        )
    ''')
    c.execute('''
                   create table if not exists remind (
                       id          integer primary key,
                       user_id     integer not Null,
                       chat_id     integer not Null,
                       user_name   varchar(50),
                       reminder    TEXT not Null,
                       period      TEXT
                   )
               ''')

    c.execute('''
                       create table if not exists tremind (
                           id          integer primary key,
                           user_id     integer not Null,
                           chat_id     integer not Null,
                           user_name   varchar(50),
                           reminder    TEXT not Null,
                           period      TEXT
                       )
                   ''')
    c.execute('''
                       create table if not exists stop (
                           id          integer primary key,
                           stop      TEXT
                       )
                   ''')
    c.close()
    conn.close()


def add_message(user_id: int, user_name: str, text: str, str_date: str):
    # logger.info('user_id =', user_id, 'user_name =', user_name, 'text =', text, 'str_date =', str_date)
    conn = get_connection()
    c = conn.cursor()
    c.execute('insert into user_message (user_id, user_name, text, date_time) values (?, ?, ?, ?)',
              (user_id, user_name, text, str_date))
    conn.commit()
    c.close()
    logger.info('Message add!')
    conn.close()


def register_reminder(message):
    logger.info('New remind - \'%s\' for %s', message.text, message.from_user.first_name)
    conn = get_connection()
    c = conn.cursor()
    try:
        logger.info(
            'Trying insert into remind values(user_id = %d chat_id = %d user_name = %s reminder = %s',
            message.id, message.chat.id, message.from_user.first_name, message.text)

        c.execute('insert into remind(user_id, chat_id, user_name, reminder, period) values (?, ?, ?, ?, ?)',
                  (message.id, message.chat.id, message.from_user.first_name, message.text, ''))
        conn.commit()

        logger.info(
            'Successfully insert into remind values(user_id = %d chat_id = %d user_name = %s reminder = %s',
            message.id, message.chat.id, message.from_user.first_name, message.text)

        calendar, step = DetailedTelegramCalendar().build()
        bot.send_message(message.chat.id,
                         f"Select {LSTEP[step]}",
                         reply_markup=calendar)
    except Exception as e:
        logger.info(e)
        bot.send_message(message.chat.id, 'Что то пошло не так... Введите /new')
    finally:
        c.close()
        conn.close()


def set_reminder_time(time, id):
    conn = get_connection()
    c = conn.cursor()
    c.execute(f'update remind set period = ? where user_id = ?', (time, id - 1))
    conn.commit()
    if c.rowcount > 0:
        logger.info('date set! time = %s', time)
    c.close()
    conn.close()
    logger.debug('id = %s', id - 1)


bot = telebot.TeleBot(token)

if __name__ == '__main__':
    init_db()


    @bot.message_handler(commands=['start'])
    def start(message):
        date_time = datetime.datetime.now()
        str_date = date_time.strftime("%d.%m.%Y %H:%M")
        add_message(message.id, message.from_user.first_name, message.text, str_date)
        bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!')
        logger.info('Привет, %s(command /start)', message.from_user.first_name)


    @bot.message_handler(commands=['show'])
    def show(message):
        logger.info('Запрос информации для %s', message.from_user.first_name)
        conn = get_connection()
        c = conn.cursor()
        c.execute(f"select reminder, period from remind where user_name = \'{message.from_user.first_name}\'")
        data = c.fetchall()
        if data:
            for i in data:
                bot.send_message(message.chat.id, str(i))
                logger.info('Напоминание %s для %s. Command /show', i, message.from_user.first_name)
        else:
            bot.send_message(message.chat.id, 'Напоминания отсутствуют')


    @bot.message_handler(commands=['new'])
    def reminder(message):
        bot.send_message(message.chat.id, 'Введите текст напоминания')
        bot.register_next_step_handler(message, register_reminder)


    @bot.callback_query_handler(func=DetailedTelegramCalendar.func())
    def cal(c):
        result, key, step = DetailedTelegramCalendar().process(c.data)
        if not result and key:
            bot.edit_message_text(f"Select {LSTEP[step]}",
                                  c.message.chat.id,
                                  c.message.message_id,
                                  reply_markup=key)
        elif result:
            bot.edit_message_text(f"You selected {result}",
                                  c.message.chat.id,
                                  c.message.message_id)
            set_reminder_time(str(result), c.message.message_id)


    @bot.message_handler(commands=['clear'])
    def clear_all(message):
        conn = get_connection()
        c = conn.cursor()
        try:
            c.execute(f"delete from remind")
            logger.info('Trying to delete all tuples in reminder table')
            if c.rowcount != 0:
                bot.send_message(message.chat.id, f'Все напоминания удалены')
                logger.info("Successfully delete all tuples in reminder table")
                conn.commit()
        except Exception as e:
            logger.error(e)
            bot.send_message(message.chat.id, f'Что-то пошло не так - {e}')
        finally:
            c.close()
            conn.close()


    @bot.message_handler()
    def delete_reminder(message):
        print('Hi from delete_reminder!')
        text = []
        if 'del' in message.text.lower():
            text = message.text.split(' ', 1)
            conn = get_connection()
            c = conn.cursor()
            try:
                c.execute(f"delete from remind where reminder = \'{text[1]}\'")
                logger.info('Trying to delete %s', text[1])
                if c.rowcount != 0:
                    bot.send_message(message.chat.id, f'Напоминание удалено({text[1]})')
                    logger.info("Successfully delete \'%s\'", text[1])
                    conn.commit()
                else:
                    bot.send_message(message.chat.id, f'Напоминание не найдено({text[1]})')
                    logger.info('This remind \'%s\' is absent', text[1])
            except Exception as e:
                logger.error(e)
            finally:
                c.close()
                conn.close()
        elif 'getall reminder' in message.text.lower():
            conn = get_connection()
            c = conn.cursor()
            try:
                c.execute(f"select * from remind")
                logger.info('Getting all info from reminder')
                rows = c.fetchall()
                if rows:
                    for row in rows:
                        row = list(map(str, row))
                        bot.send_message(message.chat.id,  " ".join(row))
                        logger.info(row)
                else:
                    bot.send_message(message.chat.id, f'таблица пуста')
                    logger.info('the table remind is empty')
            except Exception as e:
                logger.error(e)
            finally:
                c.close()
                conn.close()
        elif 'getall user_message' in message.text.lower():
            conn = get_connection()
            c = conn.cursor()
            try:
                c.execute(f"select * from user_message")
                logger.info('Getting all info from user_message')
                rows = c.fetchall()
                if rows:
                    for row in rows:
                        row = list(map(str, row))
                        bot.send_message(message.chat.id,  " ".join(row))
                        logger.info(row)
                else:
                    bot.send_message(message.chat.id, f'таблица user_message пуста')
                    logger.info('the table user_message is empty')
            except Exception as e:
                logger.error(e)
            finally:
                c.close()
                conn.close()
        elif 'getall tables' in message.text.lower():
            conn = get_connection()
            c = conn.cursor()
            try:
                c.execute("SELECT name FROM sqlite_master WHERE type='table';")
                logger.info('Getting all tables from db')
                rows = c.fetchall()
                if rows:
                    for row in rows:
                        bot.send_message(message.chat.id,  row)
                        logger.info(row)
                else:
                    bot.send_message(message.chat.id, f'В БД нет таблиц')
                    logger.info('The DB is empty')
            except Exception as e:
                logger.error(e)
            finally:
                c.close()
                conn.close()
        elif 'stop' in message.text.lower():
            conn = get_connection()
            c = conn.cursor()
            try:
                logger.info('Stopping water meters info')
                c.execute('insert into stop (stop) values (?)', (message.text.lower(),))
                logger.info('Successfully insert stop word')
            except Exception as e:
                logger.error(e)
            finally:
                c.close()
                conn.close()



    bot.polling(none_stop=True)

