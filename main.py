from aiogram.exceptions import (TelegramBadRequest, TelegramForbiddenError,
                                TelegramNetworkError, TelegramRetryAfter,
                                TelegramServerError)
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram import Bot
import config


#============================================================================
# Your Bot Token, Channel Id, Admin Id
#============================================================================
TG_TOKEN = "" 
CHANNEL_ID = "" 
ADMIN_ID = ""
PROXY = getattr(config, "PROXY", None)

