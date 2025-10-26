from datetime import datetime
import datetime
from reminder import get_connection, bot
import time
from bot_logger import setup_logger



chat_id = 1838289390
log_dir = '/var/log/'
log_file = "reminder.log"
logger = setup_logger(log_dir, log_file)


def check_reminders():
    result = []
    date_time = datetime.datetime.now()
    str_date = str(date_time.strftime("%Y-%m-%d"))
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM remind')
    data = c.fetchall()
    for i in data:
        if str_date in i:
            result.append(i)
    c.close()
    conn.close()
    return  result


def check_stop():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM stop')
    data = c.fetchall()
    try:
      if data:
        bot.send_message(chat_id, data)
    except Exception as e:
      logger.error(e)
    c.close()
    conn.close()
    if data:
        return True


def clear_stop_table():
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('Delete FROM stop')
        bot.send_message(chat_id, "Остановлено напоминание для Rеm - счетчики")
    except Exception as e:
        bot.send_message(chat_id, f"Error - {e}")
    finally:
        c.close()
        conn.close()

if __name__ == '__main__':
    while True:
        count_day = 23
        time_to_sleep = 300
        now_day = datetime.datetime.now().day
        res = check_reminders()
        time_now = int(str(datetime.datetime.now().time()).split(':')[0])
        check_stop = check_stop()
        try:
            logger.debug(f"Проверена таблица stop. Результат - {check_stop}")
        except Exception as e:
            logger.error(e)
        try:
            if res and time_now >= 9 and time_now <= 22:
                for el in res:
                    bot.send_message(el[2], f"Напоминание для {el[3]} - {el[4]}")
                time.sleep(time_to_sleep)
            if now_day == count_day and not check_stop:
                bot.send_message(chat_id, "Напоминание для Rem - счетчики")
                time.sleep(time_to_sleep)
            else:
                time.sleep(10)
            if now_day != count_day and  check_stop:
                clear_stop_table
                bot.send_message(chat_id, "Таблица стоп очищена")
        except Exception as e:
            logger.error(e)