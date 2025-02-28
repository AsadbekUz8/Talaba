import os

try:
    from secrets import BOT_TOKEN  # Mahalliy sinov uchun secrets.py ishlatiladi
except ImportError:
    BOT_TOKEN = os.environ.get("BOT_TOKEN")  # Render’da Environment Variable’dan o‘qiladi

ADMIN_ID = 6564165978
ADMIN_USERNAME = "@Justin_Claberly"
DATABASE_FILE = "teachers.db"
DEFAULT_PHOTO = "https://suret.pics/uploads/posts/2023-09/1695449176_1-2.jpg"