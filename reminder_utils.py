from datetime import datetime
import datetime
from reminder import get_connection, bot
import time



chat_id = 1838289390


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


if __name__ == '__main__':
    while True:
        now_day = datetime.datetime.now().day
        res = check_reminders()
        time_now = int(str(datetime.datetime.now().time()).split(':')[0])
        if res and time_now >= 9 and time_now <= 22:
            for el in res:
                bot.send_message(el[2], f"Напоминание для {el[3]} - {el[4]}")
            time.sleep(1800)
        if now_day == 20:
            bot.send_message(chat_id, "Напоминание для Rem - счетчики")
            time.sleep(1800)
        else:
            time.sleep(10)
