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


def check_stop_table():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM stop')
    data = c.fetchall()
    c.close()
    conn.close()
    
    if data:
        logger.debug(f"Таблица стоп не пуста. Данные: {data}")
        return True
    else:
        logger.debug("Таблица стоп пуста")
        return False
        


def clear_stop_table():
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('DELETE FROM stop')
        conn.commit()
        logger.info("Таблица стоп очищена")
        # Убрал отправку сообщения, чтобы не спамить
    except Exception as e:
        logger.error(f"Ошибка при очистке таблицы stop: {e}")
        bot.send_message(chat_id, f"Ошибка при очистке стоп-слов: {e}")
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
        
        # Получаем статус стоп-слова
        has_stop = check_stop_table()
        
        try:
            logger.debug(f"Проверена таблица stop. Результат - {has_stop}")
        except Exception as e:
            logger.error(e)
            
        try:
            # Регулярные напоминания (только если нет стоп-слова)
            if res and time_now >= 9 and time_now <= 22:
                for el in res:
                    bot.send_message(el[2], f"Напоминание для {el[3]} - {el[4]}")
                time.sleep(time_to_sleep)
                
            # Напоминание для счетчиков (только если нет стоп-слова и сегодня 23 число)
            if now_day == count_day:
                bot.send_message(chat_id, "Напоминание для Rem - счетчики")
                time.sleep(time_to_sleep)
                
            # Очищаем таблицу stop когда день изменился И есть стоп-слово
            if now_day != count_day and has_stop:
                clear_stop_table()
                logger.info("Таблица стоп очищена")               
                time.sleep(10)
                
        except Exception as e:
            logger.error(e)
            time.sleep(10)