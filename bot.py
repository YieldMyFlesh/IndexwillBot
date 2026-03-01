import asyncio
import random
import os
from aiogram import Bot, Dispatcher, types, F

API_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
IMAGE_PATH = 'proxy_will.jpg'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

PRESCRIPTIONS = [
    "Сжечь три страницы из книги завтрашнего дня.",
    "В течение часа не произносить слова, содержащие букву 'О'.",
    "Оставить цветок на пороге случайного дома.",
    "Поприветствовать каждого встречного поклоном в 30 градусов.",
    "Написать письмо самому себе из прошлого и оставить в пустой бутылке."
]

waiting_for_execution = False

async def send_will():
    global waiting_for_execution
    text = f"📜 **Предписание Указательного:**\n\n{random.choice(PRESCRIPTIONS)}"
    
    try:
        with open(IMAGE_PATH, 'rb') as photo:
            await bot.send_photo(chat_id=CHANNEL_ID, photo=photo, caption=text, parse_mode="Markdown")
        waiting_for_execution = True
    except Exception as e:
        print(f"Error: {e}")

@dp.channel_post(F.text.lower() == "executed")
async def check_execution(post: types.Message):
    global waiting_for_execution
    
    if waiting_for_execution:
        waiting_for_execution = False
        await post.reply("Предписание выполнено. Воля города удовлетворена")
        
        await asyncio.sleep(4 * 3600)
        await send_will()

async def main():
    if not API_TOKEN or not CHANNEL_ID:
        return
    
    asyncio.create_task(send_will())
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
