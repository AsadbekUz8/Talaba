from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler
from telegram.ext import filters
from database import approve_last_teacher, reject_last_teacher, get_teachers, get_all_users  # get_all_users qo‘shildi
from utils import format_teacher_info_admin
from config import ADMIN_ID, ADMIN_USERNAME

# Admin menyusi (emojilar bilan)
ADMIN_MENU = ReplyKeyboardMarkup(
    [["📊 Statistika", "✅ Tasdiqlash"],
     ["❌ Rad etish", "📢 Reklama yuborish"],
     ["👨‍🏫 O‘qituvchilar", "🚪 Chiqish"]],
    resize_keyboard=True
)

# Asosiy menyu (main.py bilan moslashtirildi)
MAIN_MENU = ReplyKeyboardMarkup(
    [["📝 O'qituvchi sifatida ro'yxatdan o'tish", "🔍 Qidiruv"],
     ["🏆 Top o'qituvchilar", "⭐ Reyting"],
     ["💬 Bog‘lanish"]],
    resize_keyboard=True
)

# Holatlar
ADMIN_MAIN = 0

async def admin_panel(update: Update, context):
    """Admin panelini ochish."""
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text(
            "*🚫 Bu faqat admin uchun!*",
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    await update.message.reply_text(
        "*👨‍💼 Admin paneliga xush kelibsiz!*\n*Quyidagi bo‘limlardan birini tanlang:*",
        reply_markup=ADMIN_MENU,
        parse_mode='Markdown'
    )
    return ADMIN_MAIN

async def admin_main(update: Update, context):
    """Admin menyusidagi buyruqlarni boshqarish."""
    choice = update.message.text
    if choice == "📊 Statistika":
        teachers = get_teachers()
        total_teachers = len(teachers)
        users = get_all_users()
        total_users = len(users)
        await update.message.reply_text(
            f"*📊 Statistika:*\n"
            f"*👨‍🏫 Tasdiqlangan o‘qituvchilar:* {total_teachers}\n"
            f"*👥 Foydalanuvchilar:* {total_users}",
            reply_markup=ADMIN_MENU,
            parse_mode='Markdown'
        )
    elif choice == "✅ Tasdiqlash":
        teacher = approve_last_teacher()
        if teacher:
            await context.bot.send_message(
                teacher['user_id'], 
                "*🎉 Tabriklaymiz! Ro‘yxatdan o‘tdingiz! 🚀*",
                parse_mode='Markdown'
            )
            await update.message.reply_text(
                f"*✅ O‘qituvchi tasdiqlandi:*\n{teacher['name']} ({teacher['subject']})",
                reply_markup=ADMIN_MENU,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "*❌ Tasdiqlash uchun o‘qituvchi yo‘q!*",
                reply_markup=ADMIN_MENU,
                parse_mode='Markdown'
            )
    elif choice == "❌ Rad etish":
        teacher = reject_last_teacher()
        if teacher:
            await context.bot.send_message(
                teacher['user_id'], 
                "*❌ Afsus, ro‘yxatdan o‘tish rad etildi.*",
                parse_mode='Markdown'
            )
            await update.message.reply_text(
                f"*❌ O‘qituvchi rad etildi:*\n{teacher['name']} ({teacher['subject']})",
                reply_markup=ADMIN_MENU,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "*❌ Rad etish uchun o‘qituvchi yo‘q!*",
                reply_markup=ADMIN_MENU,
                parse_mode='Markdown'
            )
    elif choice == "📢 Reklama yuborish":
        await update.message.reply_text(
            "*📢 Reklama matnini yozing! Masalan: /sendad Yangi kurs boshlandi! 🚀*",
            reply_markup=ADMIN_MENU,
            parse_mode='Markdown'
        )
        return ConversationHandler.END  # Keyin /sendad ishlatiladi
    elif choice == "👨‍🏫 O‘qituvchilar":
        teachers = get_teachers()
        if not teachers:
            await update.message.reply_text(
                "*❌ Hozircha tasdiqlangan o‘qituvchi yo‘q!*",
                reply_markup=ADMIN_MENU,
                parse_mode='Markdown'
            )
        else:
            teacher_list = "\n".join([f"*🆔 {t['user_id']}: {t['name']} - {t['subject']}*" for t in teachers])
            await update.message.reply_text(
                f"*👨‍🏫 Tasdiqlangan o‘qituvchilar:*\n{teacher_list}",
                reply_markup=ADMIN_MENU,
                parse_mode='Markdown'
            )
    elif choice == "🚪 Chiqish":
        await update.message.reply_text(
            "*👋 Admin panelidan chiqdingiz! Bosh menyuga qaytdik:*",
            reply_markup=MAIN_MENU,
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            "*❌ Noto‘g‘ri tanlov! Quyidagilardan birini tanlang:*",
            reply_markup=ADMIN_MENU,
            parse_mode='Markdown'
        )
    return ADMIN_MAIN

async def send_ad(update: Update, context):
    """Tasdiqlangan o‘qituvchilarga reklama yuborish."""
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text(
            "*🚫 Bu faqat admin uchun!*",
            parse_mode='Markdown'
        )
        return
    if not context.args:
        await update.message.reply_text(
            "*📢 Reklama matnini yozing! Masalan: /sendad Yangi kurs boshlandi! 🚀*",
            parse_mode='Markdown'
        )
        return
    
    ad_text = " ".join(context.args)
    teachers = get_teachers()
    
    if not teachers:
        await update.message.reply_text(
            "*❌ Tasdiqlangan o‘qituvchi yo‘q!*",
            parse_mode='Markdown'
        )
        return
    
    successful_sends = 0
    for teacher in teachers:
        try:
            await context.bot.send_message(
                teacher['user_id'], 
                ad_text,
                parse_mode='Markdown'
            )
            successful_sends += 1
        except telegram.error.BadRequest as e:
            print(f"Xabar yuborilmadi (ID {teacher['user_id']}): {e}")
        except Exception as e:
            print(f"Xato (ID {teacher['user_id']}): {e}")
    
    if successful_sends > 0:
        await update.message.reply_text(
            f"*✅ Reklama {successful_sends} ta o‘qituvchiga yuborildi!*",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "*❌ Hech kimga yuborilmadi! O‘qituvchilar botni ishlatmayotgan bo‘lishi mumkin:*",
            parse_mode='Markdown'
        )

def setup_admin(application):
    """Admin buyruqlarini ulash."""
    admin_handler = ConversationHandler(
        entry_points=[CommandHandler("admin", admin_panel)],
        states={
            ADMIN_MAIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_main)]
        },
        fallbacks=[]
    )
    application.add_handler(admin_handler)
    application.add_handler(CommandHandler("sendad", send_ad))