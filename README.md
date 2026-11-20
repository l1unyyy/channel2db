# channel2db

Экспорт треков из Telegram-канала в SQLite-базу. Без дублей, без рекламы, с возобновлением и полнотекстовым поиском.

## Что делает

- Проходит по постам канала от `start` до `LAST_ID`
- Форвардит каждый пост админу, забирает `audio`, сохраняет в базу
- Отсеивает дубли по `file_unique_id` и по нормализованному ключу `norm`
- Чистит названия от ссылок, `[без рекламы]`, `<unknown>` и т.п.
- Хранит позицию в `channel2db_pos.txt` — при перезапуске продолжает с места остановки
- FTS5-поиск по `title` / `performer` с фолбэком на подстроку

## Требования

- Python 3.10+
- aiogram 3.x

```bash
pip install aiogram
```

## Настройка

В основном скрипте:

```python
TG_TOKEN = "123456:ABC..."      # токен бота от @BotFather
CHANNEL_ID = "-10....7890"   # id канала-источника
ADMIN_ID = "123456789"          # твой user id (куда бот форвардит)
```

Бот должен быть админом канала (или иметь доступ к постам) и ты должен один раз нажать `/start` у бота — иначе он не сможет писать тебе.

## Использование

```bash
# обычный запуск — спросит id последнего поста, продолжит с сохранённой позиции
python main.py

# id последнего поста аргументом
python main.py 12345

# сброс: удалить базу и позицию, начать с нуля
python main.py --reset
```

Пример вывода:

```
Post 100/5000 | Added 87 | dupes 13
Post 200/5000 | Added 176 | dupes 24
Finished : Added 420, dupes skipped 58
```

## Как работает

1. `forward_message(ADMIN_ID, CHANNEL_ID, mid)` — забирает пост в личку админу
2. Из `message.audio` берётся `file_unique_id`, `file_id`, `title`, `performer`
3. `db.add(...)` — `INSERT OR IGNORE` по `uid` / `norm`; вернул `False` → дубль
4. Сообщение удаляется из лички, чтобы не засорять чат
5. Каждые 100 постов — `commit()` и запись позиции в `POS_FILE`
6. `retry()` глотает `TelegramRetryAfter` (ждёт `retry_after`) и сетевые ошибки (экспоненциальный бэкофф до 60 с)

## Файлы

| Файл | Назначение |
|---|---|
| `main.py` | сканер канала, retry, CLI |
| `tracks_db.py` | схема БД, `clean` / `prepare` / `add` / `search` |
| `config.py` | `PROXY` (и любые локальные настройки) |
| `tracks.db` | SQLite-база (создаётся сама) |
| `channel2db_pos.txt` | последний обработанный `msg_id` |

`tracks.db*` и `channel2db_pos.txt` — локальное состояние, в git не коммитятся.

## Схема БД

```sql
tracks(id, uid UNIQUE, norm UNIQUE, file_id, msg_id, title, performer, source)
tracks_fts(title, performer)   -- FTS5, external content
```

`norm` — ключ дедупа: `performer + title` в нижнем регистре, только буквы и цифры. `"Artist - Song (Official)"` и `"artist—song"` дают одинаковый `norm`.
