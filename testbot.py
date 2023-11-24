import asyncio
import config
import db
import sqlite3

from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.types.bot_command import BotCommand

import pymysql

import emoji 
import text
import keyboards

import logging



logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.TOKEN, parse_mode="HTML")
dp = Dispatcher()

@dp.message()
async def echo(message: types.Message):
    await bot.edit_message_text(text="Бот заменил текст поста", chat_id=message.sender_chat.id, message_id=message.forward_from_message_id)
    #await message.edit_text(text="измен")


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