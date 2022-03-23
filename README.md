Telegram бот для учёта выпитого пивка и шавермы, для вас и ваших друзей 
В переменных окружения надо проставить API токен бота

`TELEGRAM_API_TOKEN` — API токен бота
`TELEGRAM_ACCESS_ID` — Список ID Telegram аккаунтов, от которых будут приниматься сообщения (сообщения от остальных аккаунтов игнорируются)

```
docker build -t pivobot ./
docker run -d --name tg -v /local_project_path/db:/home/db pivobot
```

Чтобы войти в работающий контейнер:

```
docker exec -ti tg bash
```

Войти в контейнере в SQL шелл:

```
docker exec -ti tg bash
sqlite3 /home/db/finance.db
```


