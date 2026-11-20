from aiogram.exceptions import (TelegramBadRequest, TelegramForbiddenError,
                                TelegramNetworkError, TelegramRetryAfter,
                                TelegramServerError)
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram import Bot
import config
import sys 
import os
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

