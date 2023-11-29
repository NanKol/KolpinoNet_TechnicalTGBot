import asyncio
import config

import emoji 
import db
import text
import utils

import time
from datetime import datetime, timedelta


from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram import Bot, Dispatcher,Router, types, F
from aiogram.filters.command import Command, CommandObject
from aiogram.types.bot_command import BotCommand

import keyboards

import logging


conf = config.get_config()
if conf['SETTING']['log_to_file'].lower() == None:
    logging.basicConfig(level=logging.INFO, 
                        filemode="w",
                        filename=conf['SETTING']['log_to_file']) # , filename="FileLog.log"

router = Router()
from_chat = int(conf['BOT']['group_id'])
sending: bool = False



@router.message(Command("start"), F.chat.id == from_chat)
async def cmd_start_bot(message: types.Message):
    """Стандартная команда запуска бота"""
    
    await message.answer(text=text.start)
    await message.delete()


@router.message(Command("help"), F.chat.id == from_chat)
async def cmd_help(message: types.Message):
    """Команда выводит описание доступных команд"""
    
    await message.answer(text=text.help, parse_mode=None)
    await message.delete()
    

@router.message(Command("menu"), F.chat.id == from_chat)
async def cmd_menu(message: types.Message):
    """Команда выводит клавиатура=меню бота"""
    
    await message.answer(text=text.menu, reply_markup=keyboards.kb_menu)
    await message.delete()
    message.chat
    
@router.message(Command("check"), F.chat.id == from_chat)
async def cmd_menu(message: types.Message, command: CommandObject):
    """Команда поиска аварии по ip или id аварии"""
    
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
    
    conn = db.get_connect_mysql()
    cursor = conn.cursor()
    
    if(param_search.lower() == "ip"):
        reque_param = "e.ipaddr='{arg_search}'"
    elif(param_search.upper() == "TID"):
        reque_param = "t.id={arg_search}"
    else:
        await message.answer(text="Неправильный парамент поиска")
        return
    
    cursor.execute(db.search_trouble.format(reque_param = reque_param))
    rows = cursor.fetchall()
    
    if (not rows):
        await message.answer(text="Авария отсутствует")
        return
    
    for row in rows:
        cursor.execute(db.count_fl.format(equipment_id=int(row['eqid'])))
        count_fl = cursor.fetchone()
        cursor.execute(db.count_yl.format(equipment_id=int(row['eqid'])))
        count_yl = cursor.fetchone()

        address = utils.getobjectname(cursor, row['objid'])
        smile = emoji.emojize(":red_circle:")
        time = datetime.now() - datetime.fromtimestamp(row["date_start"]) 
        
        t = text.about_trouble(emoji=smile, trouble_id=row['tid'], 
                               time_start=datetime.fromtimestamp(row["date_start"]).strftime('%Y-%m-%d %H:%M:%S'),
                               time=''.join(str(time).split('.')[0]), 
                               time_end="", adress=address,
                               brand=row['brand'], model=row['model'], ipaddr=row['ipaddr'], 
                               uzel=row["location"],
                               ecomment = row['ecomment'],comment=row['comment'],
                               count_fl = count_fl['fl'],count_yl = count_yl['yl'])
        
        await message.answer(**t.as_kwargs(),
                                        reply_markup=keyboards.trouble_menu(trouble_id=row['tid']))


@router.callback_query(F.data == "Show_Troubles", F.message.chat.id == from_chat)
async def show_troubles(callback: types.CallbackQuery):
    """Функция обрабатывает собитие нажатия кнопки \"Показать аварии\""""
    
    global sending
    
    if(sending):
        await callback.answer("Поиск аварий уже идё")
        return
    sending = True
    
    await callback.answer(text="Поиск аварий...")
    
    try:    
        conn = db.get_connect_mysql()
        cursor = conn.cursor()
        cursor.execute(db.search_troubles)
        rows = cursor.fetchall()
    except:
        sending = False
    
    if(not rows):
        await callback.message.answer(text=text.no_trables)
        return
    
    for row in rows:
        try:
            cursor.execute(db.count_fl.format(equipment_id=int(row['eqid'])))
            count_fl = cursor.fetchone()
            cursor.execute(db.count_yl.format(equipment_id=int(row['eqid'])))
            count_yl = cursor.fetchone()
        except:
            sending = False
        address = utils.getobjectname(cursor, row['objid'])
        smile = emoji.emojize(":red_circle:")
        time = datetime.now() - datetime.fromtimestamp(row["date_start"])  
        
        t = text.about_trouble(emoji=smile, trouble_id=row['tid'], 
                               time_start=datetime.fromtimestamp(row["date_start"]).strftime('%Y-%m-%d %H:%M:%S'),
                               time=''.join(str(time).split('.')[0]), 
                               time_end="", adress=address,
                               brand=row['brand'], model=row['model'], ipaddr=row['ipaddr'], 
                               uzel=row["location"],
                               ecomment = row['ecomment'],comment=row['comment'],
                               count_fl = count_fl['fl'],count_yl = count_yl['yl'])
        
        await callback.message.answer(**t.as_kwargs(),
                                        reply_markup=keyboards.trouble_menu(trouble_id=row['tid']))
        await asyncio.sleep(1)
    
    sending = False
    await callback.message.delete()  
    
    
@router.callback_query(F.data == "Count_Troubles", F.message.chat.id == from_chat)
async def count_troubles(callback: types.CallbackQuery):
    """Функция обрабатывает собитие нажатия кнопки \"Итог по авариям\""""
    
    await callback.answer(text="Подсчёт аварий")
    
    conn = db.get_connect_mysql()
    cursor = conn.cursor()
    cursor.execute(db.count_troubles)
    row = cursor.fetchone()
    
    await callback.message.answer(text=text.count_trables.format(count_trable=row['count_trouble']),
                                      reply_markup=keyboards.count_trables_menu)
            

@router.callback_query(F.data == "Update_Count_Trouble", F.message.chat.id == from_chat)
async def Update_Count_Trouble(callback: types.CallbackQuery):
    """Функция обрабатывает собитие нажатия кнопки \"Обновить\""""
    
    con = db.get_connect_mysql()
    cursor = con.cursor()
    cursor.execute(db.count_troubles)
    
    row = cursor.fetchone()
    result_text = text.count_trables.format(count_trable=row['ct'])
    if callback.message.text == result_text:
        await callback.message.edit_text(text=result_text,
                                         reply_markup=keyboards.count_trables_menu)
    

@router.callback_query(F.data.startswith("Update_Trouble:"), F.message.chat.id == from_chat)
async def Update_Trouble(callback: types.CallbackQuery):
    """Функция обрабатывает собитие нажатия кнопки \"Проверить аварию\""""
    await callback.answer("Обновляю информацию...")
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
        
        time_end = ""
        address = utils.getobjectname(cursor, row['objid'])
        
        if row['date_end'] <= 0:
            smile = emoji.emojize(":red_circle:")
            time = datetime.now() - datetime.fromtimestamp(row["date_start"])
        else:
            time = datetime.fromtimestamp(row["date_end"]) - datetime.fromtimestamp(row["date_start"])
            time_end = str(datetime.fromtimestamp(row['date_end'])) + "\n"
            smile = emoji.emojize(":green_circle:")
            
        t = text.about_trouble(emoji=smile, trouble_id=row['tid'], 
                               time_start=datetime.fromtimestamp(row["date_start"]).strftime('%Y-%m-%d %H:%M:%S'),
                               time=''.join(str(time).split('.')[0]), 
                               time_end=time_end, adress=address,
                               brand=row['brand'], model=row['model'], ipaddr=row['ipaddr'], 
                               uzel=row["location"],
                               ecomment = row['ecomment'],comment=row['comment'],
                               count_fl = count_fl['fl'],count_yl = count_yl['yl'])
        
        await callback.message.edit_text(**t.as_kwargs(),
                                        reply_markup=keyboards.trouble_menu(trouble_id=row['tid']))
        

@router.callback_query(F.data =="Delete_Message", F.message.chat.id == from_chat)
async def delete_message(callback: types.CallbackQuery):
    """Функция обрабатывает собитие нажатия кнопки \"Удалить сообщение\""""
    
    await callback.message.delete()
    
    

async def background_cheking_troubles(bot: Bot):
    """Фоновая функция поиск новых аварий"""

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
        
        time_end = ""
        address = utils.getobjectname(cursor, row['objid'])
        
        if row['date_end'] <= 0:
            smile = emoji.emojize(":red_circle:")
            time = datetime.now() - datetime.fromtimestamp(row["date_start"])
        else:
            time = datetime.fromtimestamp(row["date_end"]) - datetime.fromtimestamp(row["date_start"])
            time_end = str(datetime.fromtimestamp(row['date_end'])) 
            smile = emoji.emojize(":green_circle:")
        
        t = text.about_trouble(emoji=smile, trouble_id=row['tid'], 
                               time_start=datetime.fromtimestamp(row["date_start"]).strftime('%Y-%m-%d %H:%M:%S'),
                               time=''.join(str(time).split('.')[0]), 
                               time_end=time_end, adress=address,
                               brand=row['brand'], model=row['model'], ipaddr=row['ipaddr'], 
                               uzel=row["location"],
                               ecomment = row['ecomment'],comment=row['comment'],
                               count_fl = count_fl['fl'],count_yl = count_yl['yl'])
        
        if(conf['BOT']['channel_trouble_start_id'] != "0" and row['date_end'] <= 0):
            await bot.send_message(chat_id=conf['BOT']['channel_trouble_start_id'],**t.as_kwargs())
            cursor.execute(db.background_search_troubles_confirm.format(trouble_id=row['tid']))
            conn.commit()
            
        if(conf['BOT']['channel_trouble_end_id'] != "0" and row['date_end'] > 0):
            await bot.send_message(chat_id=conf['BOT']['channel_trouble_end_id'],**t.as_kwargs())
            cursor.execute(db.background_search_troubles_confirm.format(trouble_id=row['tid']))
            conn.commit()
            
        await bot.send_message(chat_id=conf['BOT']['group_id'],**t.as_kwargs(),
                                        reply_markup=keyboards.trouble_menu(trouble_id=row['tid']))
        cursor.execute(db.background_search_troubles_confirm.format(trouble_id=row['tid']))

        await asyncio.sleep(1)
        
        cursor.execute(db.background_search_troubles_confirm.format(trouble_id=row['tid']))
        conn.commit()

        
            
async def main():
    bot = Bot(token=conf['BOT']['token'])
    dp = Dispatcher()
    
    dp.include_router(router)
    
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=[BotCommand(command="start", description="Старт бота"),
                               BotCommand(command="help", description="Помощь"),
                               BotCommand(command="menu", description="Вызов меню"),
                               BotCommand(command="check", description="Проверка аварии: \n/check <ip или TID> <XXX.XXX.XXX.XXX или XXX>")])
    
    scheduler = AsyncIOScheduler()
    if int(conf['BOT']['interval_background_check_trouble']) > 0: 
        
        scheduler.add_job(background_cheking_troubles, 'interval', 
                          seconds=int(conf['BOT']['interval_background_check_trouble']),
                          args=bot)
         
    scheduler.start()
    
    await dp.start_polling(bot)


if __name__ == '__main__':
   asyncio.run(main())