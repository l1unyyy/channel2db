from aiogram.exceptions import (TelegramBadRequest, TelegramForbiddenError,
                                TelegramNetworkError, TelegramRetryAfter,
                                TelegramServerError)
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram import Bot
import config
import sys 
import os
import asyncio
#============================================================================
# Your Bot Token, Channel Id, Admin Id
#============================================================================
TG_TOKEN = "" 
CHANNEL_ID = "" 
ADMIN_ID = ""
PROXY = getattr(config, "PROXY", None)
POS_FILE = "channel2db_pos.txt"

# rebuild the database
if "--reset" in sys.argv:
    if input("Delete DB? [y/N] ") != "y":
        sys.exit(0)

    for f in ("tracks.db", "tracks.db-wal", "tracks.db-shm", POS_FILE):
        if os.path.exists(f):
            os.remove(f)

args = [a for a in sys.argv[1:] if a.isdigit()]
LAST_ID = int(args[0]) if args else int(input("id последнего поста в канале : "))
start = int(open(POS_FILE).read()) + 1 if os.path.exists(POS_FILE) else 1

async def retry(make_call):
    delay = 3
    while True:
        try:
            return await make_call()
        except TelegramRetryAfter as e:
            print(f"Лимит Телеграма, жду {e.retry_after} сек", flush=True)
            await asyncio.sleep(e.retry_after + 1)
        except (TelegramNetworkError, TelegramServerError, asyncio.TimeoutError):
            print(f"Нет связи с Телеграмом, повтор через {delay} сек…", flush=True)
            await asyncio.sleep(delay)
            delay = min(delay * 2, 60)