FROM python:3.8.10

WORKDIR /twitterbot

ADD ./app ./app
ADD ./requirements.txt .

RUN pip install -r requirements.txt

CMD ["python", "./app/bot.py"]