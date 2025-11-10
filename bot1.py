import random
import telebot
import time
import os
import json
from datetime import datetime
from telebot import types

# СОЗДАЕМ НОВЫЙ ЭКЗЕМПЛЯР БОТА
bot = telebot.TeleBot("8526771479:AAHfp4-5bcw2xN7V1NeEEQzU5BiEACmb4a4")

ADMIN_ID = 7544112533
BANK_CARD = "2200701927460763"

# ФАЙЛЫ ДЛЯ СОХРАНЕНИЯ ДАННЫХ
STATS_FILE = "user_stats.json"
BLOCKS_FILE = "user_blocks.json"

# УБЕДИМСЯ ЧТО ФАЙЛЫ СУЩЕСТВУЮТ
def ensure_files_exist():
    """Создает файлы если они не существуют"""
    if not os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=2)
        print(f"📁 Создан файл {STATS_FILE}")
    
    if not os.path.exists(BLOCKS_FILE):
        with open(BLOCKS_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=2)
        print(f"📁 Создан файл {BLOCKS_FILE}")

# ВЫЗЫВАЕМ ПРИ СТАРТЕ
ensure_files_exist()

# УЛУЧШЕННАЯ ФУНКЦИЯ ЗАГРУЗКИ ДАННЫХ
def load_data(filename, default={}):
    """Загружает данные из файла"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"📥 Загружено из {filename}: {len(data)} записей")
                return data
        else:
            print(f"⚠️ Файл {filename} не существует")
            return default
    except Exception as e:
        print(f"❌ Ошибка загрузки {filename}: {e}")
        return default

# УЛУЧШЕННАЯ ФУНКЦИЯ СОХРАНЕНИЯ
def save_data(data, filename):
    """Сохраняет данные в файл"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 Сохранено в {filename}: {len(data)} записей")
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения {filename}: {e}")
        return False

# ЗАГРУЖАЕМ ДАННЫЕ ПРИ СТАРТЕ
user_stats = load_data(STATS_FILE)
user_blocks = load_data(BLOCKS_FILE)
pending_payments = {}

PRIZES = {
    100: [
        {"name": "📸 Откровенное фото", "weight": 40},
        {"name": "🎥 Горячее видео", "weight": 35}, 
        {"name": "🎤 Голосовое сообщение", "weight": 15},
        {"name": "💌 Сигна", "weight": 7},
        {"name": "📱 Персональное видео-приветствие", "weight": 2},
        {"name": "💋 Фото на заказ", "weight": 8},
        {"name": "🔥 Видео на заказ", "weight": 7},
        {"name": "💎 ВИП ПРИВАТ -50%", "weight": 6},
        {"name": "💎 ВИП ПРИВАТ -90%", "weight": 3},
        {"name": "💃 Стриптиз на камеру", "weight": 1},
        {"name": "🎤 Голосовой вирт 15 мин", "weight": 6},
        {"name": "💬 Текстовик-вирт 30 мин", "weight": 4},
        {"name": "🎭 Ролевая игра 20 мин", "weight": 3},
        {"name": "💕 Романтический видеочат 15 мин", "weight": 1},
        {"name": "✨ Эксклюзивный контент из архива", "weight": 1}
    ],
    500: [
        {"name": "📸 Откровенное фото", "weight": 40},
        {"name": "🎥 Горячее видео", "weight": 35}, 
        {"name": "🎤 Голосовое сообщение", "weight": 19},
        {"name": "💌 Сигна", "weight": 10},
        {"name": "📱 Персональное видео-приветствие", "weight": 8},
        {"name": "💋 Фото на заказ", "weight": 10},
        {"name": "🔥 Видео на заказ", "weight": 9},
        {"name": "💎 ВИП ПРИВАТ -50%", "weight": 8},
        {"name": "💎 ВИП ПРИВАТ -90%", "weight": 5},
        {"name": "💃 Стриптиз на камеру", "weight": 3},
        {"name": "📞 Видеозвонок 10 мин", "weight": 2},
        {"name": "🔥 Сигна на теле", "weight": 5},
        {"name": "🏆 Встреча", "weight": 0.5},
        {"name": "🎤 Голосовой вирт 15 мин", "weight": 6},
        {"name": "💬 Текстовик-вирт 30 мин", "weight": 4},
        {"name": "🎭 Ролевая игра 20 мин", "weight": 3},
        {"name": "💕 Романтический видеочат 15 мин", "weight": 1},
        {"name": "✨ Эксклюзивный контент из архива", "weight": 3}
    ],
    1000: [
        {"name": "🎥 Горячее видео", "weight": 18},
        {"name": "💋 Фото на заказ", "weight": 20},
        {"name": "🔥 Видео на заказ", "weight": 12},
        {"name": "💎 ВИП ПРИВАТ -50%", "weight": 10},
        {"name": "💎 ВИП ПРИВАТ -90%", "weight": 7},
        {"name": "💃 Стриптиз на камеру", "weight": 4},
        {"name": "📞 Видеозвонок 10 мин", "weight": 6},
        {"name": "🔥 Сигна на теле", "weight": 4},
        {"name": "🏆 Встреча", "weight": 1},
        {"name": "🎤 Голосовой вирт 15 мин", "weight": 6},
        {"name": "💬 Текстовик-вирт 30 мин", "weight": 8},
        {"name": "🎭 Ролевая игра 20 мин", "weight": 3},
        {"name": "💕 Романтический видеочат 15 мин", "weight": 1},
        {"name": "✨ Эксклюзивный контент из архива", "weight": 2}
    ]
}

def calculate_bonus(user_id):
    """Рассчитывает бонус на основе актуальных данных"""
    user_id_str = str(user_id)
    
    # ПЕРЕЗАГРУЖАЕМ СВЕЖИЕ ДАННЫЕ ИЗ ФАЙЛА
    fresh_stats = load_data(STATS_FILE)
    spins = fresh_stats.get(user_id_str, 0)
    bonus = min(spins * 2, 20)  # +2% за каждую крутку, максимум 20%
    
    print(f"🎁 Бонус для {user_id}: {spins} круток = +{bonus}%")
    return bonus

def is_user_blocked(user_id):
    user_id_str = str(user_id)
    if user_id_str in user_blocks:
        block_data = user_blocks[user_id_str]
        if isinstance(block_data, dict):
            if block_data.get('type') == 'permanent':
                return True
            elif block_data.get('type') == 'temporary' and time.time() < block_data.get('until', 0):
                return True
        else:
            del user_blocks[user_id_str]
            save_data(user_blocks, BLOCKS_FILE)
    return False

def update_user_stats(user_id):
    """ОБНОВЛЯЕМ СТАТИСТИКУ И СОХРАНЯЕМ В ФАЙЛ"""
    user_id_str = str(user_id)
    
    # ПЕРЕЗАГРУЖАЕМ СВЕЖИЕ ДАННЫЕ
    fresh_stats = load_data(STATS_FILE)
    current_spins = fresh_stats.get(user_id_str, 0)
    
    # ОБНОВЛЯЕМ ДАННЫЕ
    fresh_stats[user_id_str] = current_spins + 1
    
    # СОХРАНЯЕМ В ФАЙЛ
    if save_data(fresh_stats, STATS_FILE):
        # ОБНОВЛЯЕМ ГЛОБАЛЬНУЮ ПЕРЕМЕННУЮ
        global user_stats
        user_stats = fresh_stats
        print(f"📊 Обновлена статистика для {user_id}: было {current_spins}, стало {fresh_stats[user_id_str]} круток")
        return True
    else:
        print(f"❌ Ошибка сохранения статистики для {user_id}")
        return False

# КОМАНДА ДЛЯ ПРОВЕРКИ СТАТИСТИКИ
@bot.message_handler(commands=['mystats'])
def check_my_stats(message):
    """Показывает текущую статистику пользователя"""
    user_id = message.from_user.id
    user_id_str = str(user_id)
    
    # ЗАГРУЖАЕМ СВЕЖИЕ ДАННЫЕ ИЗ ФАЙЛА
    fresh_stats = load_data(STATS_FILE)
    
    spins = fresh_stats.get(user_id_str, 0)
    bonus = calculate_bonus(user_id)
    
    bot.send_message(
        message.chat.id,
        f"🔍 *ДЕБАГ СТАТИСТИКА:*\n"
        f"👤 ID: `{user_id}`\n"
        f"🎰 Круток: {spins}\n"
        f"✨ Бонус: +{bonus}%\n"
        f"💾 В памяти: {user_stats.get(user_id_str, 0)}\n"
        f"📁 В файле: {fresh_stats.get(user_id_str, 0)}",
        parse_mode='Markdown'
    )

@bot.message_handler(commands=['start'])
def start(message):
    if is_user_blocked(message.from_user.id):
        bot.send_message(message.chat.id, "❌ ТЫ ЗАБЛОКИРОВАН! 🚫")
        return
    
    # ПЕРЕЗАГРУЖАЕМ СТАТИСТИКУ ПРИ КАЖДОМ СТАРТЕ
    global user_stats
    user_stats = load_data(STATS_FILE)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('🎰 КРУТИТЬ РУЛЕТКУ')
    btn2 = types.KeyboardButton('💰 ТАРИФЫ')
    btn3 = types.KeyboardButton('📞 ПОМОЩЬ')
    markup.add(btn1, btn2, btn3)
    
    user_id = message.from_user.id
    spins = user_stats.get(str(user_id), 0)
    bonus = calculate_bonus(user_id)
    
    print(f"🚀 Старт для {user_id}: {spins} круток, +{bonus}% бонус")
    
    bot.send_message(message.chat.id,
                    f"""🎰 *РУЛЕТКА УДОВОЛЬСТВИЙ* 🎰

💫 *БЕСПРОИГРЫШНАЯ СИСТЕМА!*
Каждый получает приз - от фото до личной встречи!

💎 *СИСТЕМА ЛОЯЛЬНОСТИ:*
С каждой круткой шансы на ВИП-призы увеличиваются!
Твои крутки: {spins} (+{bonus}% к ВИП призам)

💎 *ВОЗМОЖНЫЕ ПРИЗЫ:*
• 📸 Фото / 🎥 Видео
• 💋 Контент на заказ  
• 💎 ВИП ПРИВАТ / ВИП ПРИВАТ на 24 часа / ВИП ПРИВАТ со скидкой 50-90%
• 💃 Стриптиз на камеру
• 📞 Видеозвонок / 💕 Романтический видеочат
• 🎤 Голосовые сообщения и интимный вирт
• 🎭 Ролевые игры и исполнение фантазий
• 🏆 Встреча / ✨ Эксклюзивный контент из архива
• 💌 Сигна и многое другое!

💌 *Твоя девочка:* @milsskeyy
💳 *Основная оплата:* Тинькофф {BANK_CARD}
💎 *Другие методы оплаты?* Пиши @milsskeyy

👇 *Выбери действие ниже!*""",
                    reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == '🎰 КРУТИТЬ РУЛЕТКУ')
def show_prices(message):
    if is_user_blocked(message.from_user.id):
        bot.send_message(message.chat.id, "❌ ТЫ ЗАБЛОКИРОВАН! 🚫")
        return
    
    # ПЕРЕЗАГРУЖАЕМ СТАТИСТИКУ ПЕРЕД ПОКАЗОМ ЦЕН
    global user_stats
    user_stats = load_data(STATS_FILE)
    
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('🟢 100₽', callback_data='pay_100')
    btn2 = types.InlineKeyboardButton('🟡 500₽', callback_data='pay_500') 
    btn3 = types.InlineKeyboardButton('🔴 1000₽', callback_data='pay_1000')
    markup.add(btn1, btn2, btn3)
    
    user_id = message.from_user.id
    spins = user_stats.get(str(user_id), 0)
    bonus = calculate_bonus(user_id)
    
    print(f"💰 Показ цен для {user_id}: {spins} круток, +{bonus}% бонус")
    
    bot.send_message(message.chat.id,
                   f"""💎 *ВЫБЕРИ СТАВКУ:*

🟢 *100₽* - базовые шансы
🟡 *500₽* - повышенные шансы  
🔴 *1000₽* - максимальные шансы

⚡ *С каждой круткой шансы РАСТУТ!*

📊 Твои крутки: {spins} (+{bonus}% к ВИП призам)
👇 *Сначала оплата - потом крутка!*""",
                   reply_markup=markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data.startswith('pay_'))
def handle_payment(call):
    user_id = call.from_user.id
    
    if is_user_blocked(user_id):
        bot.send_message(call.message.chat.id, "❌ ТЫ ЗАБЛОКИРОВАН! 🚫")
        return
    
    price = int(call.data.split('_')[1])
    pending_payments[user_id] = price
    
    bot.send_message(call.message.chat.id,
                   f"""💳 *ОПЛАТА ДЛЯ КРУТКИ*

💰 *Сумма к оплате:* {price}₽
📋 *Назначение:* Крутка рулетки

💳 *Реквизиты для оплаты:*
*Тинькофф:* {BANK_CARD}

📸 *После оплаты:*
1. *Сделай скриншот* чека/перевода
2. *Пришли скриншот* СЮДА В БОТА
3. *Жди подтверждения!*

⏰ *Подтверждение до 10 минут максимум!*

❓ *Если возникли проблемы с оплатой или нужен другой метод оплаты - пиши* @milsskeyy""",
                   parse_mode='Markdown')

@bot.message_handler(content_types=['photo'])
def handle_screenshot(message):
    user_id = message.from_user.id
    
    if user_id not in pending_payments:
        bot.send_message(message.chat.id, "❌ СНАЧАЛА ВЫБЕРИ СТАВКУ!")
        return
    
    price = pending_payments.get(user_id)
    if not price:
        bot.send_message(message.chat.id, "❌ ОШИБКА: СУММА ОПЛАТЫ НЕ НАЙДЕНА!")
        return

    # ОТПРАВЛЯЕМ АДМИНУ СКРИН И КНОПКИ
    admin_markup = types.InlineKeyboardMarkup()
    btn_confirm = types.InlineKeyboardButton('✅ ПОДТВЕРДИТЬ ОПЛАТУ', callback_data=f'admin_confirm_{user_id}')
    btn_reject = types.InlineKeyboardButton('❌ ОТКЛОНИТЬ', callback_data=f'admin_reject_{user_id}')
    btn_block_week = types.InlineKeyboardButton('🚫 ЗАБЛОКИРОВАТЬ НА НЕДЕЛЮ', callback_data=f'admin_block_week_{user_id}')
    btn_block_forever = types.InlineKeyboardButton('💀 ЗАБЛОКИРОВАТЬ НАВСЕГДА', callback_data=f'admin_block_forever_{user_id}')
    
    admin_markup.add(btn_confirm, btn_reject)
    admin_markup.add(btn_block_week, btn_block_forever)
    
    # ПЕРЕСЫЛАЕМ СКРИН АДМИНУ С КНОПКАМИ
    try:
        bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
        
        bot.send_message(
            ADMIN_ID,
            f"🔔 **НОВАЯ ОПЛАТА!**\n"
            f"👤 **ID:** `{user_id}`\n"
            f"💳 **Сумма:** {price}₽\n"
            f"📛 **Username:** @{message.from_user.username or 'Нет username'}\n"
            f"🕒 **Время:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"**ВЫБЕРИ ДЕЙСТВИЕ:**",
            parse_mode='Markdown',
            reply_markup=admin_markup
        )
        
    except Exception as e:
        print(f"ОШИБКА ПЕРЕСЫЛКИ СКРИНА АДМИНУ: {e}")
        try:
            bot.send_photo(
                ADMIN_ID, 
                message.photo[-1].file_id,
                caption=(
                    f"🔔 **НОВАЯ ОПЛАТА!**\n"
                    f"👤 **ID:** `{user_id}`\n"
                    f"💳 **Сумма:** {price}₽\n"
                    f"📛 **Username:** @{message.from_user.username or 'Нет username'}\n"
                    f"🕒 **Время:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                    f"**ВЫБЕРИ ДЕЙСТВИЕ:**"
                ),
                parse_mode='Markdown',
                reply_markup=admin_markup
            )
        except Exception as e2:
            print(f"ОШИБКА ОТПРАВКИ ФОТО АДМИНУ: {e2}")
            bot.send_message(
                ADMIN_ID,
                f"🔔 **НОВАЯ ОПЛАТА!**\n"
                f"👤 ID: {user_id}\n"
                f"💳 Сумма: {price}₽\n"
                f"📛 Username: @{message.from_user.username or 'Нет username'}\n"
                f"🕒 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"📸 Пользователь отправил скриншот, но не удалось его переслать\n\n"
                f"**ВЫБЕРИ ДЕЙСТВИЕ:**",
                reply_markup=admin_markup
            )
    
    bot.send_message(
        message.chat.id, 
        "✅ **СКРИНШОТ ОТПРАВЛЕН АДМИНУ!**\n\n"
        "⏳ *Ожидай подтверждения оплаты в течение 10 минут*\n"
        "📞 *Если возникли проблемы - пиши @milsskeyy*",
        parse_mode='Markdown'
    )

# КНОПКИ ДЛЯ АДМИНА
@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_'))
def handle_admin_actions(call):
    try:
        parts = call.data.split('_')
        if len(parts) < 3:
            bot.answer_callback_query(call.id, "❌ Ошибка в данных")
            return
            
        action, user_id_str = parts[1], parts[2]
        user_id = int(user_id_str)
        
        if action == 'confirm':
            price = pending_payments.get(user_id)
            if price:
                del pending_payments[user_id]
                spin_roulette_after_payment(user_id, price, user_id)
                bot.answer_callback_query(call.id, f"✅ Оплата подтверждена!")
                bot.send_message(call.message.chat.id, f"✅ ОПЛАТА ПОДТВЕРЖДЕНА ДЛЯ {user_id}!")
            else:
                bot.answer_callback_query(call.id, "❌ Пользователь не найден в ожидании")
        
        elif action == 'reject':
            if user_id in pending_payments:
                del pending_payments[user_id]
            bot.answer_callback_query(call.id, f"❌ Оплата отклонена!")
            bot.send_message(call.message.chat.id, f"❌ ОПЛАТА ОТКЛОНЕНА ДЛЯ {user_id}!")
            bot.send_message(user_id, "❌ ТВОЯ ОПЛАТА ОТКЛОНЕНА! ЕСЛИ ЧТО - ПИШИ АДМИНУ!")
        
        elif action == 'block_week':
            user_blocks[str(user_id)] = {'type': 'temporary', 'until': time.time() + 7*24*60*60}
            save_data(user_blocks, BLOCKS_FILE)
            if user_id in pending_payments:
                del pending_payments[user_id]
            bot.answer_callback_query(call.id, f"🚫 Заблокирован на неделю!")
            bot.send_message(call.message.chat.id, f"🚫 ПОЛЬЗОВАТЕЛЬ {user_id} ЗАБЛОКИРОВАН НА НЕДЕЛЮ!")
            bot.send_message(user_id, "🚫 ТЫ ЗАБЛОКИРОВАН НА НЕДЕЛЮ!")
        
        elif action == 'block_forever':
            user_blocks[str(user_id)] = {'type': 'permanent'}
            save_data(user_blocks, BLOCKS_FILE)
            if user_id in pending_payments:
                del pending_payments[user_id]
            bot.answer_callback_query(call.id, f"💀 Заблокирован навсегда!")
            bot.send_message(call.message.chat.id, f"💀 ПОЛЬЗОВАТЕЛЬ {user_id} ЗАБЛОКИРОВАН НАВСЕГДА!")
            bot.send_message(user_id, "💀 ТЫ ЗАБЛОКИРОВАН НАВСЕГДА!")
            
    except Exception as e:
        print(f"Ошибка в обработке админской кнопки: {e}")
        bot.answer_callback_query(call.id, "❌ Ошибка обработки")

def spin_roulette_after_payment(user_id, price, chat_id):
    prizes = PRIZES[price]
    
    # ОБНОВЛЯЕМ СТАТИСТИКУ ПЕРЕД КРУТКОЙ
    update_user_stats(user_id)
    
    # ПЕРЕЗАГРУЖАЕМ СВЕЖИЕ ДАННЫЕ ДЛЯ ОТОБРАЖЕНИЯ
    fresh_stats = load_data(STATS_FILE)
    spins = fresh_stats.get(str(user_id), 0)
    bonus = calculate_bonus(user_id)
    
    prize_names = [p["name"] for p in prizes]
    weights = [p["weight"] for p in prizes]
    
    # ПРИМЕНЯЕМ БОНУС К ВИП-ПРИЗАМ
    for i, name in enumerate(prize_names):
        if "ВИП" in name or "ВСТРЕЧА" in name or "ВЕЩЬ" in name:
            weights[i] += bonus
    
    prize = random.choices(prize_names, weights=weights)[0]
    
    print(f"🎰 Крутка для {user_id}: ставка {price}₽, круток {spins}, бонус +{bonus}%, выиграл: {prize}")
    
    bot.send_message(chat_id, "🎰 *Колесо запущено...*", parse_mode='Markdown')
    time.sleep(1.5)
    
    bot.send_message(chat_id, "🌀 *Колесо набирает скорость...*", parse_mode='Markdown')
    time.sleep(2)
    
    bot.send_message(chat_id, "💫 *Замедляется...*", parse_mode='Markdown')
    time.sleep(1.5)
    
    bot.send_message(chat_id,
                    f"""🎉 *ВЫ ВЫИГРАЛИ!*

💎 *Приз:* {prize}
💰 *Ставка:* {price}₽
📈 *Ваши крутки:* {spins}
✨ *Бонус:* +{bonus}% к ВИП призам

📞 *Для получения приза свяжись с* @milsskeyy
⏰ *Ответ в течение 15 минут*

🎰 *Удачи в следующих крутках!* 🍀""",
                    parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == '💰 ТАРИФЫ')
def show_tariffs(message):
    if is_user_blocked(message.from_user.id):
        bot.send_message(message.chat.id, "❌ ТЫ ЗАБЛОКИРОВАН! 🚫")
        return
    
    bot.send_message(message.chat.id,
                   """💰 *НАСКОЛЬКО ТЫ СМЕЛ?*

🟢 *100₽* - ДЛЯ НАЧАЛА

🟡 *500₽* - ДЛЯ ЦЕНИТЕЛЕЙ  

🔴 *1000₽* - ДЛЯ ИЗБРАННЫХ

🎁 *Гарантированный приз в каждой крутке!*
✨ *С каждой ставкой призы становятся интереснее!*""",
                   parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == '📞 ПОМОЩЬ')
def show_help(message):
    if is_user_blocked(message.from_user.id):
        bot.send_message(message.chat.id, "❌ ТЫ ЗАБЛОКИРОВАН! 🚫")
        return
    
    bot.send_message(message.chat.id,
                   f"""📞 *ИНСТРУКЦИЯ ДЛЯ КРУТКИ:*

1️⃣ *Нажми* «🎰 КРУТИТЬ РУЛЕТКУ»
2️⃣ *Выбери* ставку (100/500/1000₽)
3️⃣ *Оплати* на карту Тинькофф:
   {BANK_CARD}
4️⃣ *Пришли* скриншот оплаты СЮДА В БОТА
5️⃣ *Получи* подтверждение и крути рулетку!
6️⃣ *Забирай* приз!

💌 *По всем вопросам:* @milsskeyy
⏰ *Ответ в течение 15 минут*

🎰 *УДАЧИ!* 🍀""",
                   parse_mode='Markdown')

print("🎰 БОТ ЗАПУЩЕН! РАБОТАЕТ 24/7! 💀")
print("📸 СКРИНЫ ПЕРЕСЫЛАЮТСЯ АДМИНУ НАПРЯМУЮ БЕЗ СОХРАНЕНИЯ!")
print("💾 СТАТИСТИКА СОХРАНЯЕТСЯ В ФАЙЛЫ!")
print(f"📊 Загружено пользователей: {len(user_stats)}")
print(f"🚫 Загружено блокировок: {len(user_blocks)}")
bot.infinity_polling()
