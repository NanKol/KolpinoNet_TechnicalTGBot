import sys

import traceback

import asyncio
import config
import logging

import text
import emoji
import utils

import db
import aiomysql

from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram import Bot, Dispatcher,Router, types, F
from aiogram.filters.command import Command, CommandObject
from aiogram.types.bot_command import BotCommand

import keyboards



conf = config.get_config()

if conf['SETTING']['log_to_file'].lower() != "none":
    logging.basicConfig(level=logging.INFO,
                        filemode="a",
                        filename=conf['SETTING']['log_to_file']) # , filename="FileLog.log"
else:
    logging.basicConfig(level=logging.INFO)

router = Router()
from_chat = int(conf['BOT']['group_id'])
last_call_time = None
loop = asyncio.get_event_loop()


pool = loop.run_until_complete(db.get_pool_connection())
    

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
    
    if(param_search.lower() == "ip"):
        reque_param = f"e.ipaddr='{arg_search}'"
    elif(param_search.upper() == "TID"):
        reque_param = f"t.id={arg_search}"
    else:
        await message.answer(text="Неправильный парамент поиска")
        return
    
    try: 
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor: 
                await cursor.execute(db.search_trouble.format(reque_param = reque_param))
                rows = await cursor.fetchall()
    except aiomysql.MySQLError as e:
        logging.critical(f"Ошибка подключения к БД mysql: {e}")
        return
    
    
    if (not rows):
        await message.answer(text="Авария отсутствует")
        return
    
    for row in rows:
        try:
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor: 
                    await cursor.execute(db.count_fl, (int(row['eqid'])))
                    count_fl = await cursor.fetchone()
                    await cursor.execute(db.count_yl, (int(row['eqid'])))
                    count_yl = await cursor.fetchone()
                    
                    address = await utils.getobjectname(cursor, row['objid'])
        except aiomysql.MySQLError as e:
            logging.critical(f"Ошибка подключения к БД mysql: {e}")
            return

        smile = emoji.emojize(":red_circle:")
        time = datetime.now() - datetime.fromtimestamp(row['date_start'])  
        
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

#-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_
@router.callback_query(F.data == "Show_Troubles", F.message.chat.id == from_chat)
async def show_troubles(callback: types.CallbackQuery):
    """Функция обрабатывает собитие нажатия кнопки \"Показать аварии\""""
    
    global last_call_time
    
    current_time = datetime.now()
    
    if last_call_time is not None:
        time_difference = current_time - last_call_time
        if time_difference.total_seconds() <= 10:
            await callback.answer(text="Поиск аварий возможен раз в 10 сек")
            return
    
    last_call_time = current_time
    await callback.answer(text="Поиск аварий...")
    
    try: 
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor: 
                await cursor.execute(db.search_troubles)
                rows = await cursor.fetchall()
    except aiomysql.MySQLError as e:
        logging.critical(f"Ошибка подключения к БД mysql: {e}")
        return
    
    if(not rows):
        await callback.message.answer(text=text.no_trables, reply_markup=keyboards.delete)
        return
    
    for row in rows:
        try:
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor: 
                    await cursor.execute(db.count_fl, (int(row['eqid'])))
                    count_fl = await cursor.fetchone()
                    await cursor.execute(db.count_yl, (int(row['eqid'])))
                    count_yl = await cursor.fetchone()
                    
                    address = await utils.getobjectname(cursor, row['objid'])
        except aiomysql.MySQLError as e:
            logging.critical(f"Ошибка подключения к БД mysql: {e}")
            return
            
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
    
    await callback.message.delete()
    
    
@router.callback_query(F.data == "Count_Troubles", F.message.chat.id == from_chat)
async def count_troubles(callback: types.CallbackQuery):
    """Функция обрабатывает собитие нажатия кнопки \"Итог по авариям\""""
    
    await callback.answer(text="Подсчёт аварий")
    
    try:
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(db.count_troubles)
                row = await cursor.fetchone()
    except aiomysql.MySQLError as e:
        logging.critical(f"Ошибка подключения к БД mysql: {e}")
        return
        
    await callback.message.answer(text=text.count_trables.format(count_trable=row['ct']),
                                      reply_markup=keyboards.count_trables_menu)
            

@router.callback_query(F.data == "Update_Count_Trouble", F.message.chat.id == from_chat)
async def Update_Count_Trouble(callback: types.CallbackQuery):
    """Функция обрабатывает собитие нажатия кнопки \"Обновить\""""
    
    await callback.answer(text="Обновление кол-ва аварий")
    
    try:
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(db.count_troubles)
                row = await cursor.fetchone()
    except aiomysql.MySQLError as e:
        logging.critical(f"Ошибка подключения к БД mysql: {e}")
        return
    
    result_text = text.count_trables.format(count_trable=row['ct'])
    if callback.message.text != result_text:
        await callback.message.edit_text(text=result_text,
                                         reply_markup=keyboards.count_trables_menu)
    

@router.callback_query(F.data.startswith("Update_Trouble:"), F.message.chat.id == from_chat)
async def Update_Trouble(callback: types.CallbackQuery):
    """Функция обрабатывает собитие нажатия кнопки \"Проверить аварию\""""
    
    await callback.answer("Обновляю информацию...")
    trouble_id = callback.data.split(':')[1]

    try: 
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor: 
                await cursor.execute(db.update_trouble, (trouble_id))
                rows = await cursor.fetchall()
    except aiomysql.MySQLError as e:
        logging.critical(f"Ошибка подключения к БД mysql: {e}")
        return

    for row in rows:
        try:
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor: 
                    await cursor.execute(db.count_fl, (int(row['eqid'])))
                    count_fl = await cursor.fetchone()
                    await cursor.execute(db.count_yl, (int(row['eqid'])))
                    count_yl = await cursor.fetchone()
                    address = await utils.getobjectname(cursor, row['objid'])
        except aiomysql.MySQLErrorError as e:
            logging.critical(f"Ошибка подключения к БД mysql: {e}")
            return
        
        time_end = ""
        
        
        if row['date_end'] <= 0:
            smile = emoji.emojize(":red_circle:")
            time = datetime.now() - datetime.fromtimestamp(row["date_start"])
        else:
            time = datetime.fromtimestamp(row["date_end"]) - datetime.fromtimestamp(row["date_start"])
            time_end = str(datetime.fromtimestamp(row['date_end'])) + "\n"
            smile = emoji.emojize(":green_circle:")
            
        comment = row['comment'] if str(row['comment']).find("\n") == -1 else row['comment'][str(row['comment']).find("\n")+1:]
        t = text.about_trouble(emoji=smile, trouble_id=row['tid'], 
                               time_start=datetime.fromtimestamp(row["date_start"]).strftime('%Y-%m-%d %H:%M:%S'),
                               time=''.join(str(time).split('.')[0]), 
                               time_end=time_end, adress=address,
                               brand=row['brand'], model=row['model'], ipaddr=row['ipaddr'], 
                               uzel=row['location'],
                               ecomment = row['ecomment'],
                               comment=comment,
                               count_fl = count_fl['fl'],count_yl = count_yl['yl'])
        
        await callback.message.edit_text(**t.as_kwargs(),
                                        reply_markup=keyboards.trouble_menu(trouble_id=row['tid']))

@router.callback_query(F.data =="Delete_Message", F.message.chat.id == from_chat)
async def delete_message(callback: types.CallbackQuery):
    """Функция обрабатывает собитие нажатия кнопки \"Удалить сообщение\""""
    
    await callback.message.delete()

@router.shutdown()
async def bot_off():
    """Функция обрабатывающая отключение бота и закрывает пул соединений"""
    logging.info("Закрытие пула соединений...")
    pool.close()
    logging.info("БОТ ВЫКЛЮЧЕН или перезагружается")
    logging.info("Соединения закрыты!")
    await pool.wait_closed()
    
        

async def background_cheking_troubles(bot: Bot):
    """Фоновая функция поиск новых аварий"""

    try: 
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor: 
                await cursor.execute(db.background_search_troubles)
                rows = await cursor.fetchall()
    except aiomysql.MySQLError as e:
        logging.critical(f"Error connecting to MySQL: {e}")
        return
    
    if(not rows):
        return
        
    for row in rows:
        try:
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor: 
                    await cursor.execute(db.count_fl, (int(row['eqid'])))
                    count_fl = await cursor.fetchone()
                    await cursor.execute(db.count_yl, (int(row['eqid'])))
                    count_yl = await cursor.fetchone()
                    
                    address = await utils.getobjectname(cursor, row['objid'])
        except aiomysql.MySQLError  as e:
            logging.critical(f"Ошибка соединения с MySQL: {e}")
            return
        
        smile = emoji.emojize(":red_circle:")
        time = datetime.now() - datetime.fromtimestamp(row["date_start"])
        
        time_end = ""
        
        
        if row['date_end'] <= 0:
            smile = emoji.emojize(":red_circle:")
            time = datetime.now() - datetime.fromtimestamp(row["date_start"])
        else:
            time = datetime.fromtimestamp(row["date_end"]) - datetime.fromtimestamp(row["date_start"])
            time_end = str(datetime.fromtimestamp(row['date_end'])) + "\n"
            smile = emoji.emojize(":green_circle:")
        
        comment = row['comment'] if str(row['comment']).find("\n") == -1 else row['comment'][str(row['comment']).find("\n")+1:]
        t = text.about_trouble(emoji=smile, trouble_id=row['tid'], 
                               time_start=datetime.fromtimestamp(row["date_start"]).strftime('%Y-%m-%d %H:%M:%S'),
                               time=''.join(str(time).split('.')[0]), 
                               time_end=time_end, adress=address,
                               brand=row['brand'], model=row['model'], ipaddr=row['ipaddr'], 
                               uzel=row['location'],
                               ecomment = row['ecomment'],
                               comment=comment,
                               count_fl = count_fl['fl'],count_yl = count_yl['yl'])

        
        if(conf['BOT']['channel_trouble_start_id'] != "0" and row['date_end'] <= 0):
            await bot.send_message(chat_id=conf['BOT']['channel_trouble_start_id'],**t.as_kwargs())
            
        if(conf['BOT']['channel_trouble_end_id'] != "0" and row['date_end'] > 0):
            await bot.send_message(chat_id=conf['BOT']['channel_trouble_end_id'],**t.as_kwargs())
            
        await bot.send_message(chat_id=conf['BOT']['group_id'],**t.as_kwargs(),
                                        reply_markup=keyboards.trouble_menu(trouble_id=row['tid']))
        
        try:
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    pass 
                    await cursor.execute(db.background_search_troubles_confirm, (int(row['tid'])))
        except aiomysql.MySQLError as e:
            logging.critical(f"Ошибка соединения с MySQL: {e}")
            return
        
        await asyncio.sleep(1)

        
            
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
                          args=(bot, ))
    scheduler.start()
    logging.getLogger("apscheduler").setLevel(logging.WARNING)
    
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        loop.run_until_complete(main())
    except aiomysql.MySQLError  as e:
        logging.critical(f"Ошибка соединения с MySQL: {e}")
        pool.close()
    except:
        pool.close()