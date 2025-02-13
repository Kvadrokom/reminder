FROM python:3.10.5-slim-buster
COPY reminder.py /app/
COPY reminder_utils.py /app/
COPY requirements.txt /app/
COPY telebot_token.py /app/
RUN apt update -y && apt upgrade -y
RUN /usr/local/bin/python -m pip install --upgrade pip
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python3", "reminder.py"]
