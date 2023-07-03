from telebot import types


def main_keyboard():
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton('Каталог', callback_data='menu')
    button2 = types.InlineKeyboardButton('Ваши заказы', callback_data='history')
    markup.row(button1, button2)
    return markup


def basket_keyboard():
    markup = types.InlineKeyboardMarkup()
    basket = types.InlineKeyboardButton('Корзина', callback_data='basket')
    markup.row(basket)
    return markup


def back_to_one_and_accept():
    markup = types.InlineKeyboardMarkup()
    accept = types.InlineKeyboardButton('Оформить заказ!', callback_data='accept')
    back_one = types.InlineKeyboardButton('Вернуться', callback_data='back_one')
    markup.row(accept)
    markup.row(back_one)
    return markup


def only_back():
    markup = types.InlineKeyboardMarkup()
    back_one = types.InlineKeyboardButton('Вернуться', callback_data='back_one')
    markup.row(back_one)
    return markup


def back_ones():
    markup = types.InlineKeyboardMarkup()
    back_one = types.InlineKeyboardButton('Вернуться', callback_data='back_one')
    markup.row(back_one)
    return markup


def in_menu_keyboard():
    markup = types.InlineKeyboardMarkup()
    back = types.InlineKeyboardButton('В меню', callback_data='back')
    markup.row(back)
    return markup


def add_dell_keyboard(id_piz):
    markup = types.InlineKeyboardMarkup()
    add = types.InlineKeyboardButton('Добавить', callback_data='add_to_basket_' + str(id_piz))
    dell = types.InlineKeyboardButton('Убрать', callback_data='dell_from_basket_' + str(id_piz))
    markup.row(add, dell)
    return markup


def edit_and_yes():
    markup = types.InlineKeyboardMarkup()
    edit = types.InlineKeyboardButton('Изменить', callback_data='edit')
    yes = types.InlineKeyboardButton('Да', callback_data='yes')
    markup.row(edit, yes)
    return markup
