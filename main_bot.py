from create_bot import dp,TOKEN,APP_NAME,bot
from aiogram.utils import executor
from aiogram.utils.executor import start_webhook
from handlers import casino,banks
import os
import logging


async def on_startup(dispatcher):
    print('Bot online')
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)

async def on_shutdown(dispatcher):
    await bot.delete.webhook()    



casino.register_handler_casino(dp)
banks.register_handler_bank(dp)
#other.register_handlers_other(dp)

WEBHOOK_HOST = f'https://{APP_NAME}.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = os.getenv('PORT', default=8000)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT)

