# utils.py - Ma’lumotlarni chiroyli formatlash uchun yordamchi funksiyalar

def format_teacher_info(teacher):
    """Foydalanuvchi uchun o‘qituvchi ma’lumotlarini formatlash (kontaktsiz)."""
    return (f"👨‍🏫 Ism: {teacher['name']}\n"
            f"📚 Fan: {teacher['subject']}\n"
            f"⏳ Tajriba: {teacher['experience']} yil\n"
            f"💸 Narx: {teacher['price']} so‘m/soat\n"
            f"📍 Joy: {teacher['location']}\n"
            f"ℹ️ Bio: {teacher['bio']}")

def format_teacher_info_admin(teacher):
    """Admin uchun o‘qituvchi ma’lumotlarini formatlash (kontakt bilan)."""
    return (f"👨‍🏫 Ism: {teacher['name']}\n"
            f"📚 Fan: {teacher['subject']}\n"
            f"⏳ Tajriba: {teacher['experience']} yil\n"
            f"💸 Narx: {teacher['price']} so‘m/soat\n"
            f"📍 Joy: {teacher['location']}\n"
            f"ℹ️ Bio: {teacher['bio']}\n"
            f"📞 Kontakt: {teacher['contact']}")