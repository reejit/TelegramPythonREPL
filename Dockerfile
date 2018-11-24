FROM python:alpine

ADD requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

ADD bot.py /app/bot.py
WORKDIR /app

CMD ["python", "bot.py"]
