import os
import telebot
import json

TOKEN = os.environ["TOKEN"]
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
bot = telebot.TeleBot(TOKEN)

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from urllib.parse import quote
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

GUIDE_DATA = {
    'food': {
        'title': '🍽️ Їжа',
        'menu_text': 'Хочеш щось смачненьке? Ось що можу порекомендувати:',
        'sub_menu': {
            'breakfast': ('Сніданки та бранчі', '*Camélia Brunch Garden* – високі оцінки, затишний сад\n*Do Norte Café* – популярно серед туристів та місцевих\n*Eleven Lab Concept* – креативні бранчі, Instagram‑дружня зона'),
            'traditional': ('Традиційна їжа', '*O Buraco* – тріпас по‑португальськи, домашні страви\n*A Cozinha do Manel* – класичний португал. обід\n*Taberna Dos Mercadores* – інтимна атмосфера, традиційна кухня'),
            'nata': ('Паштел де ната', '*Manteigaria* – бездоганні крем‑пиріжки\n*Castro – Atelier de Pastéis de Nata* – один з найкращих у місті\n*Fábrica da Nata* – популярне, близько до Боляньо'),
            'bars': ('Бари і паби', '*Letraria Craft Beer Garden* – понад 50 сортів крафту\n*Catraio* – найстаріший паб із 130+ пінтами\n*Bar Santa Cachaca* – класичні коктейлі, дружня атмосфера'),
            'dinner': ('Вечеря', '*Ode Porto Wine House* – романтика, португал. кухня\n*Casa de Chá da Boa Nova* – морські краєвиди, мішленівська атмосфера\n*Taberna Dos Mercadores* – вечірня класика'),
            'vegan': ('Веганські місця', '*Apuro Vegan Bar* – рейтинговий веган‑бар\n*Essência Restaurante Vegetariano* – затишно і смачно\n*Árvore do Mundo* – близький фул‑веган, творчий дизайн'),
        }
    },
    'viewpoints': ('🌅 В'юпойнтс', 'Ось топ‑3 точки для заходу сонця:\n*Jardim do Morro (Gaia)* – класика для sunset\n*Mosteiro da Serra do Pilar* – неоцифрований вид на місто\n*Jardins do Palácio de Cristал* – панорама та романтика'),
    'workspaces': ('🧑‍💻 Місця для роботи', 'Віддалено попрацювати? Ось топ‑3:\n*C'alma Coffee Room* – добрий Wi‑Fi, кавова енергія\n*Negra Café* – стильно, валід для ноутбуку\n*Outsite Cowork Café* – простір з кабінками та зустрічками'),
    'winebars': ('🍷 Винні бари', '*Portologia – La Maison des Port* – дегустація, сири, Gaia\n*Dick's Bar (в The Yeatman Hotel)* – містична атмосфера, вид на Дору\n*A Cave Do Bon Vivant* – натуральні вина, спокійна камерність'),
    'beaches': ('🏖️ Пляжі', '*Praia dos Ingleses (Foz)* – кафе на "пальях"\n*Piscinas de Marés, Leça da Palmeira* – архітектурні басейни Сиза\n*Praia do Senhor da Pedra (Miramar)* – скеля + релакс'),
    'trails': ('🥾 Волкін трейли', '*Porto City Walk (~7 км)* – по історичних вулицях і набережній\n*Ribeira → Gaia → Miradouro trail* – через місто до Gaia viewpoint\n*Serra do Porto Park Trails* – зелень і природа за містом'),
    'sights': ('🏛️ Визначні місця', '*Dom Luís I Bridge* – ікона Порто, пішохідний перехід\n*Clérigos Tower* – підйом на панорамну вежу\n*São Bento Station* – азулежу‑музей на вокзалі'),
    'stay': ('🛏️ Де зупинитись', '*Hospes Infante Sagres* – бутік‑готель, центрально, зятний сніданок\n*The Yeatman Hotel* – люкс із видом, винний бар\n*PortoBay Flores* – стильний, недалеко від старого міста'),
}

def create_maps_link(place_name):
    base_url = "https://www.google.com/maps/search/?api=1&query="
    query = quote(f"{place_name}, Porto")
    return f"[{place_name}]({base_url}{query})"

def format_content(content_string):
    lines = content_string.split('\n')
    formatted_lines = [f"📍 {create_maps_link(line.strip('*').split('–')[0].strip())} {'–' + '–'.join(line.strip('*').split('–')[1:]) if '–' in line else ''}" if line.startswith('*') else line for line in lines]
    return '\n'.join(formatted_lines)

def gen_main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = [InlineKeyboardButton(data['title'] if isinstance(data, dict) else data[0], callback_data=f"main_{key}") for key, data in GUIDE_DATA.items()]
    markup.add(*buttons)
    return markup

def gen_food_submenu():
    markup = InlineKeyboardMarkup(row_width=1)
    buttons = [InlineKeyboardButton(data[0], callback_data=f"sub_food_{key}") for key, data in GUIDE_DATA['food']['sub_menu'].items()]
    markup.add(*buttons)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        logging.info(f"Користувач {message.from_user.first_name} (ID: {message.from_user.id}) натиснув /start")
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Хочу гайд по Порто", callback_data="show_main_menu"))
        welcome_text = "Привіт! Дякуємо за оплату - твій гід по Порто від нас вже готовий!"
        photo_url = os.environ.get("WELCOME_IMAGE_URL", "")
        if photo_url:
            bot.send_photo(
                chat_id=message.chat.id,
                photo=photo_url,
                caption=welcome_text,
                reply_markup=markup
            )
        else:
            bot.send_message(message.chat.id, welcome_text, reply_markup=markup)
    except Exception as e:
        logging.error(f"ПОМИЛКА в send_welcome: {e}", exc_info=True)
        if ADMIN_ID:
            bot.send_message(ADMIN_ID, f"⚠️ Виникла помилка в боті при обробці /start:\n\n`{e}`", parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    try:
        logging.info(f"Користувач {call.from_user.first_name} (ID: {call.from_user.id}) натиснув кнопку '{call.data}'")
        bot.answer_callback_query(call.id)
        if call.data == 'show_main_menu':
            bot.send_message(call.message.chat.id, "Що саме тебе цікавить у Порто?", reply_markup=gen_main_menu())
            return
        parts = call.data.split('_')
        menu_type, category = parts[0], parts[1]
        if menu_type == 'main':
            if category == 'food':
                bot.send_message(call.message.chat.id, GUIDE_DATA['food']['menu_text'], reply_markup=gen_food_submenu())
            else:
                title, content = GUIDE_DATA[category]
                bot.send_message(call.message.chat.id, f"*{title}*\n\n{format_content(content)}", parse_mode='Markdown')
        elif menu_type == 'sub' and category == 'food':
            sub_category = parts[2]
            title, content = GUIDE_DATA['food']['sub_menu'][sub_category]
            bot.send_message(call.message.chat.id, f"*{title}*\n\n{format_content(content)}", parse_mode='Markdown')
    except Exception as e:
        logging.error(f"ПОМИЛКА в обробнику кнопок: {e}", exc_info=True)
        if ADMIN_ID:
            bot.send_message(ADMIN_ID, f"⚠️ Виникла помилка в боті при обробці кнопки '{call.data}':\n\n`{e}`", parse_mode='Markdown')

@bot.message_handler(commands=['reply'])
def reply_to_user(message):
    if message.from_user.id != ADMIN_ID:
        logging.warning(f"Спроба несанкціонованого доступу до /reply від user ID: {message.from_user.id}")
        return
    try:
        parts = message.text.split(maxsplit=2)
        target_user_id, reply_text = int(parts[1]), parts[2]
        bot.send_message(target_user_id, f"Відповідь від підтримки:\n\n{reply_text}")
        bot.reply_to(message, f"✅ Повідомлення успішно надіслано користувачу {target_user_id}.")
        logging.info(f"Адміністратор (ID: {ADMIN_ID}) надіслав відповідь користувачу {target_user_id}.")
    except Exception as e:
        bot.reply_to(message, "Неправильний формат або помилка. Використовуйте: /reply <ID> <текст>")
        logging.error(f"Помилка в команді /reply: {e}")

def handler(request, response):
    if request.method == "POST":
        length = int(request.headers.get("content-length", 0))
        body = request.body.read(length)
        update = telebot.types.Update.de_json(body.decode("utf-8"))
        bot.process_new_updates([update])
        response.status_code = 200
        response.body = b"ok"
        return response
    else:
        response.status_code = 405
        response.body = b"Method Not Allowed"
        return response
