# Study hub bot (IMSDS + MMMDS)

Telegram-бот, который открывает обе обучалки как Mini App и даёт квиз в чате.

## Запуск
1. @BotFather → /newbot → получить токен.
2. Опубликовать папку `docs/` на GitHub Pages (репозиторий study-hub, Settings → Pages → Deploy from branch → main, папка `/docs`).
   Адрес будет вида `https://<user>.github.io/study-hub`.
3. Запустить бота:
   ```
   pip install -r requirements.txt
   BOT_TOKEN=... WEBAPP_URL=https://<user>.github.io/study-hub python bot.py
   ```
   Для работы 24/7 нужен хост (VPS, Railway, Fly.io и т.п.), polling-процесс должен быть запущен постоянно.

## Команды
/start, /help, /link, /imsds, /mmds, /aacm, /quiz (86 тестовых вопросов IMSDS), /oral (18 устных вопросов). Кнопка меню «Учёба» открывает обе обучалки в одном окне.

`questions.json` собран из банка вопросов IMSDS Studio.
