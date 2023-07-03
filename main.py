import telebot
import json
from datetime import datetime
# from telebot import types

from keyboards import main_keyboard, in_menu_keyboard, add_dell_keyboard, basket_keyboard, back_to_one_and_accept, \
    back_ones, only_back, edit_and_yes

bot = telebot.TeleBot('6281465070:AAGMmPzed7cVSHlFY27QU-RmLQYYpb7Q3t8')

dct = {}

say = False

number = 0


# -----------------------СТАРТ---------------------------------#
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

        # -----------Инлайн кнопка каталог--------------------------
        if call.data == 'menu':
            bot.send_message(call.message.chat.id, "Каталог: ", parse_mode='html')

            with open('json/catalog.json', 'r', encoding="utf-8") as file:
                data = json.load(file)
            #print(data)

            for item in data['response']['items']:
                markup = add_dell_keyboard(item['id_pizza'])
                photos = item['photo']
                pizza_name = item['pizza_name']
                text = item['text']
                prices = item['price']
                message_1 = pizza_name + ": " + text + "\n" + "<b>Цена:</b> " + str(prices) + " руб."
                bot.send_photo(call.message.chat.id, photo=open(photos, 'rb'), caption=message_1, parse_mode='html',
                               reply_markup=markup)
                bot.answer_callback_query(call.id, text="Добавлено в корзину!")
                #print(photos, pizza_name, text, prices)

            # Корзина
            markup = basket_keyboard()
            bot.send_message(call.message.chat.id, f'Чтобы открыть корзину, нажмите на кнопку!', reply_markup=markup)

            # Назад
            markup = in_menu_keyboard()
            bot.send_message(call.message.chat.id, f'Чтобы вернуться в главное меню, нажмите на кнопу!',
                             reply_markup=markup)

        # -----------Инлайн кнопка история заказов--------------------------
        elif call.data == 'history':
            markup = back_ones()
            with open('json/history.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
            with open('json/catalog.json', 'r', encoding="utf-8") as file:
                pizzas = json.load(file)

            history = data.get(str(call.from_user.id), [])
            history = history[-10:]
            if not history:
                mess1 = f'Ваша история заказов в данный момент пуста. ' \
                       f'Сделайте заказ, и она пополнится!'
                bot.send_message(call.message.chat.id, text=mess1, parse_mode='html', reply_markup=markup)
            else:
                mess = f'Ваша история заказов:\n'
                for item in history:
                    address = item['address']
                    order = item['order']
                    date = item['datetime']
                    price = item['price']
                    mess += date + "\n" + "Адрес: " + address + "\n" + "Детали:\n"
                    #print(address, order, date, price)
                    for pizza_id in order:
                        for pizza in pizzas['response']['items']:
                            if pizza['id_pizza'] == pizza_id:
                                mess += pizza['pizza_name'] + '\n'
                    mess += "Цена: " + str(price) + "\n"
                bot.send_message(call.message.chat.id, mess, parse_mode='html', reply_markup=markup)

        # -----------Инлайн кнопка добавить в корзину--------------------------
        elif call.data.startswith('add_to_basket'):
            id_piz = int(call.data.split("_")[-1])
            with open('json/users.json', 'r', encoding="utf-8") as file:
                data = json.load(file)

            basket = data.get(str(call.from_user.id), [])
            basket.append(id_piz)
            data[str(call.from_user.id)] = basket
            with open('json/users.json', 'w') as file:
                json.dump(data, file)

            bot.answer_callback_query(call.id, text="Добавлено в корзину!")

        # -----------Инлайн кнопка убрать из корзины--------------------------
        elif call.data.startswith('dell_from_basket'):
            id_piz = int(call.data.split("_")[-1])
            with open('json/users.json', 'r', encoding="utf-8") as file:
                data = json.load(file)

            basket = data.get(str(call.from_user.id), [])
            if basket.count(id_piz) > 0:
                basket.remove(id_piz)
            data[str(call.from_user.id)] = basket
            with open('json/users.json', 'w') as file:
                json.dump(data, file)

            bot.answer_callback_query(call.id, text="Удалено из корзины!")

        # -----------Инлайн кнопка корзина--------------------------
        elif call.data == 'basket':
            with open('json/users.json', 'r', encoding="utf-8") as file:
                data = json.load(file)

            with open('json/catalog.json', 'r', encoding="utf-8") as file:
                pizzas = json.load(file)

            basket = data.get(str(call.from_user.id), [])
            if len(basket) == 0:
                markup = only_back()
                mess = f'Ваша корзина в данный момент пуста!'
                bot.send_message(call.message.chat.id, mess, reply_markup=markup)

            else:
                markup = back_to_one_and_accept()
                mess = "Ваша корзина:\n"
                cost = 0
                for pizza_id in basket:
                    for pizza in pizzas['response']['items']:
                        if pizza['id_pizza'] == pizza_id:
                            mess += pizza['pizza_name'] + '\n'
                            cost += pizza['price']
                mess += "Цена: " + str(cost) + " руб."
                bot.send_message(call.message.chat.id, mess, parse_mode='html', reply_markup=markup)

        # -----------Инлайн кнопка оформить заказ--------------------------
        elif call.data == 'accept':
            with open('json/address.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
            address = data.get(str(call.from_user.id), "")
            if address == "":
                mess = f'Запишите ваш адрес в виде: ул.ХХХ д.ХХ эт.Х кв.ХХ\n Если вы обладатель частного дома, ' \
                       f'квартиру и ' \
                       f'этаж не писать.'
                bot.send_message(call.message.chat.id, mess, parse_mode='html')
                say = True

            else:
                markup = edit_and_yes()
                bot.send_message(call.message.chat.id, "Ваш адрес: " + address + ", верно?", reply_markup=markup)

        # -----------Инлайн кнопка изменить--------------------------
        elif call.data == 'edit':
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
            with open('json/address.json', 'r', encoding="utf-8") as file:
                data = json.load(file)

            data[str(call.from_user.id)] = ""
            with open('json/users.json', 'w') as file:
                json.dump(data, file)

            mess = f'Запишите ваш адрес в виде: ул.ХХХ д.ХХ эт.Х кв.ХХ\n Если вы обладатель частного дома, ' \
                   f'квартиру и ' \
                   f'этаж не писать.'
            bot.send_message(call.message.chat.id, mess, parse_mode='html')
            say = True

        # -----------Инлайн кнопка да--------------------------
        elif call.data == 'yes':
            mess = f'Заказ оформлен! Курьер прибудет по адресу:\n'
            with open('json/address.json', 'r', encoding="utf-8") as file:
                data1 = json.load(file)

            with open('json/users.json', 'r', encoding="utf-8") as file:
                data2 = json.load(file)

            with open('json/catalog.json', 'r', encoding="utf-8") as file:
                pizzas = json.load(file)
            address = data1.get(str(call.from_user.id), "")
            mess += address
            mess += '\n' + "Детали: " + '\n'
            basket = data2.get(str(call.from_user.id), [])
            cost = 0
            for pizza_id in basket:
                for pizza in pizzas['response']['items']:
                    if pizza['id_pizza'] == pizza_id:
                        mess += pizza['pizza_name'] + '\n'
                        cost += pizza['price']
            mess += "К оплате: " + str(cost) + " руб."
            bot.send_message(call.message.chat.id, mess, parse_mode='html')
            mess = f'Заказ будет доставлен в течении часа, ожидайте.\nВы можете обратиться с некоторыми вопросами по ' \
                   f'номеру: 80000000000'
            markup = in_menu_keyboard()
            bot.send_message(call.message.chat.id, mess, parse_mode='html', reply_markup=markup)

            with open('json/history.json', 'r', encoding="utf-8") as file:
                data3 = json.load(file)
            history = data3.get(str(call.from_user.id), [])
            order = dict()
            number += 1
            order["id"] = number
            order["address"] = address
            order["order"] = basket
            order["status"] = ""
            order["datetime"] = datetime.now().strftime('%d.%m.%y')
            order["price"] = cost
            history.append(order)
            data3[str(call.from_user.id)] = history
            with open('json/history.json', 'w') as file:
                json.dump(data3, file)

            data2[str(call.from_user.id)] = []
            with open('json/users.json', 'w') as file:
                json.dump(data2, file)

        # -----------Инлайн кнопка вернуться--------------------------
        elif call.data == 'back_one':
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)

        # -----------Инлайн кнопка в главное меню--------------------------
        elif call.data == 'back':
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
            name = call.from_user.first_name
            mess = f'Привет, <b>{name}</b>. ' \
                   f'BotPizza🍕 - прототип бота, который доставляет еду. '

            photo_pic = open('pic.png', 'rb')
            markup = main_keyboard()
            bot.send_photo(call.message.chat.id, photo_pic, caption=mess, parse_mode='html', reply_markup=markup)


# ----------------------------------------TEXT-------------------------------------------------------#

@bot.message_handler(content_types=['text'])
def get_user_text(message):
    global say
    if message.text == "Привет":
        bot.send_message(message.chat.id, "И тебе привет!", parse_mode='html')

    if say:
        with open('json/address.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        if len(message.text) > 6:
            address = message.text
            data[str(message.from_user.id)] = address
            with open('json/address.json', 'w') as file:
                json.dump(data, file)
            markup = edit_and_yes()
            bot.send_message(message.chat.id, "Ваш адрес: " + address + ", верно?",
                             reply_markup=markup)
            say = False
        else:
            bot.send_message(message.chat.id,
                             "Возможно вы неправильно ввели адрес, повторите попытку.", parse_mode='html')


bot.polling(none_stop=True)
