import asyncio
import random
import os
from datetime import datetime, timedelta
import pytz
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyParameters

API_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
STICKER_ID = os.getenv('STICKER_ID')

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

BASE_PRESCRIPTIONS = list(set([
    "Оставить мелкую монету на подоконнике любого общественного здания.",
    "Пересчитать все трещины на бордюре у ближайшего перекрестка.",
    "Коснуться рукой стены старого каменного здания и постоять так минуту.",
    "Купить два билета на автобус и один оставить на сиденье.",
    "Завязать узел на ветке дерева по пути к дому.",
    "Выпить стакан воды, глядя строго на север.",
    "Пропустить три идущих подряд автобуса или трамвая.",
    "Найти камень с острыми краями и переложить его на траву.",
    "Прочитать вслух любую вывеску синего цвета.",
    "Постоять на пешеходном переходе лишний цикл светофора.",
    "Сложить из чека самолетик и оставить его на скамье в парке.",
    "Коснуться подошвой обуви железного люка на дороге.",
    "Пройти мимо своего подъезда и вернуться к нему через пять минут.",
    "Нарисовать пальцем на пыльном стекле круг с точкой в центре.",
    "Посмотреть на самую высокую точку здания в течение 30 секунд.",
    "Считать шаги до поворота, а затем намеренно сбиться со счета.",
    "Поправить воротник одежды, глядя на восток.",
    "Найти дерево с облупившейся корой и провести по нему ладонью.",
    "Переложить телефон в другой карман до следующего утра.",
    "Сделать глубокий вдох, проходя под любой аркой.",
    "Постучать по дереву трижды, не думая о причине.",
    "Положить в карман небольшой гладкий камень с дороги.",
    "Уйти с привычного маршрута на одну параллельную улицу.",
    "Кивнуть своему отражению в случайном зеркале или витрине.",
    "Считать красные машины, пока не насчитаешь пять штук.",
    "Оставить открытой любую дверь на пару секунд дольше обычного.",
    "Потрогать железные перила лестницы указательным пальцем.",
    "Произнести свое имя задом наперед, глядя в окно.",
    "Выбросить старый ненужный чек в самую дальнюю урну от дома.",
    "Постоять под фонарным столбом, пока он не изменит состояние (вкл/выкл).",
    "Написать на запотевшем стекле букву 'Г' и сразу стереть её.",
    "Перешагнуть через стык дорожных плит, не наступая на шов.",
    "Выбрать окно в доме напротив и представить, что там находится.",
    "Повернуть ключ в замке максимально медленно.",
    "Найти предмет, который явно старше тебя, и коснуться его.",
    "Слушать шум города минуту, стараясь услышать звук воды.",
    "Положить ладонь на почтовый ящик в своем подъезде.",
    "Сложить пальцы в замок и потянуть руки вверх перед входом в здание.",
    "Найти на асфальте пятно необычной формы и обойти его по кругу.",
    "Дождаться, пока мимо пройдет человек в черном, и только тогда продолжить путь.",
    "Прикоснуться к самому тонкому дереву, которое встретишь.",
    "Проверить, закрыта ли входная дверь, ровно два раза.",
    "Проводить взглядом птицу в небе до тех пор, пока она не скроется.",
    "Сложить руки за спиной и пройти так ровно десять шагов.",
    "Оставить сухую ветку на крышке мусорного бака.",
    "Провести пальцем по любой металлической ограде.",
    "Запомнить три цифры номера первой проехавшей машины.",
    "Остановиться у витрины книжного магазина на минуту.",
    "Сделать пять шагов по прямой линии, как по канату.",
    "Посмотреть на уличные часы и дождаться смены минуты.",
    "Коснуться края любого дорожного знака."
]))

SIMPLE_PRESCRIPTIONS = list(set([
    "Пописяй.", "Покакай.", "Моргни.", "Топни ногой.", "Посмотри влево.",
    "Почеши нос.", "Зевни.", "Скажи 'Ой'.", "Хлопни в ладоши.", "Подними палец вверх."
]))

base_queue, simple_queue = [], []
waiting_for_execution = False

def get_next(queue, source):
    if not queue:
        queue.extend(source)
        random.shuffle(queue)
    return queue.pop(0)

async def wait_until_morning():
    kiev_tz = pytz.timezone('Europe/Kyiv')
    while True:
        now = datetime.now(kiev_tz)
        if 8 <= now.hour < 20: break
        target = now.replace(hour=8, minute=0, second=0, microsecond=0)
        if now.hour >= 20: target += timedelta(days=1)
        await asyncio.sleep(min((target - now).total_seconds(), 3600))

async def send_will():
    global waiting_for_execution
    await wait_until_morning()
    text = f"\_ПРЕДПИСАНИЕ ПОЛУЧЕНО.\_\n\n{get_next(base_queue, BASE_PRESCRIPTIONS)}"
    try:
        if STICKER_ID: 
            await bot.send_sticker(chat_id=CHANNEL_ID, sticker=STICKER_ID)
        await bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode="Markdown")
        waiting_for_execution = True
    except Exception as e: print(f"Error: {e}")

@dp.channel_post(F.text.lower().contains("март"))
async def march_trigger(post: types.Message):
    idx = post.text.lower().find("март")
    text = f"\_ПРЕДПИСАНИЕ ПОЛУЧЕНО.\_\n\n{get_next(simple_queue, SIMPLE_PRESCRIPTIONS)}"
    try:
        params = ReplyParameters(message_id=post.message_id, quote=post.text[idx:idx+4])
        if STICKER_ID: 
            await bot.send_sticker(chat_id=CHANNEL_ID, sticker=STICKER_ID, reply_parameters=params)
        await bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode="Markdown")
    except Exception as e: print(f"Error: {e}")

@dp.channel_post(F.text.lower() == "исполнено")
async def check_execution(post: types.Message):
    global waiting_for_execution
    if waiting_for_execution:
        waiting_for_execution = False
        await post.reply("\_ПОДТВЕРЖДЕНО.\_", parse_mode="Markdown")
        await asyncio.sleep(4 * 3600)
        await send_will()

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    asyncio.create_task(send_will())
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
    
