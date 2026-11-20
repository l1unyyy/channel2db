from aiogram.exceptions import (TelegramBadRequest, TelegramForbiddenError,
                                TelegramNetworkError, TelegramRetryAfter,
                                TelegramServerError)
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram import Bot
import config
import sys 
import os
import asyncio
import tracks_db as db
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
LAST_ID = int(args[0]) if args else int(input("Last post id in the channel: "))
start = int(open(POS_FILE).read()) + 1 if os.path.exists(POS_FILE) else 1

async def retry(make_call):
    delay = 3
    while True:
        try:
            return await make_call()
        except TelegramRetryAfter as e:
            print(f"Telegram rate limit, waiting {e.retry_after} sec", flush=True)
            await asyncio.sleep(e.retry_after + 1)
        except (TelegramNetworkError, TelegramServerError, asyncio.TimeoutError):
            print(f"No connection to Telegram, retrying in {delay} sec…", flush=True)
            await asyncio.sleep(delay)
            delay = min(delay * 2, 60)


async def main():
    session = AiohttpSession(proxy=PROXY) if PROXY else AiohttpSession()
    bot = Bot(TG_TOKEN, session=session)
    added = dupes = 0
    done = start - 1                      
    try:
        for mid in range(start, LAST_ID + 1):
            m = None
            try:
                m = await retry(lambda: bot.forward_message(ADMIN_ID, CHANNEL_ID, mid))
            except TelegramBadRequest:
                pass                     
            except TelegramForbiddenError:
                print("Bot can't message the admin: send /start to the bot from the ADMIN_ID account")
                return
            if m:
                a = m.audio
                if a:
                    if db.add(a.file_unique_id, a.file_id, mid, a.title, a.performer):
                        added += 1
                    else:
                        dupes += 1
                try:
                    await retry(lambda: bot.delete_message(ADMIN_ID, m.message_id))
                except TelegramBadRequest:
                    pass
                await asyncio.sleep(0.5)
            done = mid
            if mid % 100 == 0:
                db.commit()
                open(POS_FILE, "w").write(str(done))
                print(f"Post {mid}/{LAST_ID} | Added {added} | dupes {dupes}", flush=True)
        print(f"Finished : Added {added}, dupes skipped {dupes}")
    finally:
        db.commit()                      
        open(POS_FILE, "w").write(str(done))
        await bot.session.close()


asyncio.run(main())