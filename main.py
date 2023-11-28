import asyncio
import config

import emoji 
import db
import text
import utils

import time
from datetime import datetime, timedelta


from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command, CommandObject
from aiogram.types.bot_command import BotCommand

import keyboards

import logging


conf = config.get_config()
logging.basicConfig(level=logging.INFO)
if conf['SETTING']['log_to_file'].lower() == None:
    logging.basicConfig(level=logging.INFO, 
                        filemode="w",
                        filename=conf['SETTING']['log_to_file']) # , filename="FileLog.log"


bot = Bot(token=conf['BOT']['token']) # , parse_mode="HTML"  "6434306263:AAH8JZtJCqSDp0zafl759UyGm5QqFLDvjpU"
dp = Dispatcher()



@dp.message(Command("start"))
async def cmd_start_bot(message: types.Message):
    await message.answer(text=text.start)
    await message.delete()


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(text=text.help, parse_mode=None)
    await message.delete()
    
    
@dp.message(Command("clear"))
async def cmd_clear(message: types.Message):
    
    await message.delete()


@dp.message(Command("menu"))
async def cmd_menu(message: types.Message):
    await message.answer(text=text.menu, reply_markup=keyboards.kb_menu)
    await message.delete()
    
    
@dp.message(Command("check"))
async def cmd_menu(message: types.Message, command: CommandObject):
    if command.args is None:
        await message.answer("Ошибка: не переданы аргументы")
        return
    
    try:
        param_search, arg_search = command.args.split(" ", maxsplit=1)
    except ValueError:
        await message.answer(
            "Ошибка: неправильный формат команды. Пример:\n"
            "/check <ip или TID> <XXX.XXX.XXX.XXX или XXX>\n"
            "Пример: /check ip 172.18.14.225 или /check tid 236211"
        )
        return
    
    con = db.get_connect_sqlite()
    cursor = con.cursor()
    reque_param: str
    
    if(param_search == "ip"):
        reque_param = "e.ipaddr='{arg_search}'"
    elif(param_search == "TID"):
        reque_param = "t.id={arg_search}"
    else:
        await message.answer(text="Неправильный парамент поиска")
        return
    
    cursor.execute(db.search_trouble.format(reque_param = reque_param))
    rows = cursor.fetchall()
    
    if rows:
        await message.answer(text="Авария отсутствует")
        return
    
    for row in rows:
        cursor.execute(db.count_fl.format(equipment_id=row['eqid']))
        count_fl = cursor.fetchone()
        cursor.execute(db.count_yl.format(equipment_id=row['eqid']))
        count_yl = cursor.fetchone()
        
        smile = emoji.emojize(":red_circle:")
        time = datetime.now() - datetime.fromtimestamp(row["date_start"])  
        
        addtess = "адрес"#utils.getobjectname(cursor, row['objid'])
        
        await message.answer(text = text.about_trable.format(emoji=smile,
                                                            trouble_id=row['tid'],
                                                            time_start=datetime.fromtimestamp(
                                                                row["date_start"]).strftime(
                                                                '%Y-%m-%d %H:%M:%S'),
                                                            time=''.join(str(time).split('.')[0]),
                                                            time_end="",
                                                            adress=addtess,
                                                            uzel=row["location"],
                                                            brand=row['brand'], model=row['model'],
                                                            ipaddr=row['ipaddr'],
                                                            ecomment=row['ecomment'],
                                                            comment=row['comment'],
                                                            count_fl=count_fl['fl'],
                                                            count_yl=count_yl['yl']),
                                reply_markup=keyboards.trouble_menu(trouble_id=row['tid']))
    
    await message.delete()


@dp.callback_query(F.data == "Show_Trables")
async def Show_Trables(callback: types.CallbackQuery):
    await callback.answer(text="Поиск аварий...")
    
    conn = db.get_connect_mysql()
    cursor = conn.cursor()
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

        address = utils.getobjectname(cursor, row['objid'])
        
        smile = emoji.emojize(":red_circle:")
        time = datetime.now() - datetime.fromtimestamp(row["date_start"])  
        
        
        await callback.message.answer(text=text.about_trable.format(emoji=smile,
                                            trouble_id=row['tid'],
                                            time_start = datetime.fromtimestamp(row["date_start"]).strftime('%Y-%m-%d %H:%M:%S'),
                                            time = ''.join(str(time).split('.')[0]),
                                            time_end = "",
                                            adress = address,
                                            brand = row['brand'], model = row['model'], ipaddr = row['ipaddr'],
                                            uzel = row["location"],
                                            ecomment = row['ecomment'],
                                            comment=row['comment'],
                                            count_fl = count_fl['fl'],
                                            count_yl = count_yl['yl']),
                                        reply_markup=keyboards.trouble_menu(trouble_id=row['tid']))
        await asyncio.sleep(1)
        
    await callback.message.delete()  
    
    
@dp.callback_query(F.data == "Count_Troubles")
async def Count_Troubles(callback: types.CallbackQuery):
    await callback.answer(text="Поиск аварий")
    
    conn = db.get_connect_mysql()
    cursor = conn.cursor()
    cursor.execute(db.count_troubles)
    row = cursor.fetchone()
    
    await callback.message.answer(text=text.count_trables.format(count_trable=row['count_trouble']),
                                      reply_markup=keyboards.count_trables_menu) 
    
    await callback.message.delete()  
            

@dp.callback_query(F.data == "Update_Count_Trouble")
async def Update_Count_Trouble(callback: types.CallbackQuery):
    con = db.get_connect_mysql()
    cursor = con.cursor()
    cursor.execute(db.count_troubles)
    
    row = cursor.fetchone()
    result_text = text.count_trables.format(count_trable=row['ct'])
    if callback.message.text == result_text:
        await callback.message.edit_text(text=result_text,
                                         reply_markup=keyboards.count_trables_menu)
    

# _-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_
# @dp.callback_query(F.data.startswith("comlite_trouble:"))
# async def comlite_trouble(callback: types.CallbackQuery):
#     trouble_id = callback.data.split(':')[1]
#     con = db.get_connect_sqlite()
#     cursor = con.cursor()
#     date = time.mktime(datetime.now().timetuple())
#     cursor.execute(f"""UPDATE troubles SET date_end={int(date)} WHERE id={trouble_id}""")
#     con.commit()
#     con.close()
# _-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_
        
@dp.callback_query(F.data.startswith("Update_Trouble:"))
async def Update_Trouble(callback: types.CallbackQuery):
    trouble_id = callback.data.split(':')[1]

    conn = db.get_connect_mysql()
    cursor = conn.cursor()
    cursor.execute(db.update_trouble.format(trouble_id=int(trouble_id)))
    rows = cursor.fetchall()
    
    if(not rows):
        await callback.message.answer(text=text.no_trables)
        return
    
    for row in rows:
        cursor.execute(db.count_fl.format(equipment_id=row['eqid']))
        count_fl = cursor.fetchone()
        cursor.execute(db.count_yl.format(equipment_id=row['eqid']))
        count_yl = cursor.fetchone()
        
        time: timedelta
        time_end = ""
        
        if row['date_end'] <= 0:
            smile = emoji.emojize(":red_circle:")
            time = datetime.now() - datetime.fromtimestamp(row["date_start"])
        else:
            time = datetime.fromtimestamp(row["date_end"]) - datetime.fromtimestamp(row["date_start"])
            time_end = f"Время конца: {datetime.fromtimestamp(row['date_end'])}" 
            smile = emoji.emojize(":green_circle:")
            
        uzel = utils.getobjectname(cursor, row['objid'])
        
        await callback.message.edit_text(text = text.about_trable.format(emoji=smile,
                                                                        trouble_id=row['tid'],
                                                                        time_start=datetime.fromtimestamp(
                                                                            row["date_start"]).strftime(
                                                                            '%Y-%m-%d %H:%M:%S'),
                                                                        time=''.join(str(time).split('.')[0]),
                                                                        time_end=time_end,
                                                                        adress=row["location"],
                                                                        comment=row["ecomment"],
                                                                        brand=row['brand'], model=row['model'],
                                                                        ipaddr=row['ipaddr'],
                                                                        uzel=uzel,
                                                                        ecomment=row['ecomment'],
                                                                        count_fl=count_fl['fl'],
                                                                        count_yl=count_yl['yl']),
                                            reply_markup=keyboards.trouble_menu(trouble_id=row['tid']))
    

@dp.callback_query(F.data =="Delete_Message")
async def delete_message(callback: types.CallbackQuery):
    await callback.message.delete()
    
    

async def background_cheking_troubles_start():
    conn = db.get_connect_mysql()
    cursor = conn.cursor()
    cursor.execute(db.background_search_troubles)
    rows = cursor.fetchall()
    
    if(not rows):
        return
    
    for row in rows:
        cursor.execute(db.count_fl.format(equipment_id=int(row['eqid'])))
        count_fl = cursor.fetchone()
        cursor.execute(db.count_yl.format(equipment_id=int(row['eqid'])))
        count_yl = cursor.fetchone()
        
        smile = emoji.emojize(":red_circle:")
        time = datetime.now() - datetime.fromtimestamp(row["date_start"])
        
        
        uzel = utils.getobjectname(cursor, row['objid'])

        await bot.send_message(chat_id=config.ALL_TO_CHAT_ID,
                               text=text.about_trable.format(emoji=smile,
                                            trouble_id=row['tid'],
                                            time_start = datetime.fromtimestamp(row["date_start"]).strftime('%Y-%m-%d %H:%M:%S'),
                                            time = ''.join(str(time).split('.')[0]),
                                            time_end = "",
                                            adress = row["location"],
                                            comment=row["ecomment"],
                                            brand = row['brand'], model = ['model'], ipaddr = ['ipaddr'],
                                            uzel = uzel,
                                            ecomment = row['ecomment'],
                                            count_fl = count_fl['fl'],
                                            count_yl = count_yl['yl']),
                                        reply_markup=keyboards.trouble_menu(trouble_id=row['tid']))
        
        cursor.execute(db.background_search_troubles_confirm.format(trouble_id=row['tid']))
        conn.commit()
                
async def background_cheking_troubles_end():
    con = db.get_connect_mysql()
    cursor = con.cursor()
    cursor.execute(db.background_search_troubles)
    rows = cursor.fetchall()
    
    if(not rows):
        return
    
    for row in rows:
        cursor.execute(db.count_fl.format(equipment_id=int(row['eqid'])))
        count_fl = cursor.fetchone()
        cursor.execute(db.count_yl.format(equipment_id=int(row['eqid'])))
        count_yl = cursor.fetchone()
        
        if row['date_end'] <= 0:
            smile = emoji.emojize(":red_circle:")
            time = datetime.now() - datetime.fromtimestamp(row["date_start"])
        else:
            time = datetime.fromtimestamp(row["date_end"]) - datetime.fromtimestamp(row["date_start"])
            smile = emoji.emojize(":green_circle:")  
        
        uzel = utils.getobjectname(cursor, row['objid'])
        
        await bot.send_message(chat_id=conf['BOT']['channel_trouble_end'],
                               text=text.about_trable.format(emoji=smile,
                                            trouble_id=row['tid'],
                                            time_start = datetime.fromtimestamp(row["date_start"]).strftime('%Y-%m-%d %H:%M:%S'),
                                            time = ''.join(str(time).split('.')[0]),
                                            time_end = "",
                                            adress = row["location"],
                                            comment=row["ecomment"],
                                            brand = row['brand'], model = ['model'], ipaddr = ['ipaddr'],
                                            uzel = uzel,
                                            ecomment = row['ecomment'],
                                            count_fl = count_fl['fl'],
                                            count_yl = count_yl['yl']))
        
        cursor.execute(db.background_search_troubles_confirm.format(trouble_id=row['tid']))
        con.commit()
            
            
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=[BotCommand(command="start", description="Старт бота"),
                               BotCommand(command="help", description="Помощь"),
                               BotCommand(command="menu", description="Вызов меню"),
                               BotCommand(command="check", description="Проверка аварии: \n/check <ip или TID> <XXX.XXX.XXX.XXX или XXX>")])
    
    # scheduler = AsyncIOScheduler()
    # if conf['BOT']['channel_trouble_start'] != "0": 
    #     scheduler.add_job(background_cheking_troubles_start, 'interval', seconds=int(conf['BOT']['channel_trouble_start_interval']))
    # if conf['BOT']['channel_trouble_end'] != "0":
    #     scheduler.add_job(background_cheking_troubles_end, 'interval', seconds=int(conf['BOT']['channel_trouble_end_interval']))
         
    # scheduler.start()
    
    await dp.start_polling(bot)
    


if __name__ == '__main__':
   asyncio.run(main())