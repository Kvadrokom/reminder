Этот телеграм-бот создан для напоминания о важных событиях.
Сама бот состоит из двух скриптов:
reminder.py - считывает и  исполняет запросы пользователя,
reninder_utils - проверяет БД sqlite3 на наличие записей о событии и в нужный момент оправляет сообщение в телеграмм
Создан модуль systemd в /etc/systemd/system/reminder.service:
[Unit]
Description=Start reminder in telegrambot

[Service]
Type=simple
Restart=on-failure
ExecStart=/bin/bash -c '/usr/bin/python3 /root/reminder.py & /usr/bin/python3 /root/reminder_utils.py'

[Install]
WantedBy=multi-user.target
