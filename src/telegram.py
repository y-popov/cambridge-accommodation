import os
import logging
import requests


def send_tg_message(message: str, bot: str = None):
    bot = bot or os.getenv('BOT_TOKEN')
    params = {'chat_id': os.getenv('CHAT_ID'),
              'parse_mode': 'MarkdownV2',
              'text': message}
    r = requests.get(f'https://api.telegram.org/bot{bot}/sendMessage', params=params)
    if r.status_code != 200:
        logging.error(r.text)
