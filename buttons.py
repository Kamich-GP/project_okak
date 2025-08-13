# Файл с кнопками для бота
from telebot import types


# Кнопка отправки номера телефона
def num_button():
    # Создаем пространство
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # Создаем сами кнопки
    but1 = types.KeyboardButton('Отправить номер📞', request_contact=True)
    # Добавляем кнопки в пространство
    kb.add(but1)
    return kb


# Кнопки вывода товаров
def main_menu(products):
    # Создаем пространство
    kb = types.InlineKeyboardMarkup(row_width=2)
    # Создаем сами кнопки
    cart = types.InlineKeyboardButton(text='Корзина🛒', callback_data='cart')
    all_products = [types.InlineKeyboardButton(text=f'{i[1]}', callback_data=i[0])
                    for i in products]
    # Добавляем кнопки в пространство
    kb.add(*all_products)
    kb.row(cart)
    return kb


# Кнопки выбора кол-ва товара
def choose_pr_count(pr_count, plus_or_minus='', amount=1):
    # Создаем пространство
    kb = types.InlineKeyboardMarkup(row_width=3)
    # Создаем сами кнопки
    plus = types.InlineKeyboardButton(text='+', callback_data='increment')
    minus = types.InlineKeyboardButton(text='-', callback_data='decrement')
    count = types.InlineKeyboardButton(text=str(amount), callback_data=str(amount))
    back = types.InlineKeyboardButton(text='Назад🔙', callback_data='back')
    to_cart = types.InlineKeyboardButton(text='В корзину🛒', callback_data='to_cart')
    # Алгоритм изменения кол-ва товара
    if plus_or_minus == 'increment':
        if amount < pr_count:
            count = types.InlineKeyboardButton(text=str(amount+1), callback_data=str(amount+1))
    elif plus_or_minus == 'decrement':
        if 1 < amount:
            count = types.InlineKeyboardButton(text=str(amount-1), callback_data=str(amount-1))
    # Добавляем кнопки в пространство
    kb.add(minus, count, plus)
    kb.row(back, to_cart)
    return kb
