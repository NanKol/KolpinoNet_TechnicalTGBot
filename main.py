import asyncio
import config
import db
import sqlite3

from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.types.bot_command import BotCommand

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
async def Show_Trables(callback: types.CallbackQuery):
    await callback.answer(text="Поиск аварий...")
    # con = sqlite3.connect("test.db")
    # con.row_factory = sqlite3.Row
    # cur = con.cursor()
    # 
    # await callback.message.answer(text="Перед циклом")
    # rows = cur.execute("""<ЗАПРОС>""").fetchall()
    # print(rows)
    # for row in rows:
    #     await callback.message.answer(text=f"""Авария
    #                            Примечание: {row['comment']}
    #                            Начало: {row['date_start']}
    #                            Оборудование: {row['brand']} {row['model']} [{row['ipaddr']}]
    #                            Коментарий: {row['brand']}""")

    with pymysql.connect() as connection:
        with connection.cursor() as cursor:
            
            cursor.execute(db.search_troubles)
            rows = cursor.fetchall()
            
            cursor.execute(db.count_fl)
            count_fl = cursor.fetchone()
            cursor.execute(db.count_yl)
            count_yl = cursor.fetchone()
            
            for row in rows:
                await callback.message.answer(text = text.about_trable.format(emoji="EMOJI",
                                                    time_start = datetime.datetime.fromtimestamp(int(row["date_start"])).strftime('%Y-%m-%d %H:%M:%S'),
                                                    time = "Продолжительность аварии",
                                                    adress = row["location"],
                                                    uzel = "УЗЕЛ",
                                                    comment = row["ecomment"],
                                                    obect = "ОБЪЕКТ",
                                                    count_fl = count_fl['fl'],
                                                    count_ul = count_fl['yl']),
                                              reply_markup=keyboards.check_trouble())
                return
    await callback.message.answer(text=text.no_trables)
    
    
@dp.callback_query(F.data == "Result_Trables")
async def Result_Trables(callback: types.CallbackQuery):
    await callback.answer(text="Поиск аварий")
    with pymysql.connect() as connection:
        with connection.cursor() as cursor:
            
            cursor.execute(db.search_truble)
            row = cursor.fetchone()
            
            await callback.message.answer(text=text.result_trable.format(count_trable=row['ct']))
    
# async def background_cheking_troubles():
#     with pymysql.connect() as connection:
#         with connection.cursor() as cursor:
            
#             cursor.execute(db.background_search_troubles)
#             rows = cursor.fetchall()
            
#             for row in rows:
#                 await bot.send_message()
#                 await callback.message.answer(text = text.about_trable.format(emoji="EMOJI",
#                                                                 trouble_id=row['tid']
#                                                                 time_start = datetime.datetime.fromtimestamp(int(row["date_start"])).strftime('%Y-%m-%d %H:%M:%S'),
#                                                                 time = "Продолжительность аварии",
#                                                                 adress = row["location"],
#                                                                 uzel = "УЗЕЛ",
#                                                                 comment = row["ecomment"],
#                                                                 count_fl = "КОЛ-ВО ФЛ",
#                                                                 count_ul = "КОЛ-ВО ЮЛ"))
#                 cursor.execute(db.background_search_troubles_confirm.format(trouble_id=row['tid']))
#                 connection.commit()
                
            
            
            

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    # await bot(set_my_commands([BotCommand("start", "Старт бота"),
    #                            BotCommand("help", "Помощь"),
    #                            BotCommand("check", "В разработке")]))
    await dp.start_polling(bot)
    
    # scheduler = AsyncIOScheduler()
    # scheduler.add_job(background_cheking_troubles, 'interval', seconds=5)
    # scheduler.start()


if __name__ == '__main__':
   asyncio.run(main())