"""Study bot: opens the IMSDS / MMMDS study hub as a Telegram Mini App and quizzes in chat.
Env: BOT_TOKEN, WEBAPP_URL (public https URL of web/index.html, e.g. GitHub Pages)."""
import json, os, random, asyncio, re
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import (Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
                           WebAppInfo, MenuButtonWebApp, BotCommand)

TOKEN, URL = os.environ["BOT_TOKEN"], os.environ["WEBAPP_URL"].rstrip("/")
DATA = json.load(open(os.path.join(os.path.dirname(__file__), "questions.json"), encoding="utf-8"))
BANK, ORAL, LES = DATA["bank"], DATA["oral"], DATA["lessons"]
bot, dp = Bot(TOKEN), Dispatcher()
STATE: dict[int, dict] = {}  # user_id -> {"score":int,"n":int,"q":dict}

def app_kb():
    wa = lambda t, p: InlineKeyboardButton(text=t, web_app=WebAppInfo(url=f"{URL}/{p}"))
    return InlineKeyboardMarkup(inline_keyboard=[
        [wa("IMSDS Studio", "imsds.html")], [wa("MMMDS Exam Studio", "mmds.html")], [wa("AACM Studio", "aacm.html")],
        [wa("Все предметы в одном окне", "index.html")],
        [InlineKeyboardButton(text="🌐 Открыть сайт в браузере", url=f"{URL}/index.html")],
        [InlineKeyboardButton(text="Квиз IMSDS в чате", callback_data="quiz")]])

@dp.message(CommandStart())
async def start(m: Message):
    await m.answer("JulYera study hub: IMSDS, MMMDS и AACM.\n\nВыбери предмет кнопкой ниже. Как пользоваться, в том числе сайтом в браузере и переносом прогресса: /help", reply_markup=app_kb())

@dp.message(Command("imsds"))
async def c_imsds(m: Message):
    await m.answer("IMSDS Studio", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Открыть", web_app=WebAppInfo(url=f"{URL}/imsds.html"))]]))

HELP = (
    "Как это работает\n\n"
    "1. В Telegram: кнопка «Учёба» слева от поля ввода или /start открывает хаб прямо в чате. "
    "Прогресс и язык сохраняются на твой аккаунт автоматически.\n\n"
    "2. В браузере (ноутбук, другой телефон): открой " + URL + "/index.html и нажми «Войти через Telegram» в правом нижнем углу. "
    "Прогресс подтянется сам.\n\n"
    "3. Быстрее всего: в Mini App в шапке есть кнопка ↗. Она открывает сайт в браузере уже под твоим аккаунтом, без входа.\n\n"
    "Прогресс общий везде: что отметил в боте, видно на сайте, и наоборот. Язык RU/EN переключается в шапке.\n\n"
    "Команды: /imsds /mmds /aacm /quiz /oral /link")

@dp.message(Command("help"))
async def c_help(m: Message):
    await m.answer(HELP, disable_web_page_preview=True)

@dp.message(Command("link"))
async def c_link(m: Message):
    await m.answer("Сайт (открывается в любом браузере): " + URL + "/index.html\n\nЧтобы прогресс был тот же, что в боте, нажми на сайте «Войти через Telegram» или открой его из бота кнопкой ↗ в шапке.\n\nСсылка на бота: https://t.me/dsstudyhub_bot", disable_web_page_preview=True)


@dp.message(Command("aacm"))
async def c_aacm(m: Message):
    await m.answer("AACM Studio (Advanced Algorithms)", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Открыть", web_app=WebAppInfo(url=f"{URL}/aacm.html"))]]))


@dp.message(Command("mmds"))
async def c_mmds(m: Message):
    await m.answer("MMMDS Exam Studio", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Открыть", web_app=WebAppInfo(url=f"{URL}/mmds.html"))]]))

async def ask(target: Message, uid: int):
    q = random.choice(BANK); st = STATE.setdefault(uid, {"score": 0, "n": 0}); st["q"] = q
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=o[:60], callback_data=f"a{i}")] for i, o in enumerate(q["opts"])])
    await target.answer(f"{LES.get(q['lesson'], '')}\n\n{q['q']}", reply_markup=kb)

@dp.message(Command("quiz"))
async def c_quiz(m: Message):
    STATE[m.from_user.id] = {"score": 0, "n": 0}; await ask(m, m.from_user.id)

@dp.callback_query(F.data == "quiz")
async def cb_quiz(c: CallbackQuery):
    STATE[c.from_user.id] = {"score": 0, "n": 0}; await c.answer(); await ask(c.message, c.from_user.id)

@dp.callback_query(F.data.startswith("a"))
async def cb_ans(c: CallbackQuery):
    st = STATE.get(c.from_user.id)
    if not st or "q" not in st: return await c.answer("Начни: /quiz")
    q = st.pop("q"); i = int(c.data[1:]); ok = i == q["a"]; st["n"] += 1; st["score"] += ok
    await c.answer()
    await c.message.edit_text(f"{q['q']}\n\n{'Верно.' if ok else 'Неверно.'} Правильный ответ: {q['opts'][q['a']]}\n{q['why']}\n\nСчёт: {st['score']}/{st['n']}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Дальше", callback_data="quiz2")]]))

@dp.callback_query(F.data == "quiz2")
async def cb_next(c: CallbackQuery):
    await c.answer(); await ask(c.message, c.from_user.id)

def md(t: str) -> str:
    return re.sub(r"([_*\[\]()~`>#+\-=|{}.!\\])", r"\\\1", t)

@dp.message(Command("oral"))
async def c_oral(m: Message):
    o = random.choice(ORAL)
    await m.answer(f"{md(LES.get(o['lesson'], ''))}\n\n{md(o['q'])}\n\nОтвет \\(нажми, чтобы показать\\):\n||{md(o['a'])}||", parse_mode="MarkdownV2")

async def main():
    await bot.set_my_commands([BotCommand(command="start", description="Открыть учебный хаб"), BotCommand(command="imsds", description="IMSDS Studio"),
        BotCommand(command="mmds", description="MMMDS Exam Studio"), BotCommand(command="aacm", description="AACM Studio"), BotCommand(command="help", description="Как пользоваться"), BotCommand(command="link", description="Ссылка на сайт"), BotCommand(command="quiz", description="Квиз IMSDS в чате"), BotCommand(command="oral", description="Устный вопрос")])
    await bot.set_chat_menu_button(menu_button=MenuButtonWebApp(text="Учёба", web_app=WebAppInfo(url=f"{URL}/index.html")))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
