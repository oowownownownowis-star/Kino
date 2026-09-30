from datetime import datetime
import random
import sqlite3
from threading import Thread
from flask import Flask
import telebot
from telebot import types

# --- TO'G'RIDAN-TO'G'RI SOZLangan MA'LUMOTLAR ---
TOKEN = "8781482311:AAhw-gEN7ZiL8PYrrVOoI6exP0b7K1uzDRM"
ADMIN_ID = 8753350906

# --- AVTOMATIK SQLITE BAZASI ---
conn = sqlite3.connect('bot_database.db', check_same_thread=False)
cursor = conn.cursor()

# Jadvallarni avtomatik yaratish
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    joined_date TEXT,
    status TEXT DEFAULT 'active',
    lang TEXT DEFAULT 'uz',
    is_vip_uz INTEGER DEFAULT 0,
    is_vip_ru INTEGER DEFAULT 0,
    is_vip_en INTEGER DEFAULT 0
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS movies (
    code TEXT PRIMARY KEY,
    video_id TEXT,
    is_vip INTEGER DEFAULT 0,
    downloads INTEGER DEFAULT 0
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS channels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_username TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS custom_buttons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    button_name TEXT,
    button_content TEXT
)
''')
conn.commit()
# ---------------------------------------------

bot = telebot.TeleBot(TOKEN)
user_states = {}

# --- RENDER / 24/7 UCHUN FLASK SERVER ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running 24/7!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_web)
    t.start()
# ---------------------------------------

LANG_TEXTS = {
    "uz": {
        "menu": "✅ Asosiy menyu:",
        "search_btn": "🔍 Qidirish",
        "random_btn": "🎲 Tasodifiy kino",
        "vip_btn": "💎 Premium Obuna",
        "lang_btn": "🌐 Tilni o'zgartirish",
        "ad_btn": "📢 Reklama",
        "settings_btn": "⚙️ Nastroyka (Admin)",
        "search_prompt": "🔎 Kino kodini yuboring (masalan: `1`):",
        "movie_not_found": "❌ `{code}` kodi topilmadi.",
        "movies_not_found": "❌ Kinolar topilmadi.",
        "download_count": "⬇️ Yuklab olishlar:",
        "vip_choose_period": "💎 **O'zbekcha VIP Premium Obuna**\n\nMuddatni tanlang:",
        "card_info": "💳 **Karta raqami:** `6262 5701 4806 4381`\n👤 **Ism Familiya:** Obidjonova M.\n\n📥 To'lov qilib, chek rasmini shu botga yuboring!",
        "vip_ad_notice": "💎 *Agar VIP obunaga a'zo bo'lsangiz, hech qanday kanallarga obuna bo'lmasdan, reklamasiz va yuqori sifatda tomosha qilasiz!*",
        "ad_footer": (
            "\n\n━━━━━━━━━━━━━━━━━━━━━\n"
            "🚀 **TELEGRAM KANALINGIZ O'SMAYAPTI?**\n"
            "📢 Telegram kanal va guruhlaringizga AKTIV obunachilar yig'ib beramiz!\n\n"
            "✅ Haqiqiy auditoriya\n"
            "✅ Tezkor xizmat\n"
            "✅ Sifat kafolati\n\n"
            "• Garantiya - 😎🇺🇿\n"
            "(Jvoy o'zbek obunachi)\n\n"
            "1000 👥 obunachi - 90.000so'm\n"
            "2000 👥 obunachi - 180.000so'm\n"
            "3000 👥 obunachi - 270.000so'm\n"
            "5000 👥 obunachi - 450.000so'm\n\n"
            "🔥 Kanalingizni bugunoq rivojlantirishni boshlang!\n"
            "📩 Admin: @mhdnvwv"
        )
    },
    "ru": {
        "menu": "✅ Главное меню:",
        "search_btn": "🔍 Поиск",
        "random_btn": "🎲 Случайный фильм",
        "vip_btn": "💎 VIP Подписка",
        "lang_btn": "🌐 Сменить язык",
        "ad_btn": "📢 Реклама",
        "settings_btn": "⚙️ Настройки (Админ)",
        "search_prompt": "🔎 Отправьте код фильма (например: `1`):",
        "movie_not_found": "❌ Код `{code}` не найден.",
        "movies_not_found": "❌ Фильмы не найдены.",
        "download_count": "⬇️ Скачивания:",
        "vip_choose_period": "💎 **Русская VIP Премиум Подписка**\n\nВыберите срок:",
        "card_info": "💳 **Номер карты:** `6262 5701 4806 4381`\n👤 **ФИО:** Obidjonova M.\n\n📥 Сделайте перевод и отправьте скриншот чека сюда!",
        "vip_ad_notice": "💎 *Если у вас есть VIP подписка, вы смотрите без подписок на каналы, без рекламы и в высоком качестве!*",
        "ad_footer": (
            "\n\n━━━━━━━━━━━━━━━━━━━━━\n"
            "🚀 **РАСКРУТКА В TELEGRAM**\n"
            "📢 Живые и активные подписчики в ваши каналы!\n\n"
            "1000 👥 подписчиков - 90.000 сум\n"
            "2000 👥 подписчиков - 180.000 сум\n"
            "3000 👥 подписчиков - 270.000 сум\n"
            "5000 👥 подписчиков - 450.000 сум\n\n"
            "📩 Админ: @mhdnvwv"
        )
    },
    "en": {
        "menu": "✅ Main menu:",
        "search_btn": "🔍 Search",
        "random_btn": "🎲 Random Movie",
        "vip_btn": "💎 VIP Subscription",
        "lang_btn": "🌐 Language",
        "ad_btn": "📢 Ads",
        "settings_btn": "⚙️ Settings (Admin)",
        "search_prompt": "🔎 Send movie code (e.g., `1`):",
        "movie_not_found": "❌ Code `{code}` not found.",
        "movies_not_found": "❌ No movies found.",
        "download_count": "⬇️ Downloads:",
        "vip_choose_period": "💎 **English VIP Premium Subscription**\n\nSelect period:",
        "card_info": "💳 **Card Number:** `6262 5701 4806 4381`\n👤 **Name:** Obidjonova M.\n\n📥 Make the payment and send the receipt screenshot here!",
        "vip_ad_notice": "💎 *If you have a VIP subscription, you watch without channel subscriptions, ad-free, and in high quality!*",
        "ad_footer": (
            "\n\n━━━━━━━━━━━━━━━━━━━━━\n"
            "🚀 **TELEGRAM PROMOTION**\n"
            "📢 Active subscribers for your channels!\n\n"
            "1000 👥 subscribers - 90.000 UZS\n"
            "2000 👥 subscribers - 180.000 UZS\n"
            "3000 👥 subscribers - 270.000 UZS\n"
            "5000 👥 subscribers - 450.000 UZS\n\n"
            "📩 Админ: @mhdnvwv"
        )
    }
}

def get_user_lang(user_id):
    cursor.execute("SELECT lang FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if row:
        return row[0]
    return "uz"

def set_user_lang(user_id, lang):
    cursor.execute("UPDATE users SET lang = ? WHERE user_id = ?", (lang, user_id))
    conn.commit()

def is_user_vip_for_lang(user_id, lang):
    if user_id == ADMIN_ID:
        return True
    cursor.execute(f"SELECT is_vip_{lang} FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if row:
        return row[0] == 1
    return False

def check_channels_subscription(user_id):
    if user_id == ADMIN_ID:
        return True
    cursor.execute("SELECT channel_username FROM channels")
    channels = cursor.fetchall()
    if not channels:
        return True

    for ch_row in channels:
        ch = ch_row[0]
        try:
            member = bot.get_chat_member(ch, user_id)
            if member.status in ['left', 'kicked']:
                return False
        except Exception:
            pass
    return True

def show_vip_keyboard(lang):
    markup = types.InlineKeyboardMarkup()
    periods = [
        ("1 kunlik", "1d"), ("3 kunlik", "3d"), ("10 kunlik", "10d"),
        ("1 oylik", "1"), ("3 oylik", "3"), ("6 oylik", "6"),
        ("9 oylik", "9"), ("1 yillik", "12"), ("10 yillik", "120")
    ]
    for name, code in periods:
        markup.row(types.InlineKeyboardButton(f"💎 {name} VIP ({lang.upper()})", callback_data=f"vip_{lang}_{code}"))
    return markup

def get_movie_inline_buttons(lang):
    markup = types.InlineKeyboardMarkup()
    if lang == 'uz':
        markup.row(
            types.InlineKeyboardButton("💎 VIP Obuna", callback_data="btn_vip_menu"),
            types.InlineKeyboardButton("📢 Reklama berish", callback_data="btn_ad_info")
        )
    elif lang == 'ru':
        markup.row(
            types.InlineKeyboardButton("💎 VIP Подписка", callback_data="btn_vip_menu"),
            types.InlineKeyboardButton("📢 Реклама", callback_data="btn_ad_info")
        )
    else:
        markup.row(
            types.InlineKeyboardButton("💎 VIP Subscription", callback_data="btn_vip_menu"),
            types.InlineKeyboardButton("📢 Ads", callback_data="btn_ad_info")
        )
    return markup

def show_main_menu(chat_id, user_id):
    lang = get_user_lang(user_id)
    t = LANG_TEXTS[lang]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(t["search_btn"], t["random_btn"])
    markup.row(t["vip_btn"], t["lang_btn"])
    markup.row(t["ad_btn"])
    
    cursor.execute("SELECT button_name FROM custom_buttons")
    custom_btns = cursor.fetchall()
    for btn in custom_btns:
        markup.row(btn[0])

    if user_id == ADMIN_ID:
        markup.row(t["settings_btn"])
    bot.send_message(chat_id, t["menu"], reply_markup=markup)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    
    if not row:
        cursor.execute("INSERT INTO users (user_id, username, joined_date, status, lang, is_vip_uz, is_vip_ru, is_vip_en) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                       (user_id, message.from_user.username, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'active', 'uz', 0, 0, 0))
        conn.commit()
    else:
        cursor.execute("UPDATE users SET status = 'active' WHERE user_id = ?", (user_id,))
        conn.commit()

    if message.text and message.text.startswith('/start kino_'):
        code = message.text.split('_')[1]
        process_user_movie_request(message.chat.id, user_id, code)
        return

    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz"),
        types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")
    )
    bot.send_message(message.chat.id, "🌍 Tilni tanlang / Выберите язык / Select language:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def callback_language(call):
    lang = call.data.split('_')[1]
    set_user_lang(call.from_user.id, lang)
    bot.answer_callback_query(call.id, "Saved ✅")
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    show_main_menu(call.message.chat.id, call.from_user.id)

@bot.callback_query_handler(func=lambda call: call.data == 'btn_vip_menu')
def inline_vip_menu(call):
    lang = get_user_lang(call.from_user.id)
    t = LANG_TEXTS[lang]
    markup = show_vip_keyboard(lang)
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, t["vip_choose_period"], reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'btn_ad_info')
def inline_ad_info(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "📢 **Reklama va kanal rivojlantirish uchun:**\n\nMurojaat uchun lichkamiz: @mhdnvwv", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == 'check_sub')
def check_subscription_callback(call):
    user_id = call.from_user.id
    if check_channels_subscription(user_id):
        bot.answer_callback_query(call.id, "Rahmat! Obuna tasdiqlandi ✅")
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        bot.send_message(call.message.chat.id, "✅ Obunangiz tekshirildi! Endi kino kodini qaytadan yuboring yoki menyudan foydalaning.")
    else:
        bot.answer_callback_query(call.id, "Siz hali hamma kanallarga obuna bo'lmadingiz ❌", show_alert=True)

@bot.message_handler(func=lambda m: m.text in ["🌐 Tilni o'zgartirish", "🌐 Сменить язык", "🌐 Language"])
def change_lang_btn(m):
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz"),
        types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")
    )
    bot.send_message(m.chat.id, "🌍 Tilni tanlang / Выберите язык / Select language:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in ["💎 Premium Obuna", "💎 VIP Подписка", "💎 VIP Subscription"])
def vip_menu(m):
    lang = get_user_lang(m.from_user.id)
    t = LANG_TEXTS[lang]
    markup = show_vip_keyboard(lang)
    bot.send_message(m.chat.id, t["vip_choose_period"], reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('vip_'))
def callback_vip_period(call):
    parts = call.data.split('_')
    lang = parts[1]
    period = parts[2]
    t = LANG_TEXTS[lang]
    text = f"💎 **VIP Obuna ({lang.upper()} - {period})**\n\n" + t["card_info"]
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(content_types=['photo'], func=lambda m: m.from_user.id != ADMIN_ID)
def handle_payment_screenshot(message):
    user_id = message.from_user.id
    photo_id = message.photo[-1].file_id
    lang = get_user_lang(user_id)
    
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("UZB ✅", callback_data=f"accept_vip_uz_{user_id}"),
        types.InlineKeyboardButton("RUS ✅", callback_data=f"accept_vip_ru_{user_id}"),
        types.InlineKeyboardButton("ENG ✅", callback_data=f"accept_vip_en_{user_id}")
    )
    markup.row(types.InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_vip_{user_id}"))
    
    bot.send_photo(ADMIN_ID, photo_id, caption=f"💳 **Yangi to'lov cheki!**\nFoydalanuvchi ID: `{user_id}`\nTil: `{lang}`", parse_mode="Markdown", reply_markup=markup)
    bot.reply_to(message, "✅ Chekingiz admingacha yetib bordi! Tez orada tekshiriladi.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('accept_vip_') or call.data.startswith('reject_vip_') or call.data.startswith('revoke_vip_'))
def admin_vip_decision(call):
    if call.from_user.id != ADMIN_ID:
        return
    data = call.data.split('_')
    action = data[0]
    
    if action == 'accept':
        lang_vip = data[2]
        user_id = int(data[3])
        cursor.execute(f"UPDATE users SET is_vip_{lang_vip} = 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        
        bot.answer_callback_query(call.id, f"{lang_vip.upper()} VIP tasdiqlandi ✅")
        bot.send_message(user_id, f"🎉 Tabriklaymiz! Sizning {lang_vip.upper()} bo'yicha VIP obunangiz faollashdi! ✅")
        
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton(f"❌ {lang_vip.upper()} VIP ni bekor qilish", callback_data=f"revoke_vip_{lang_vip}_{user_id}"))
        bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=call.message.caption + f"\n\n✅ QABUL QILINGAN ({lang_vip.upper()} VIP FAOL)", reply_markup=markup)
        
    elif action == 'revoke':
        lang_vip = data[2]
        user_id = int(data[3])
        cursor.execute(f"UPDATE users SET is_vip_{lang_vip} = 0 WHERE user_id = ?", (user_id,))
        conn.commit()
        
        bot.answer_callback_query(call.id, f"{lang_vip.upper()} VIP bekor qilindi ❌")
        bot.send_message(user_id, f"❌ Sizning {lang_vip.upper()} VIP obunangiz admin tomonidan bekor qilindi/o'zgartirildi.")
        
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("UZB ✅", callback_data=f"accept_vip_uz_{user_id}"),
            types.InlineKeyboardButton("RUS ✅", callback_data=f"accept_vip_ru_{user_id}"),
            types.InlineKeyboardButton("ENG ✅", callback_data=f"accept_vip_en_{user_id}")
        )
        markup.row(types.InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_vip_{user_id}"))
        bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=call.message.caption.split("\n\n✅")[0] + "\n\n❌ VIP BEKOR QILINDI", reply_markup=markup)

    else:
        user_id = int(data[2])
        bot.answer_callback_query(call.id, "Rad etildi ❌")
        bot.send_message(user_id, "❌ To'lov chekingiz rad etildi.")
        bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=call.message.caption + "\n\n❌ RAD ETILGAN")

@bot.message_handler(func=lambda m: m.text in ["📢 Reklama", "📢 Реклама", "📢 Ads"])
def ad_info(m):
    bot.send_message(m.chat.id, "📢 **Reklama va kanal rivojlantirish uchun:**\n\nMurojaat uchun lichkamiz: @mhdnvwv", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and m.text in ["⚙️ Nastroyka (Admin)", "⚙️ Настройки (Админ)", "⚙️ Settings (Admin)"])
def admin_settings_menu(m):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📊 Statistika")
    markup.row("➕ Majburiy obuna", "🗑 Majburiy obunani o'chirish")
    markup.row("🎬 Kino qo'shish", "💎 VIP kino qo'shish")
    markup.row("🗑 Kino o'chirish")
    markup.row("➕ Qo'shimcha tugma qo'shish", "🗑 Tugmani o'chirish")
    markup.row("⬅️ Asosiy menyu")
    bot.send_message(m.chat.id, "⚙️ Admin sozlamalari paneliga xush kelibsiz:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "⬅️ Asosiy menyu")
def back_to_main(m):
    show_main_menu(m.chat.id, m.from_user.id)

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and m.text == "📊 Statistika")
def admin_stats(m):
    cursor.execute("SELECT status, is_vip_uz, is_vip_ru, is_vip_en FROM users")
    users = cursor.fetchall()
    
    total_users = len(users)
    active_users = sum(1 for u in users if u[0] == "active")
    left_users = total_users - active_users
    vip_users = sum(1 for u in users if u[1] == 1 or u[2] == 1 or u[3] == 1)
    
    cursor.execute("SELECT COUNT(*) FROM movies")
    movies_count = cursor.fetchone()[0]
    
    text = (
        "📊 **Bot Statistikasi:**\n\n"
        f"👥 Jami kirgan odamlar: {total_users}\n"
        f"🟢 Hozirda botda bor odamlar: {active_users}\n"
        f"🔴 Chiqib ketgan odamlar: {left_users}\n"
        f"🎬 Kinolar soni: {movies_count}\n"
        f"💎 VIP obuna bo'lganlar (jami): {vip_users}"
    )
    bot.reply_to(m, text, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and m.text == "➕ Majburiy obuna")
def add_channel_start(m):
    user_states[m.from_user.id] = {'state': 'waiting_for_channel'}
    bot.reply_to(m, "📢 Majburiy kanal username yoki havolasini yuboring (masalan: `@kanal_nomi`):")

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and user_states.get(m.from_user.id, {}).get('state') == 'waiting_for_channel')
def save_channel(m):
    channel = m.text.strip()
    cursor.execute("INSERT INTO channels (channel_username) VALUES (?)", (channel,))
    conn.commit()
    bot.reply_to(m, f"✅ `{channel}` majburiy obuna uchun qo'shildi!", parse_mode="Markdown")
    user_states[m.from_user.id] = {}

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and m.text == "🗑 Majburiy obunani o'chirish")
def delete_channel_list(m):
    cursor.execute("SELECT id, channel_username FROM channels")
    channels = cursor.fetchall()
    
    if not channels:
        bot.reply_to(m, "❌ Hozircha majburiy kanallar yo'q.")
        return
        
    markup = types.InlineKeyboardMarkup()
    for ch in channels:
        markup.row(types.InlineKeyboardButton(f"❌ O'chirish: {ch[1]}", callback_data=f"del_ch_{ch[0]}"))
    bot.reply_to(m, "🗑 O'chirmoqchi bo'lgan majburiy kanalni tanlang:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('del_ch_'))
def remove_channel_callback(call):
    if call.from_user.id != ADMIN_ID:
        return
    ch_id = int(call.data.split('_')[2])
    cursor.execute("DELETE FROM channels WHERE id = ?", (ch_id,))
    conn.commit()
    bot.answer_callback_query(call.id, "O'chirildi ✅")
    bot.edit_message_text("🗑 Tanlangan majburiy obuna kanali o'chirildi!", call.message.chat.id, call.message.message_id)

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and m.text == "➕ Qo'shimcha tugma qo'shish")
def add_custom_button_start(m):
    user_states[m.from_user.id] = {'state': 'waiting_for_button_name'}
    bot.reply_to(m, "➕ Yangi tugma nomini yuboring (masalan: `🎁 Konkurs` yoki `🔥 Aksiya`):")

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and user_states.get(m.from_user.id, {}).get('state') == 'waiting_for_button_name')
def get_custom_button_name(m):
    user_states[m.from_user.id]['button_name'] = m.text.strip()
    user_states[m.from_user.id]['state'] = 'waiting_for_button_content'
    bot.reply_to(m, "✅ Tugma nomi qabul qilindi.\n\nEndi foydalanuvchi shu tugmani bosganda chiqadigan **matn, shartlar yoki e'lonni** yuboring:")

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and user_states.get(m.from_user.id, {}).get('state') == 'waiting_for_button_content')
def get_custom_button_content(m):
    content = m.text.strip()
    data = user_states.get(m.from_user.id, {})
    btn_name = data.get('button_name')
    
    cursor.execute("INSERT INTO custom_buttons (button_name, button_content) VALUES (?, ?)", (btn_name, content))
    conn.commit()
    
    bot.reply_to(m, f"🎉 Yangi `{btn_name}` tugmasi muvaffaqiyatli qo'shildi va menyuda chiqdi!", parse_mode="Markdown")
    user_states[m.from_user.id] = {}

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and m.text == "🗑 Tugmani o'chirish")
def delete_custom_button_list(m):
    cursor.execute("SELECT id, button_name FROM custom_buttons")
    buttons = cursor.fetchall()
    
    if not buttons:
        bot.reply_to(m, "❌ Hozircha qo'shimcha tugmalar mavjud emas.")
        return
        
    markup = types.InlineKeyboardMarkup()
    for b in buttons:
        markup.row(types.InlineKeyboardButton(f"❌ O'chirish: {b[1]}", callback_data=f"del_btn_{b[0]}"))
    bot.reply_to(m, "🗑 O'chirmoqchi bo'lgan tugmangizni tanlang:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('del_btn_'))
def remove_custom_button_callback(call):
    if call.from_user.id != ADMIN_ID:
        return
    b_id = int(call.data.split('_')[2])
    cursor.execute("DELETE FROM custom_buttons WHERE id = ?", (b_id,))
    conn.commit()
    bot.answer_callback_query(call.id, "Tugma o'chirildi ✅")
    bot.edit_message_text("🗑 Tanlangan tugma menyudan olib tashlandi!", call.message.chat.id, call.message.message_id)

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and m.text == "🗑 Kino o'chirish")
def delete_movie_start(m):
    user_states[m.from_user.id] = {'state': 'waiting_for_delete_code'}
    bot.reply_to(m, "🗑 O'chirmoqchi bo'lgan kino kodini yuboring:")

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and user_states.get(m.from_user.id, {}).get('state') == 'waiting_for_delete_code')
def delete_movie_by_code(m):
    code = m.text.strip()
    cursor.execute("SELECT code FROM movies WHERE code = ?", (code,))
    if cursor.fetchone():
        cursor.execute("DELETE FROM movies WHERE code = ?", (code,))
        conn.commit()
        bot.reply_to(m, f"✅ `{code}` kodi bo'lgan kino bazadan muvaffaqiyatli o'chirildi!", parse_mode="Markdown")
    else:
        bot.reply_to(m, f"❌ `{code}` kodi bilan kino topilmadi.", parse_mode="Markdown")
    user_states[m.from_user.id] = {}

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and m.text in ["🎬 Kino qo'shish", "💎 VIP kino qo'shish"])
def admin_add_movie(m):
    is_vip = 1 if "VIP" in m.text else 0
    user_states[m.from_user.id] = {'state': 'waiting_for_movie_video', 'is_vip': is_vip}
    bot.reply_to(m, "🎬 Kino videosini yuboring:")

@bot.message_handler(content_types=['video'], func=lambda m: m.from_user.id == ADMIN_ID and user_states.get(m.from_user.id, {}).get('state') == 'waiting_for_movie_video')
def get_movie_video(m):
    user_states[m.from_user.id]['video_id'] = m.video.file_id
    user_states[m.from_user.id]['state'] = 'waiting_for_movie_code'
    bot.reply_to(m, "✅ Video qabul qilindi. Endi kino kodini yuboring (masalan: `1`):")

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and user_states.get(m.from_user.id, {}).get('state') == 'waiting_for_movie_code')
def get_movie_code(m):
    code = m.text.strip()
    data = user_states.get(m.from_user.id, {})
    
    cursor.execute("INSERT OR REPLACE INTO movies (code, video_id, is_vip, downloads) VALUES (?, ?, ?, COALESCE((SELECT downloads FROM movies WHERE code = ?), 0))",
                   (code, data.get('video_id'), data.get('is_vip', 0), code))
    conn.commit()
    
    bot.reply_to(m, f"🎉 Kino saqlandi! Kodi: `{code}`", parse_mode="Markdown")
    user_states[m.from_user.id] = {}

@bot.message_handler(func=lambda m: m.text in ["🎲 Tasodifiy kino", "🎲 Случайный фильм", "🎲 Random Movie"])
def random_m(message):
    process_user_random_request(message.chat.id, message.from_user.id)

def process_user_random_request(chat_id, user_id):
    lang = get_user_lang(user_id)
    t = LANG_TEXTS[lang]
    
    is_vip_current = is_user_vip_for_lang(user_id, lang)

    if not is_vip_current and not check_channels_subscription(user_id):
        send_subscription_prompt(chat_id, lang)
        return

    if is_vip_current or user_id == ADMIN_ID:
        cursor.execute("SELECT code, video_id, downloads FROM movies")
    else:
        cursor.execute("SELECT code, video_id, downloads FROM movies WHERE is_vip = 0")
        
    movies = cursor.fetchall()
    
    if not movies:
        bot.send_message(chat_id, t["movies_not_found"])
        return
        
    movie = random.choice(movies)
    code, video_id, downloads = movie[0], movie[1], movie[2]
    
    new_downloads = downloads + 1
    cursor.execute("UPDATE movies SET downloads = ? WHERE code = ?", (new_downloads, code))
    conn.commit()
    
    caption = f"🎬 **Kino tavsiyasi** (Kod: `{code}`)\n\n{t['download_count']} {new_downloads}" + t["ad_footer"]
    markup = get_movie_inline_buttons(lang)
    bot.send_video(chat_id, video_id, caption=caption, parse_mode="Markdown", reply_markup=markup, protect_content=False)

@bot.message_handler(func=lambda m: m.text in ["🔍 Qidirish", "🔍 Поиск", "🔍 Search"])
def search(m):
    lang = get_user_lang(m.from_user.id)
    bot.send_message(m.chat.id, LANG_TEXTS[lang]["search_prompt"])

EXCLUDED_BTNS = [
    "📊 Statistika", "🎲 Tasodifiy kino", "🎲 Случайный фильм", "🎲 Random Movie",
    "🔍 Qidirish", "🔍 Поиск", "🔍 Search", "💎 Premium Obuna", "💎 VIP Подписка", "💎 VIP Subscription",
    "📢 Reklama", "📢 Реклама", "📢 Ads", "🌐 Tilni o'zgartirish", "🌐 Сменить язык", "🌐 Language",
    "⚙️ Nastroyka (Admin)", "⚙️️ Настройки (Админ)", "⚙️ Settings (Admin)",
    "➕ Majburiy obuna", "🗑 Majburiy obunani o'chirish", "🎬 Kino qo'shish", "💎 VIP kino qo'shish", "🗑 Kino o'chirish",
    "➕ Qo'shimcha tugma qo'shish", "🗑 Tugmani o'chirish", "⬅️ Asosiy menyu"
]

@bot.message_handler(func=lambda m: m.text and not m.text.startswith('/') and m.text not in EXCLUDED_BTNS)
def handle_text_codes_or_custom_buttons(message):
    text = message.text.strip()
    
    cursor.execute("SELECT button_content FROM custom_buttons WHERE button_name = ?", (text,))
    row = cursor.fetchone()
    if row:
        bot.send_message(message.chat.id, row[0], parse_mode="Markdown")
        return
        
    process_user_movie_request(message.chat.id, message.from_user.id, text)

def send_subscription_prompt(chat_id, lang):
    t = LANG_TEXTS[lang]
    cursor.execute("SELECT channel_username FROM channels")
    channels = cursor.fetchall()

    markup = types.InlineKeyboardMarkup()
    for ch_row in channels:
        ch = ch_row[0]
        channel_url = f"https://t.me/{ch.replace('@', '')}"
        markup.row(types.InlineKeyboardButton(f"📢 {ch} ga obuna bo'lish", url=channel_url))
    
    markup.row(types.InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub"))

    text = f"{t['vip_ad_notice']}\n\n❌ **Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:**"
    bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=markup)

def process_user_movie_request(chat_id, user_id, code):
    lang = get_user_lang(user_id)
    t = LANG_TEXTS[lang]
    
    is_vip_current = is_user_vip_for_lang(user_id, lang)

    if not is_vip_current and not check_channels_subscription(user_id):
        send_subscription_prompt(chat_id, lang)
        return

    cursor.execute("SELECT video_id, is_vip, downloads FROM movies WHERE code = ?", (code,))
    row = cursor.fetchone()
    if not row:
        bot.send_message(chat_id, t["movie_not_found"].format(code=code), parse_mode="Markdown")
        return
        
    video_id, is_vip, downloads = row[0], row[1], row[2]
    
    if is_vip == 1 and not is_vip_current and user_id != ADMIN_ID:
        markup = show_vip_keyboard(lang)
        bot.send_message(chat_id, "❌ Bu kino faqat tanlangan til bo'yicha VIP obunachilar uchun!", reply_markup=markup)
        return
        
    new_downloads = downloads + 1
    cursor.execute("UPDATE movies SET downloads = ? WHERE code = ?", (new_downloads, code))
    conn.commit()
    
    caption = f"🎬 **Kino tavsiyasi** (Kod: `{code}`)\n\n{t['download_count']} {new_downloads}" + t["ad_footer"]
    markup = get_movie_inline_buttons(lang)
    bot.send_video(chat_id, video_id, caption=caption, parse_mode="Markdown", reply_markup=markup, protect_content=False)

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
