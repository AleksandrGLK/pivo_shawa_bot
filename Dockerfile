FROM python:3.8

WORKDIR /home

ENV TELEGRAM_API_TOKEN=$TELEGRAM_API_TOKEN 
ENV TELEGRAM_ACCESS_ID=["60956061","782745","105298587"]

ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN pip install -U pip aiogram pytz && apt-get update && apt-get install sqlite3
COPY *.py ./
COPY createdb.sql ./

ENTRYPOINT ["python", "server.py"]

