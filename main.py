import asyncio
import config
import db

from datetime import datetime, timedelta

import sqlite3
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.types.bot_command import BotCommand

import emoji 
import text
import keyboards

import logging



logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.TOKEN, parse_mode="HTML")
dp = Dispatcher()



@dp.message(Command("start"))
async def cmd_start_bot(message: types.Message):
    await message.answer(text=text.start)
    await message.delete()


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(text=text.help)
    await message.delete()


@dp.message(Command("menu"))
async def cmd_menu(message: types.Message):
    await message.answer(text=text.menu, reply_markup=keyboards.kb_menu)
    await message.delete()


@dp.callback_query(F.data == "Show_Trables")
async def Show_Trables(callback: types.CallbackQuery):
    await callback.answer(text="Поиск аварий...")
    
    con = sqlite3.connect("Test.db")
    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    cursor.execute(db.search_troubles)
    rows = cursor.fetchall()
    
    if(not rows):
        await callback.message.answer(text=text.no_trables)
        return
    
    for row in rows:
        cursor.execute(db.count_fl.format(equipment_id=int(row['eqid'])))
        count_fl = cursor.fetchone()
        cursor.execute(db.count_yl.format(equipment_id=int(row['eqid'])))
        count_yl = cursor.fetchone()
        
        if row['date_end'] <= 0:
            smile = emoji.emojize(":red_circle:")
        else:
            smile = emoji.emojize(":green_circle:")
        time = datetime.now() - datetime.fromtimestamp(row["date_start"])
        # time = 
        await callback.message.answer(text=text.about_trable.format(emoji=smile,
                                            trouble_id=row['tid'],
                                            time_start = datetime.fromtimestamp(row["date_start"]).strftime('%Y-%m-%d %H:%M:%S'),
                                            time = ':'.join(str(time).split(':')[:2]),
                                            time_end = "",
                                            adress = row["location"],
                                                                    comment=row["ecomment"],
                                                                    brand = row['brand'], model = ['model'], ipaddr = ['ipaddr'],
                                            uzel = "ОНО СУЩЕСТВУЕТ, но это не точно",
                                                                    ecomment = row['ecomment'],
                                            count_fl = count_fl['fl'],
                                            count_yl = count_yl['yl']),
                                        reply_markup=keyboards.trouble_menu(trouble_id=row['tid']))
    
    
@dp.callback_query(F.data == "Result_Trables")
async def Result_Trables(callback: types.CallbackQuery):
    await callback.answer(text="Поиск аварий")
    
    with sqlite3.connect("Test.db") as connection:
        connection.row_factory = sqlite3.Row
        with connection.cursor() as cursor: 
            cursor.execute(db.search_truble)
            row = cursor.fetchone()
            
            await callback.message.answer(text=text.result_trable.format(count_trable=row['ct']))   
            
            
@dp.callback_query(F.data.startswich("Update_Trouble:"))
async def Update_Trouble(callback: types.CallbackQuery):
    trouble_id = callback.data.split(':')[1]

    with sqlite3.connect("Test.db") as connection:
        connection.row_factory = sqlite3.Row
        with connection.cursor() as cursor:
            cursor.execute(db.update_trouble.format(truble_id=trouble_id))
            rows = cursor.fetchall()
            
            if(not rows):
                await callback.message.answer(text=text.no_trables)
                return
            
            for row in rows:
                cursor.execute(db.count_fl.format(equipment_id=row['eqid']))
                count_fl = cursor.fetchone()
                cursor.execute(db.count_yl.format(equipment_id=row['eqid']))
                count_yl = cursor.fetchone()
                
                if row['date_end'] <= 0:
                    smile = emoji.emojize(":red_circle:")
                else:
                    smile = emoji.emojize(":green_circle:")

            time = datetime.now() - datetime.fromtimestamp(row["date_start"])

            for row in rows:
                await callback.message.edit_text(text = text.about_trable.format(emoji=smile,
                                                                                 trouble_id=row['tid'],
                                                                                 time_start=datetime.fromtimestamp(
                                                                                     row["date_start"]).strftime(
                                                                                     '%Y-%m-%d %H:%M:%S'),
                                                                                 time=':'.join(str(time).split(':')[:2]),
                                                                                 time_end="",
                                                                                 adress=row["location"],
                                                                                 comment=row["ecomment"],
                                                                                 brand=row['brand'], model=row['model'],
                                                                                 ipaddr=row['ipaddr'],
                                                                                 uzel="ОНО СУЩЕСТВУЕТ, но это не точно",
                                                                                 ecomment=row['ecomment'],
                                                                                 count_fl=count_fl['fl'],
                                                                                 count_yl=count_yl['yl']),
                                                 reply_markup=keyboards.trouble_menu(trouble_id=row['tid']))
    
@dp.callback_query()
async def call_echo(callback: types.CallbackQuery):
    callback.answer(text=callback.data)
    callback.message.answer(text=callback.data)

@dp.callback_query(F.data =="Delete_Message")
async def delete_message(callback: types.CallbackQuery):
    await callback.message.delete()
    
@dp.message()
async def info_id(message: types.Message, chat: types.Chat):
    await message.answer(text=f"user_id: {message.from_user.id}\nid_chat:{chat.id}")
# async def background_cheking_troubles():
#     connection = db.get_connct_sqllite()
#     with connection.cursor() as cursor:
#         cursor.execute(db.background_search_troubles)
#         rows = cursor.fetchall()
        
#         if(not row):
#             await bot.message.answer(text=text.no_trables)
#             return
        
#         for row in rows:
#             cursor.execute(db.count_fl.format(equipment_id=row['eqid']))
#             count_fl = cursor.fetchone()
#             cursor.execute(db.count_yl.format(equipment_id=row['eqid']))
#             count_yl = cursor.fetchone()
            
#             if row['date_end'] <= 0:
#                 smile = emoji.emojize(":red_circle:")
#             else:
#                 smile = emoji.emojize(":green_circle:")
        
#         for row in rows:
#             await bot.send_message(chat_id=,text = text.about_trable.format(emoji=smile,
#                                                 time_start = datetime.fromtimestamp(int(row["date_start"])).strftime('%Y-%m-%d %H:%M:%S'),
#                                                 time = (datetime.now() - datetime.fromtimestamp(int(row["date_start"]))).time(),
#                                                 time_end = f"Время конца:{datetime.fromtimestamp(int(row['date_end'])).strftime('%Y-%m-%d %H:%M:%S')}",
#                                                 adress = row["location"],
#                                                 uzel = "ОНО СУЩЕСТВУЕТ, но это не точно",
#                                                 comment = row["ecomment"],
#                                                 count_fl = count_fl['fl'],
#                                                 count_ul = count_yl['yl']),
#                                                 reply_markup=keyboards.trouble_menu())
#             cursor.execute(db.background_search_troubles_confirm.format(trouble_id=row['tid']))
#             connection.commit()
                
            
            
            

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