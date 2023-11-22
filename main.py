import asyncio
import config
import db

from datetime import datetime

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram import flags

import pymysql

import text
import keyboards

import logging



logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.TOKEN, parse_mode="HTML")
dp = Dispatcher()



@dp.message(Command("start"))
async def cmd_start_bot(message: types.Message):
    await message.answer(text=text.start)


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(text=text.help)


@dp.message(Command("menu"))
async def cmd_menu(message: types.Message):
    await message.answer(text=text.menu, reply_markup=keyboards.kb_menu)


@dp.callback_query(F.data == "Show_Trables")
@flags.chat_action("typing")
async def Show_Trables(callback: types.CallbackQuery):
    await callback.answer(text="Поиск аварий")
    
    rows = None
    
    with pymysql.connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(db.search_truble)

            rows = cursor.fetchall()
            
    for row in rows:
        await bot.send_message(chat_id=callback.message.chat.id, text = text.about_trable.format(emoji="EMOJI",
                                                        status_trable = "СТАТУС",
                                                        time_start = datetime.datetime.fromtimestamp(int(row["date_start"])).strftime('%Y-%m-%d %H:%M:%S'),
                                                        time = "Продолжительность аварии",
                                                        adress = row["location"],
                                                        uzel = "УЗЕЛ",
                                                        comment = row["ecomment"],
                                                        obect = "ОБЪЕКТ",
                                                        count_fl = "КОЛ-ВО ФЛ",
                                                        count_ul = "КОЛ-ВО ЮЛ"))
    
    
     
@dp.callback_query(F.data == "Result_Trables")
@flags.chat_action("typing")
async def Result_Trables(callback: types.CallbackQuery):
    await callback.answer(text="Поиск аварий")
    await bot.send_message(chat_id=callback.message.chat.id, text=text.result_trable.format(count_trable="КОЛ-ВО АВАРИЙ"))



async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)



if __name__ == '__main__':
   asyncio.run(main())