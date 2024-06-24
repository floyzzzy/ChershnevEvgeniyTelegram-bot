import telebot
import sqlite3
from datetime import datetime
# from telebot import types

from keyboards import main_keyboard, in_menu_keyboard, add_dell_keyboard, basket_keyboard, back_to_one_and_accept, \
    back_ones, only_back, edit_and_yes

bot = telebot.TeleBot('6281465070:AAGMmPzed7cVSHlFY27QU-RmLQYYpb7Q3t8')

say = False
number = 0

# Инициализация базы данных и создание таблиц
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                      user_id INTEGER PRIMARY KEY,
                      address TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS basket (
                      user_id INTEGER,
                      pizza_id INTEGER,
                      FOREIGN KEY(user_id) REFERENCES users(user_id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS history (
                      user_id INTEGER,
                      order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                      address TEXT,
                      order_details TEXT,
                      price INTEGER,
                      datetime TEXT,
                      FOREIGN KEY(user_id) REFERENCES users(user_id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS pizzas (
                      id_pizza INTEGER PRIMARY KEY,
                      photo TEXT,
                      pizza_name TEXT,
                      text TEXT,
                      price INTEGER)''')
    conn.commit()
    conn.close()

def add_to_basket(user_id, pizza_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO basket (user_id, pizza_id) VALUES (?, ?)', (user_id, pizza_id))
    conn.commit()
    conn.close()

def remove_from_basket(user_id, pizza_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM basket WHERE user_id = ? AND pizza_id = ?', (user_id, pizza_id))
    conn.commit()
    conn.close()

def get_basket(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT pizza_id FROM basket WHERE user_id = ?', (user_id,))
    basket = cursor.fetchall()
    conn.close()
    return [item[0] for item in basket]

def update_address(user_id, address):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO users (user_id, address) VALUES (?, ?)', (user_id, address))
    conn.commit()
    conn.close()

def get_address(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT address FROM users WHERE user_id = ?', (user_id,))
    address = cursor.fetchone()
    conn.close()
    return address[0] if address else None

def add_order(user_id, address, order_details, price):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO history (user_id, address, order_details, price, datetime) VALUES (?, ?, ?, ?, ?)',
                   (user_id, address, order_details, price, datetime.now().strftime('%d.%m.%y')))
    conn.commit()
    conn.close()

def get_order_history(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT address, order_details, datetime, price FROM history WHERE user_id = ? ORDER BY datetime DESC LIMIT 10', (user_id,))
    history = cursor.fetchall()
    conn.close()
    return history

@bot.message_handler(commands=['start', 'LetsGo'])
def start(message):
    name = message.from_user.first_name
    mess = f'Привет, <b>{name}</b>. ' \
           f'BotPizza🍕 - прототип бота, который доставляет еду. '

    photo_pic = open('pic.png', 'rb')
    markup = main_keyboard()
    bot.send_photo(message.chat.id, photo_pic, caption=mess, parse_mode='html', reply_markup=markup)

@bot.callback_query_handler(func=lambda callback: True)
def callback(call):
    global say, number
    if call.message:
        if call.data == 'menu':
            bot.send_message(call.message.chat.id, "Каталог: ", parse_mode='html')

            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute('SELECT id_pizza, photo, pizza_name, text, price FROM pizzas')
            data = cursor.fetchall()
            conn.close()

            for item in data:
                id_pizza, photo, pizza_name, text, price = item
                markup = add_dell_keyboard(id_pizza)
                message_1 = f"{pizza_name}: {text}\n<b>Цена:</b> {price} руб."
                bot.send_photo(call.message.chat.id, photo=open(photo, 'rb'), caption=message_1, parse_mode='html',
                               reply_markup=markup)
                bot.answer_callback_query(call.id, text="Добавлено в корзину!")

            markup = basket_keyboard()
            bot.send_message(call.message.chat.id, f'Чтобы открыть корзину, нажмите на кнопку!', reply_markup=markup)

            markup = in_menu_keyboard()
            bot.send_message(call.message.chat.id, f'Чтобы вернуться в главное меню, нажмите на кнопу!',
                             reply_markup=markup)

        elif call.data == 'history':
            markup = back_ones()
            history = get_order_history(call.from_user.id)
            if not history:
                mess1 = f'Ваша история заказов в данный момент пуста. ' \
                        f'Сделайте заказ, и она пополнится!'
                bot.send_message(call.message.chat.id, text=mess1, parse_mode='html', reply_markup=markup)
            else:
                mess = f'Ваша история заказов:\n'
                conn = sqlite3.connect('database.db')
                cursor = conn.cursor()
                cursor.execute('SELECT id_pizza, pizza_name FROM pizzas')
                pizzas = {item[0]: item[1] for item in cursor.fetchall()}
                conn.close()

                for item in history:
                    address, order_details, date, price = item
                    mess += f"{date}\nАдрес: {address}\nДетали:\n"
                    for pizza_id in order_details.split(','):
                        if int(pizza_id) in pizzas:
                            mess += f"{pizzas[int(pizza_id)]}\n"
                    mess += f"Цена: {price}\n"
                bot.send_message(call.message.chat.id, mess, parse_mode='html', reply_markup=markup)

        elif call.data.startswith('add_to_basket'):
            id_piz = int(call.data.split("_")[-1])
            add_to_basket(call.from_user.id, id_piz)
            bot.answer_callback_query(call.id, text="Добавлено в корзину!")

        elif call.data.startswith('dell_from_basket'):
            id_piz = int(call.data.split("_")[-1])
            remove_from_basket(call.from_user.id, id_piz)
            bot.answer_callback_query(call.id, text="Удалено из корзины!")

        elif call.data == 'basket':
            basket = get_basket(call.from_user.id)
            if not basket:
                markup = only_back()
                mess = f'Ваша корзина в данный момент пуста!'
                bot.send_message(call.message.chat.id, mess, reply_markup=markup)
            else:
                markup = back_to_one_and_accept()
                mess = "Ваша корзина:\n"
                cost = 0
                conn = sqlite3.connect('database.db')
                cursor = conn.cursor()
                cursor.execute('SELECT id_pizza, pizza_name, price FROM pizzas')
                pizzas = {item[0]: (item[1], item[2]) for item in cursor.fetchall()}
                conn.close()
                for pizza_id in basket:
                    if pizza_id in pizzas:
                        pizza_name, price = pizzas[pizza_id]
                        mess += f"{pizza_name}\n"
                        cost += price
                mess += f"Цена: {cost} руб."
                bot.send_message(call.message.chat.id, mess, parse_mode='html', reply_markup=markup)

        elif call.data == 'accept':
            address = get_address(call.from_user.id)
            if not address:
                mess = f'Запишите ваш адрес в виде: ул.ХХХ д.ХХ эт.Х кв.ХХ\nЕсли вы обладатель частного дома, квартиру и этаж не писать.'
                bot.send_message(call.message.chat.id, mess, parse_mode='html')
                say = True
            else:
                markup = edit_and_yes()
                bot.send_message(call.message.chat.id, f"Ваш адрес: {address}, верно?", reply_markup=markup)

        elif call.data == 'edit':
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
            update_address(call.from_user.id, "")
            mess = f'Запишите ваш адрес в виде: ул.ХХХ д.ХХ эт.Х кв.ХХ\nЕсли вы обладатель частного дома, квартиру и этаж не писать.'
            bot.send_message(call.message.chat.id, mess, parse_mode='html')
            say = True

        elif call.data == 'yes':
            mess = f'Заказ оформлен! Курьер прибудет по адресу:\n'
            address = get_address(call.from_user.id)
            basket = get_basket(call.from_user.id)
            order_details = ','.join(map(str, basket))
            cost = 0
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute('SELECT id_pizza, pizza_name, price FROM pizzas')
            pizzas = {item[0]: (item[1], item[2]) for item in cursor.fetchall()}
            conn.close()
            for pizza_id in basket:
                if pizza_id in pizzas:
                    pizza_name, price = pizzas[pizza_id]
                    mess += f"{pizza_name}\n"
                    cost += price
            mess += f"К оплате: {cost} руб."
            bot.send_message(call.message.chat.id, mess, parse_mode='html')
            mess = 'Заказ будет доставлен в течение часа, ожидайте.\nВы можете обратиться с некоторыми вопросами по номеру: 80000000000'
            markup = in_menu_keyboard()
            bot.send_message(call.message.chat.id, mess, parse_mode='html', reply_markup=markup)

            add_order(call.from_user.id, address, order_details, cost)

        elif call.data == 'back_one':
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)

        elif call.data == 'back':
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
            name = call.from_user.first_name
            mess = f'Привет, <b>{name}</b>. BotPizza🍕 - прототип бота, который доставляет еду. '

            photo_pic = open('pic.png', 'rb')
            markup = main_keyboard()
            bot.send_photo(call.message.chat.id, photo_pic, caption=mess, parse_mode='html', reply_markup=markup)

@bot.message_handler(content_types=['text'])
def get_user_text(message):
    global say
    if message.text == "Привет":
        bot.send_message(message.chat.id, "И тебе привет!", parse_mode='html')

    if say:
        if len(message.text) > 6:
            address = message.text
            update_address(message.from_user.id, address)
            markup = edit_and_yes()
            bot.send_message(message.chat.id, f"Ваш адрес: {address}, верно?", reply_markup=markup)
            say = False
        else:
            bot.send_message(message.chat.id, "Возможно вы неправильно ввели адрес, повторите попытку.", parse_mode='html')

if __name__ == '__main__':
    init_db()
    bot.polling(none_stop=True)
