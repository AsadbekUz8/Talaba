import telegram
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler
from telegram.ext import filters
from database import add_teacher_pending, get_teachers, get_teachers_by_subject, get_top_teachers, init_db, add_user, get_all_users, has_added_teacher, mark_teacher_added, add_message, add_rating
from utils import format_teacher_info, format_teacher_info_admin
from admin import setup_admin
from config import BOT_TOKEN, ADMIN_ID, ADMIN_USERNAME, DEFAULT_PHOTO

# Holatlar (ConversationHandler uchun)
CONTACT, GENDER, ERKAK_NAME, ERKAK_SUBJECT, ERKAK_EXPERIENCE, ERKAK_PRICE, ERKAK_LOCATION, ERKAK_PHOTO, ERKAK_BIO, \
AYOL_NAME, AYOL_SUBJECT, AYOL_EXPERIENCE, AYOL_PRICE, AYOL_LOCATION, AYOL_PHOTO, AYOL_BIO, SEARCH_SUBJECT, SEARCH_SELECT, \
TOP_SELECT, CHAT_TEACHER, CHAT_MESSAGE, RATE_TEACHER, RATE_VALUE = range(23)

# Asosiy menyudagi knopkalar (emojilar bilan)
MAIN_MENU = ReplyKeyboardMarkup(
    [["📝 O'qituvchi sifatida ro'yxatdan o'tish", "🔍 Qidiruv"],
     ["🏆 Top o'qituvchilar", "⭐ Reyting"],
     ["💬 Bog‘lanish"]],
    resize_keyboard=True
)

# Jins tanlash menyusi (emojilar bilan)
GENDER_MENU = ReplyKeyboardMarkup(
    [["👨 Erkak o'qituvchi", "👩 Ayol o'qituvchi"],
     ["❌ Bekor qilish"]],
    resize_keyboard=True
)

# Qidiruv menyusi (baho berish qo‘shildi)
SEARCH_MENU = ReplyKeyboardMarkup(
    [["⭐ Baho berish"],
     ["❌ Bekor qilish"]],
    resize_keyboard=True
)

# Bekor qilish knopkasi bilan menyular (emojilar bilan)
REG_MENU = ReplyKeyboardMarkup([["❌ Bekor qilish"]], resize_keyboard=True)
TOP_MENU = ReplyKeyboardMarkup([["❌ Bekor qilish"]], resize_keyboard=True)

# Chet el davlatlarining qisqa ro'yxati (filtr uchun)
FOREIGN_COUNTRIES = ["USA", "Russia", "Germany", "France", "Japan", "China", "India", "UK", "Canada", "Australia", 
                     "Dubai", "Turkey", "Korea", "Spain", "Italy", "England", "America", "Moscow", "London"]

async def start(update: Update, context):
    """Botni ishga tushirish va kontaktni so'rash."""
    user_id = update.message.from_user.id
    if 'contact' not in context.user_data:
        await update.message.reply_text(
            "*🎉 Botga xush kelibsiz, bilim olish vaqti keldi!*\n*📱 Kontakt yuboring:*",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("📞 Kontakt yuboring", request_contact=True)]],
                resize_keyboard=True, one_time_keyboard=True
            ),
            parse_mode='Markdown'
        )
        return CONTACT
    else:
        await update.message.reply_text(
            "*👋 Salom! Quyidagi bo'limlardan birini tanlang:*",
            reply_markup=MAIN_MENU,
            parse_mode='Markdown'
        )
    return ConversationHandler.END

async def contact(update: Update, context):
    """Kontaktni qabul qilish va menyuni ko'rsatish."""
    if not update.message.contact:
        await update.message.reply_text(
            "*📱 Iltimos, kontakt yuboring, bizga sizni topish kerak!*",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("📞 Kontakt yuboring", request_contact=True)]],
                resize_keyboard=True, one_time_keyboard=True
            ),
            parse_mode='Markdown'
        )
        return CONTACT
    user_id = update.message.from_user.id
    contact = update.message.contact.phone_number
    context.user_data['contact'] = contact
    add_user(user_id, contact)
    await update.message.reply_text(
        "*✅ Zo'r! Endi bo'limlardan birini tanlang:*",
        reply_markup=MAIN_MENU,
        parse_mode='Markdown'
    )
    return ConversationHandler.END

async def register_handler(update: Update, context):
    """O'qituvchi ro'yxatdan o'tish jarayonini boshlash."""
    user_id = update.message.from_user.id
    if 'contact' not in context.user_data:
        await update.message.reply_text(
            "*❌ Kontaktni avval yuborishingiz kerak! /start bilan boshlang!*",
            reply_markup=MAIN_MENU,
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    if user_id != ADMIN_ID and has_added_teacher(user_id):
        await update.message.reply_text(
            f"*❌ Siz bir martalik imkoniyatni ishlatdingiz!*\n*📩 Adminga yozing: {ADMIN_USERNAME}*",
            reply_markup=MAIN_MENU,
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    
    await update.message.reply_text(
        "*📝 Repetitorlik qilmoqchimisiz? Qo'shiling!*\n*⚠️ Bu bir martalik imkoniyat!*\n*👥 Jinsingizni tanlang:*",
        reply_markup=GENDER_MENU,
        parse_mode='Markdown'
    )
    return GENDER

async def gender(update: Update, context):
    """Jinsni tanlash."""
    choice = update.message.text
    if choice == "❌ Bekor qilish":
        await update.message.reply_text(
            "*❌ Bekor qilindi! Bosh menyuga qaytdik:*",
            reply_markup=MAIN_MENU,
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    elif choice == "👨 Erkak o'qituvchi":
        context.user_data['gender'] = "Erkak"
        await update.message.reply_text(
            "*📝 Ismingizni yozing:*",
            reply_markup=REG_MENU,
            parse_mode='Markdown'
        )
        return ERKAK_NAME
    elif choice == "👩 Ayol o'qituvchi":
        context.user_data['gender'] = "Ayol"
        await update.message.reply_text(
            "*📝 Hurmatli o'qituvchi, ismingizni yozing:*",
            reply_markup=REG_MENU,
            parse_mode='Markdown'
        )
        return AYOL_NAME
    else:
        await update.message.reply_text(
            "*❌ Faqat menyudagi tanlovlardan birini bosing:*",
            reply_markup=GENDER_MENU,
            parse_mode='Markdown'
        )
        return GENDER

# Erkak o'qituvchi uchun jarayon
async def erkak_name(update: Update, context):
    if update.message.text == "❌ Bekor qilish":
        await update.message.reply_text(
            "*❌ Bekor qilindi! Bosh menyuga qaytdik:*",
            reply_markup=MAIN_MENU,
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    context.user_data['name'] = update.message.text
    await update.message.reply_text(
        "*📚 Qaysi fanni o'qitasiz?*",
        reply_markup=REG_MENU,
        parse_mode='Markdown'
    )
    return ERKAK_SUBJECT

async def erkak_subject(update: Update, context):
    if update.message.text == "❌ Bekor qilish":
        await update.message.reply_text(
            "*❌ Bekor qilindi! Bosh menyuga qaytdik:*",
            reply_markup=MAIN_MENU,
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    context.user_data['subject'] = update.message.text
    await update.message.reply_text(
        "*⏳ Necha yil tajribangiz bor?*",
        reply_markup=REG_MENU,
        parse_mode='Markdown'
    )
    return ERKAK_EXPERIENCE

async def erkak_experience(update: Update, context):
    if update.message.text == "❌ Bekor qilish":
        await update.message.reply_text(
            "*❌ Bekor qilindi! Bosh menyuga qaytdik:*",
            reply_markup=MAIN_MENU,
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    context.user_data['experience'] = update.message.text
    await update.message.reply_text(
        "*💸 Soatlik narxingiz qancha (so'mda)?*",
        reply_markup=REG_MENU,
        parse_mode='Markdown'
    )
    return ERKAK_PRICE

async def erkak_price(update: Update, context):
    if update.message.text == "❌ Bekor qilish":
        await update.message.reply_text(
            "*❌ Bekor qilindi! Bosh menyuga qaytdik:*",
            reply_markup=MAIN_MENU,
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    context.user_data['price'] = update.message.text
    await update.message.reply_text(
        "*📍 Qaysi joyda yashaysiz? (Faqat O'zbekiston hududini yozing):*",
        reply_markup=REG_MENU,
        parse_mode='Markdown'
    )
    return ERKAK_LOCATION

async def erkak_location(update: Update, context):
    if update.message.text == "❌ Bekor qilish":
        await update.message.reply_text(
            "*❌ Bekor qilindi! Bosh menyuga qaytdik:*",
            reply_markup=MAIN_MENU,
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    location = update.message.text.strip()
    if any(country.lower() in location.lower() for country in FOREIGN_COUNTRIES):
        await update.message.reply_text(
            "*❌ Faqat O'zbekiston hududini yozing! Qaytadan kiriting:*",
            reply_markup=REG_MENU,
            parse_mode='Markdown'
        )
        return ERKAK_LOCATION
    context.user_data['location'] = location
    await update.message.reply_text(
        "*📸 Rasmingizni yuboring (jpg/png, 2 MB dan oshmasin):*",
        reply_markup=REG_MENU,
        parse_mode='Markdown'
    )
    return ERKAK_PHOTO

async def erkak_photo(update: Update, context):
    if update.message.text == "❌ Bekor qilish":
        await update.message.reply_text(
            "*❌ Bekor qilindi! Bosh menyuga qaytdik:*",
            reply_markup=MAIN_MENU,
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    try:
        if not update.message.photo:
            await update.message.reply_text(
                "*📸 Rasmingizni yuboring (jpg/png, 2 MB dan oshmasin)!*",
                reply_markup=REG_MENU,
                parse_mode='Markdown'
            )
            return ERKAK_PHOTO
        photo = update.message.photo[-1]
        file_size = photo.file_size
        if file_size > 2 * 1024 * 1024:
            await update.message.reply_text(
                "*⚠️ Rasm 2 MB dan oshdi! Kichikroq rasm yuboring:*",
                reply_markup=REG_MENU,
                parse_mode='Markdown'
            )
            return ERKAK_PHOTO
        photo_file = await photo.get_file()
        context.user_data['photo'] = photo_file.file_id
        await update.message.reply_text(
            "*ℹ️ O'zingiz haqida qisqacha yozing (bio):*",
            reply_markup=REG_MENU,
            parse_mode='Markdown'
        )
        return ERKAK_BIO
    except Exception as e:
        await update.message.reply_text(
            "*❌ Xato! Rasmni qaytadan yuboring:*",
            reply_markup=REG_MENU,
            parse_mode='Markdown'
        )
        print(f"Xato: {e}")
        return ERKAK_PHOTO

async def erkak_bio(update: Update, context):
    user_id = update.message.from_user.id
    if update.message.text == "❌ Bekor qilish":
        await update.message.reply_text(
            "*❌ Bekor qilindi! Bosh menyuga qaytdik:*",
            reply_markup=MAIN_MENU,
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    
    context.user_data['bio'] = update.message.text
    teacher_data = {
        'name': context.user_data['name'],
        'subject': context.user_data['subject'],
        'experience': context.user_data['experience'],
        'price': context.user_data['price'],
        'location': context.user_data['location'],
        'photo': context.user_data['photo'],
        'bio': context.user_data['bio'],
        'user_id': user_id,
        'contact': context.user_data['contact'],
        'gender': context.user_data['gender']
    }
    add_teacher_pending(teacher_data)
    if user_id != ADMIN_ID:
        mark_teacher_added(user_id)
    await update.message.reply_text(
        "*✅ Ma'lumotlaringiz tasdiqlash uchun yuborildi! Admin tasdiqlashini kuting:*",
        reply_markup=MAIN_MENU,
        parse_mode='Markdown'
    )
    
    try:
        await context.bot.send_message(
            ADMIN_ID,
            f"*📢 Yangi o'qituvchi keldi:*\n{format_teacher_info_admin(teacher_data)}\n"
            f"*🚀 Tasdiqlash: /tasdiqlash*\n*❌ Rad etish: /rad_etish*",
            parse_mode='Markdown'
        )
    except telegram.error.BadRequest as e:
        print(f"Admin ID ({ADMIN_ID}) topilmadi: {e}")
    except Exception as e:
        print(f"Xato: {e}")
    
    return ConversationHandler.END

# Ayol o'qituvchi uchun jarayon
async def ayol_name(update: Update, context):
    if update.message.text == "❌ Bekor qilish":
        await update.message.reply_text(
            "*❌ Bekor qilindi! Bosh menyuga qaytdik:*",
            reply_markup=MAIN_MENU,
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    context.user_data['name'] = update.message.text
    await update.message.reply_text(
        "*📚 Qaysi fanni o'qitasiz?*",
        reply_markup=REG_MENU,
        parse_mode='Markdown'
    )
    return AYOL_SUBJECT

async def ayol_subject(update: Update, context):
    if update.message.text == "❌ Bekor qilish":
        await update.message.reply_text(
            "*❌ Bekor qilindi! Bosh menyuga qaytdik:*",
            reply_markup=MAIN_MENU,
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    context.user_data['subject'] = update.message.text
    await update.message.reply_text(
        "*⏳ Necha yillik tajribangiz bor?*",
        reply_markup=REG_MENU,
        parse_mode='Markdown'
    )
    return AYOL_EXPERIENCE

async def ayol_experience(update: Update, context):
    if update.message.text == "❌ Bekor qilish":
        await update.message.reply_text(
            "*❌ Bekor qilindi! Bosh menyuga qaytdik:*",
            reply_markup=MAIN_MENU,
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    context.user_data['experience'] = update.message.text
    await update.message.reply_text(
        "*💸 Soatlik narxingiz qancha (so'mda)?*",
        reply_markup=REG_MENU,
        parse_mode='Markdown'
    )
    return AYOL_PRICE

async def ayol_price(update: Update, context):
    if update.message.text == "❌ Bekor qilish":
        await update.message.reply_text(
            "*❌ Bekor qilindi! Bosh menyuga qaytdik:*",
            reply_markup=MAIN_MENU,
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    context.user_data['price'] = update.message.text
    await update.message.reply_text(
        "*📍 Qaysi joyda yashaysiz? (Faqat O'zbekiston hududini yozing):*",
        reply_markup=REG_MENU,
        parse_mode='Markdown'
    )
    return AYOL_LOCATION

async def ayol_location(update: Update, context):
    if update.message.text == "❌ Bekor qilish":
        await update.message.reply_text(
            "*❌ Bekor qilindi! Bosh menyuga qaytdik:*",
            reply_markup=MAIN_MENU,
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    location = update.message.text.strip()
    if any(country.lower() in location.lower() for country in FOREIGN_COUNTRIES):
        await update.message.reply_text(
            "*❌ Faqat O'zbekiston hududini yozing! Qaytadan kiriting:*",
            reply_markup=REG_MENU,
            parse_mode='Markdown'
        )
        return AYOL_LOCATION
    context.user_data['location'] = location
    await update.message.reply_text(
        "*📸 Rasmingizni yuboring (jpg/png, 2 MB dan oshmasin):*",
        reply_markup=REG_MENU,
        parse_mode='Markdown'
    )
    return AYOL_PHOTO

async def ayol_photo(update: Update, context):
    if update.message.text == "❌ Bekor qilish":
        await update.message.reply_text(
            "*❌ Bekor qilindi! Bosh menyuga qaytdik:*",
            reply_markup=MAIN_MENU,
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    try:
        if not update.message.photo:
            await update.message.reply_text(
                "*📸 Rasmingizni yuboring (jpg/png, 2 MB dan oshmasin)!*",
                reply_markup=REG_MENU,
                parse_mode='Markdown'
            )
            return AYOL_PHOTO
        photo = update.message.photo[-1]
        file_size = photo.file_size
        if file_size > 2 * 1024 * 1024:
            await update.message.reply_text(
                "*⚠️ Rasm 2 MB dan oshdi! Kichikroq rasm yuboring:*",
                reply_markup=REG_MENU,
                parse_mode='Markdown'
            )
            return AYOL_PHOTO
        photo_file = await photo.get_file()
        context.user_data['photo'] = photo_file.file_id
        await update.message.reply_text(
            "*ℹ️ O'zingiz haqida qisqacha yozing (bio):*",
            reply_markup=REG_MENU,
            parse_mode='Markdown'
        )
        return AYOL_BIO
    except Exception as e:
        await update.message.reply_text(
            "*❌ Xato! Rasmni qaytadan yuboring:*",
            reply_markup=REG_MENU,
            parse_mode='Markdown'
        )
        print(f"Xato: {e}")
        return AYOL_PHOTO

async def ayol_bio(update: Update, context):
    user_id = update.message.from_user.id
    if update.message.text == "❌ Bekor qilish":
        await update.message.reply_text(
            "*❌ Bekor qilindi! Bosh menyuga qaytdik:*",
            reply_markup=MAIN_MENU,
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    
    context.user_data['bio'] = update.message.text
    teacher_data = {
        'name': context.user_data['name'],
        'subject': context.user_data['subject'],
        'experience': context.user_data['experience'],
        'price': context.user_data['price'],
        'location': context.user_data['location'],
        'photo': context.user_data['photo'],
        'bio': context.user_data['bio'],
        'user_id': user_id,
        'contact': context.user_data['contact'],
        'gender': context.user_data['gender']
    }
    add_teacher_pending(teacher_data)
    if user_id != ADMIN_ID:
        mark_teacher_added(user_id)
    await update.message.reply_text(
        "*✅ Ma'lumotlaringiz tasdiqlash uchun yuborildi! Admin tasdiqlashini kuting:*",
        reply_markup=MAIN_MENU,
        parse_mode='Markdown'
    )
    
    try:
        await context.bot.send_message(
            ADMIN_ID,
            f"*📢 Yangi o'qituvchi keldi:*\n{format_teacher_info_admin(teacher_data)}\n"
            f"*🚀 Tasdiqlash: /tasdiqlash*\n*❌ Rad etish: /rad_etish*",
            parse_mode='Markdown'
        )
    except telegram.error.BadRequest as e:
        print(f"Admin ID ({ADMIN_ID}) topilmadi: {e}")
    except Exception as e:
        print(f"Xato: {e}")
    
    return ConversationHandler.END

async def search_handler(update: Update, context):
    """Qidiruv jarayonini boshlash."""
    await update.message.reply_text(
        "*🔍 Qaysi fan kerak? Nomini yozing:*",
        reply_markup=SEARCH_MENU,
        parse_mode='Markdown'
    )
    return SEARCH_SUBJECT

async def search_subject(update: Update, context):
    """Foydalanuvchi kiritgan fan bo'yicha o'qituvchilarni qidirish."""
    if update.message.text == "❌ Bekor qilish":
        await update.message.reply_text(
            "*❌ Bekor qilindi! Bosh menyuga qaytdik:*",
            reply_markup=MAIN_MENU,
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    subject = update.message.text.strip()
    teachers = get_teachers_by_subject(subject)
    if not teachers:
        await update.message.reply_text(
            f"*❌ {subject} bo'yicha o'qituvchi topilmadi! Keyinroq qarang:*",
            reply_markup=MAIN_MENU,
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    
    teacher_list = "\n".join([f"*🔢 {i+1}. {teacher['name']} - {teacher['subject']} (⭐ {teacher['avg_rating']:.1f})*" for i, teacher in enumerate(teachers)])
    context.user_data['search_results'] = teachers
    await update.message.reply_text(
        f"*✅ {subject} bo'yicha o'qituvchilar:*\n{teacher_list}\n\n"
        f"*🔍 Batafsil ma'lumot uchun raqamni yuboring (1-{len(teachers)}):*",
        reply_markup=SEARCH_MENU,
        parse_mode='Markdown'
    )
    return SEARCH_SELECT

async def search_select(update: Update, context):
    """Foydalanuvchi tanlagan o'qituvchi haqida ma'lumot ko'rsatish."""
    if update.message.text == "❌ Bekor qilish":
        await update.message.reply_text(
            "*❌ Bekor qilindi! Bosh menyuga qaytdik:*",
            reply_markup=MAIN_MENU,
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    elif update.message.text == "⭐ Baho berish":
        teachers = context.user_data.get('search_results', [])
        if not teachers:
            await update.message.reply_text(
                "*❌ O'qituvchilar topilmadi! Avval qidiruv qiling:*",
                reply_markup=MAIN_MENU,
                parse_mode='Markdown'
            )
            return ConversationHandler.END
        teacher_list = "\n".join([f"*🔢 {i+1}. {t['name']} - {t['subject']}*" for i, t in enumerate(teachers)])
        context.user_data['teachers_to_rate'] = teachers
        await update.message.reply_text(
            f"*⭐ Kimni baholamoqchisiz?*\n{teacher_list}\n\n*Raqamni yuboring (1-{len(teachers)}):*",
            reply_markup=REG_MENU,
            parse_mode='Markdown'
        )
        return RATE_TEACHER
    
    try:
        choice = int(update.message.text) - 1
        teachers = context.user_data['search_results']
        if 0 <= choice < len(teachers):
            teacher = teachers[choice]
            await update.message.reply_photo(
                photo=teacher['photo'],
                caption=f"*{format_teacher_info(teacher)}*\n*⭐ O‘rtacha baho:* {teacher['avg_rating']:.1f}\n\n*💬 Bog‘lanish uchun adminga yozing: {ADMIN_USERNAME}*",
                parse_mode='Markdown'
            )
            await update.message.reply_text(
                "*✅ Tanlagan o'qituvchi ma'lumotlari yuqorida!*",
                reply_markup=SEARCH_MENU,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"*❌ Noto'g'ri raqam! 1-{len(teachers)} oralig'ida tanlang:*",
                reply_markup=SEARCH_MENU,
                parse_mode='Markdown'
            )
            return SEARCH_SELECT
    except ValueError:
        await update.message.reply_text(
            "*❌ Faqat raqam yuboring!*",
            reply_markup=SEARCH_MENU,
            parse_mode='Markdown'
        )
        return SEARCH_SELECT
    
    return SEARCH_SELECT

async def rate_teacher(update: Update, context):
    """O‘qituvchini tanlash uchun."""
    if update.message.text == "❌ Bekor qilish":
        await update.message.reply_text(
            "*❌ Bekor qilindi! Bosh menyuga qaytdik:*",
            reply_markup=MAIN_MENU,
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    
    try:
        choice = int(update.message.text) - 1
        teachers = context.user_data.get('teachers_to_rate', [])
        if not teachers:
            await update.message.reply_text(
                "*❌ O'qituvchilar topilmadi! Qaytadan qidiruvdan boshlang:*",
                reply_markup=MAIN_MENU,
                parse_mode='Markdown'
            )
            return ConversationHandler.END
        if 0 <= choice < len(teachers):
            context.user_data['selected_teacher'] = teachers[choice]
            await update.message.reply_text(
                f"*⭐ {teachers[choice]['name']} ga baho bering:*\n*1-5 gacha raqam yuboring (masalan, 4):*",
                reply_markup=REG_MENU,
                parse_mode='Markdown'
            )
            return RATE_VALUE
        else:
            await update.message.reply_text(
                f"*❌ Noto'g'ri raqam! 1-{len(teachers)} oralig'ida tanlang:*",
                reply_markup=REG_MENU,
                parse_mode='Markdown'
            )
            return RATE_TEACHER
    except ValueError:
        await update.message.reply_text(
            "*❌ Faqat raqam yuboring!*",
            reply_markup=REG_MENU,
            parse_mode='Markdown'
        )
        return RATE_TEACHER

async def rate_value(update: Update, context):
    """Tanlangan o‘qituvchiga baho qo‘yish."""
    user_id = update.message.from_user.id
    if update.message.text == "❌ Bekor qilish":
        await update.message.reply_text(
            "*❌ Bekor qilindi! Bosh menyuga qaytdik:*",
            reply_markup=MAIN_MENU,
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    
    try:
        rating = int(update.message.text)
        if 1 <= rating <= 5:
            teacher = context.user_data.get('selected_teacher')
            if not teacher:
                await update.message.reply_text(
                    "*❌ O'qituvchi topilmadi! Qaytadan boshlang:*",
                    reply_markup=MAIN_MENU,
                    parse_mode='Markdown'
                )
                return ConversationHandler.END
            add_rating(user_id, teacher['user_id'], rating)
            await update.message.reply_text(
                f"*✅ {teacher['name']} ga {rating}⭐ baho berdingiz! Rahmat!*",
                reply_markup=MAIN_MENU,
                parse_mode='Markdown'
            )
            return ConversationHandler.END
        else:
            await update.message.reply_text(
                "*❌ 1-5 oralig‘ida raqam yuboring!*",
                reply_markup=REG_MENU,
                parse_mode='Markdown'
            )
            return RATE_VALUE
    except ValueError:
        await update.message.reply_text(
            "*❌ Faqat raqam yuboring!*",
            reply_markup=REG_MENU,
            parse_mode='Markdown'
        )
        return RATE_VALUE

async def top_teachers_handler(update: Update, context):
    """Top o'qituvchilarni ko'rsatish."""
    teachers = get_top_teachers()
    if not teachers:
        await update.message.reply_text(
            "*❌ Hozircha top o'qituvchilar yo'q! Tez orada yangilanadi:*",
            reply_markup=TOP_MENU,
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    
    teacher_list = "\n".join([f"*🔢 {i+1}. {teacher['name']} - {teacher['subject']} (⭐ {teacher['avg_rating']:.1f})*" for i, teacher in enumerate(teachers)])
    context.user_data['top_results'] = teachers
    await update.message.reply_text(
        f"*🏆 Top o'qituvchilar ro'yxati:*\n{teacher_list}\n\n"
        f"*🔍 Batafsil ma'lumot uchun raqamni yuboring (1-{len(teachers)}):*",
        reply_markup=TOP_MENU,
        parse_mode='Markdown'
    )
    return TOP_SELECT

async def top_select(update: Update, context):
    """Foydalanuvchi tanlagan top o'qituvchi haqida ma'lumot ko'rsatish."""
    if update.message.text == "❌ Bekor qilish":
        await update.message.reply_text(
            "*❌ Bekor qilindi! Bosh menyuga qaytdik:*",
            reply_markup=MAIN_MENU,
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    
    try:
        choice = int(update.message.text) - 1
        teachers = context.user_data['top_results']
        if 0 <= choice < len(teachers):
            teacher = teachers[choice]
            await update.message.reply_photo(
                photo=teacher['photo'],
                caption=f"*{format_teacher_info(teacher)}*\n*⭐ O‘rtacha baho:* {teacher['avg_rating']:.1f}\n\n*💬 Bog‘lanish uchun adminga yozing: {ADMIN_USERNAME}*",
                parse_mode='Markdown'
            )
            await update.message.reply_text(
                "*✅ Tanlagan o'qituvchi ma'lumotlari yuqorida!*",
                reply_markup=MAIN_MENU,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"*❌ Noto'g'ri raqam! 1-{len(teachers)} oralig'ida tanlang:*",
                reply_markup=TOP_MENU,
                parse_mode='Markdown'
            )
            return TOP_SELECT
    except ValueError:
        await update.message.reply_text(
            "*❌ Faqat raqam yuboring!*",
            reply_markup=TOP_MENU,
            parse_mode='Markdown'
        )
        return TOP_SELECT
    
    return ConversationHandler.END

async def chat_handler(update: Update, context):
    """Bog‘lanish jarayonini boshlash."""
    teachers = get_teachers()
    if not teachers:
        await update.message.reply_text(
            "*❌ Hozircha o'qituvchilar yo'q! Keyinroq qaytib keling:*",
            reply_markup=MAIN_MENU,
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    
    teacher_list = "\n".join([f"*🔢 {i+1}. {teacher['name']} - {teacher['subject']}*" for i, teacher in enumerate(teachers)])
    context.user_data['teachers'] = teachers
    await update.message.reply_text(
        f"*💬 Kim bilan bog‘lanmoqchisiz?*\n{teacher_list}\n\n*Raqamni yuboring (1-{len(teachers)}):*",
        reply_markup=REG_MENU,
        parse_mode='Markdown'
    )
    return CHAT_TEACHER

async def chat_teacher(update: Update, context):
    """Bog‘lanmoqchi bo‘lgan o‘qituvchini tanlash."""
    if update.message.text == "❌ Bekor qilish":
        await update.message.reply_text(
            "*❌ Bekor qilindi! Bosh menyuga qaytdik:*",
            reply_markup=MAIN_MENU,
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    
    try:
        choice = int(update.message.text) - 1
        teachers = context.user_data['teachers']
        if 0 <= choice < len(teachers):
            context.user_data['chat_teacher'] = teachers[choice]
            await update.message.reply_text(
                f"*💬 {teachers[choice]['name']} ga xabar yozing:*",
                reply_markup=REG_MENU,
                parse_mode='Markdown'
            )
            return CHAT_MESSAGE
        else:
            await update.message.reply_text(
                f"*❌ Noto'g'ri raqam! 1-{len(teachers)} oralig'ida tanlang:*",
                reply_markup=REG_MENU,
                parse_mode='Markdown'
            )
            return CHAT_TEACHER
    except ValueError:
        await update.message.reply_text(
            "*❌ Faqat raqam yuboring!*",
            reply_markup=REG_MENU,
            parse_mode='Markdown'
        )
        return CHAT_TEACHER

async def chat_message(update: Update, context):
    """Xabarni o‘qituvchiga yuborish."""
    user_id = update.message.from_user.id
    if update.message.text == "❌ Bekor qilish":
        await update.message.reply_text(
            "*❌ Bekor qilindi! Bosh menyuga qaytdik:*",
            reply_markup=MAIN_MENU,
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    
    teacher = context.user_data.get('chat_teacher')
    if not teacher:
        await update.message.reply_text(
            "*❌ O'qituvchi topilmadi! Qaytadan boshlang:*",
            reply_markup=MAIN_MENU,
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    
    message = update.message.text
    add_message(user_id, teacher['user_id'], message)
    await update.message.reply_text(
        f"*✅ Xabar {teacher['name']} ga yuborildi:* {message}",
        reply_markup=MAIN_MENU,
        parse_mode='Markdown'
    )
    try:
        await context.bot.send_message(
            teacher['user_id'],
            f"*💬 Sizga yangi xabar keldi:*\n*Kimdan:* ID {user_id}\n*Xabar:* {message}\n*Javob berish uchun: /javob {user_id} <xabar>*",
            parse_mode='Markdown'
        )
        await context.bot.send_message(
            ADMIN_ID,
            f"*💬 Chat xabari:*\n*Kimdan:* ID {user_id}\n*Kimga:* ID {teacher['user_id']}\n*Xabar:* {message}",
            parse_mode='Markdown'
        )
    except telegram.error.BadRequest as e:
        print(f"Teacher ID ({teacher['user_id']}) topilmadi: {e}")
    return ConversationHandler.END

async def rating_handler(update: Update, context):
    """Reyting bo'limini ko'rsatish (tajribaga va baholarga asoslangan top 5)."""
    teachers = get_top_teachers()
    if not teachers:
        await update.message.reply_text(
            "*❌ Hozircha reytingda o'qituvchilar yo'q! Tez orada yangilanadi:*",
            reply_markup=MAIN_MENU,
            parse_mode='Markdown'
        )
        return
    
    rating_list = "\n".join([f"*🏆 {i+1}. {teacher['name']} - {teacher['subject']} (⭐ {teacher['avg_rating']:.1f}, Tajriba: {teacher['experience']} yil)*" for i, teacher in enumerate(teachers)])
    await update.message.reply_text(
        f"*⭐ Eng yaxshi o'qituvchilar (Top 5):*\n{rating_list}",
        reply_markup=MAIN_MENU,
        parse_mode='Markdown'
    )

async def reply_handler(update: Update, context):
    """O‘qituvchi yoki talaba javob berishi uchun."""
    user_id = update.message.from_user.id
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "*❌ /javob <ID> <xabar> formatida yozing!*\n*Masalan:* /javob 123456 Salom",
            parse_mode='Markdown'
        )
        return
    try:
        receiver_id = int(context.args[0])
        message = " ".join(context.args[1:])
        add_message(user_id, receiver_id, message)
        await update.message.reply_text(
            f"*✅ Xabar ID {receiver_id} ga yuborildi:* {message}",
            reply_markup=MAIN_MENU,
            parse_mode='Markdown'
        )
        await context.bot.send_message(
            receiver_id,
            f"*💬 Sizga yangi xabar keldi:*\n*Kimdan:* ID {user_id}\n*Xabar:* {message}\n*Javob berish uchun: /javob {user_id} <xabar>*",
            parse_mode='Markdown'
        )
        await context.bot.send_message(
            ADMIN_ID,
            f"*💬 Chat xabari:*\n*Kimdan:* ID {user_id}\n*Kimga:* ID {receiver_id}\n*Xabar:* {message}",
            parse_mode='Markdown'
        )
    except ValueError:
        await update.message.reply_text(
            "*❌ ID noto‘g‘ri! /javob <ID> <xabar> formatida yozing:*",
            parse_mode='Markdown'
        )
    except telegram.error.BadRequest as e:
        print(f"Receiver ID ({receiver_id}) topilmadi: {e}")

async def cancel(update: Update, context):
    """Jarayonni bekor qilish."""
    await update.message.reply_text(
        "*❌ Bekor qilindi! Bosh menyuga qaytdik:*",
        reply_markup=MAIN_MENU,
        parse_mode='Markdown'
    )
    return ConversationHandler.END

def main():
    """Botni ishga tushirish."""
    init_db()

    application = Application.builder().token(BOT_TOKEN).build()

    reg_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start),
                      MessageHandler(filters.Regex("^📝 O'qituvchi sifatida ro'yxatdan o'tish$"), register_handler)],
        states={
            CONTACT: [MessageHandler(filters.CONTACT | (filters.TEXT & ~filters.COMMAND), contact)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, gender)],
            ERKAK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, erkak_name)],
            ERKAK_SUBJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, erkak_subject)],
            ERKAK_EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, erkak_experience)],
            ERKAK_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, erkak_price)],
            ERKAK_LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, erkak_location)],
            ERKAK_PHOTO: [MessageHandler(filters.PHOTO | (filters.TEXT & ~filters.COMMAND), erkak_photo)],
            ERKAK_BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, erkak_bio)],
            AYOL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ayol_name)],
            AYOL_SUBJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ayol_subject)],
            AYOL_EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ayol_experience)],
            AYOL_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ayol_price)],
            AYOL_LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, ayol_location)],
            AYOL_PHOTO: [MessageHandler(filters.PHOTO | (filters.TEXT & ~filters.COMMAND), ayol_photo)],
            AYOL_BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, ayol_bio)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    search_handler_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🔍 Qidiruv$"), search_handler)],
        states={
            SEARCH_SUBJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, search_subject)],
            SEARCH_SELECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, search_select)],
            RATE_TEACHER: [MessageHandler(filters.TEXT & ~filters.COMMAND, rate_teacher)],
            RATE_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, rate_value)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    top_handler_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🏆 Top o'qituvchilar$"), top_teachers_handler)],
        states={
            TOP_SELECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, top_select)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    chat_handler_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^💬 Bog‘lanish$"), chat_handler)],
        states={
            CHAT_TEACHER: [MessageHandler(filters.TEXT & ~filters.COMMAND, chat_teacher)],
            CHAT_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, chat_message)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(reg_handler)
    application.add_handler(search_handler_conv)
    application.add_handler(top_handler_conv)
    application.add_handler(chat_handler_conv)
    application.add_handler(MessageHandler(filters.Regex("^⭐ Reyting$"), rating_handler))
    application.add_handler(CommandHandler("javob", reply_handler))
    application.add_handler(MessageHandler(filters.Regex("^❌ Bekor qilish$"), cancel))
    setup_admin(application)

    application.run_polling()

if __name__ == '__main__':
    main()