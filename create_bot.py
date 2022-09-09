from aiogram import Bot,types
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import logging

logging.basicConfig(level=logging.INFO)

TOKEN = 'token'
DB_URL = 'db_url'
APP_NAME = 'app_name'

bot = Bot(token=TOKEN)#Вводим токен боту
dp = Dispatcher(bot, storage=MemoryStorage())