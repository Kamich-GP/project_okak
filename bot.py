# Основной функционал бота
import telebot
import buttons
import database


# Создаем объект бота
bot = telebot.TeleBot('TOKEN')
# Временные данные
users = {}


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if database.check_user(user_id):
        bot.send_message(user_id, 'Добро пожаловать!',
                        reply_markup=telebot.types.ReplyKeyboardRemove())
        bot.send_message(user_id, 'Выберите пункт меню:',
                         reply_markup=buttons.main_menu(database.get_pr_buttons()))
    else:
        bot.send_message(user_id, 'Здравствуйте! Давайте начнем регистрацию!'
                                  'Напишите свое имя',
                         reply_markup=telebot.types.ReplyKeyboardRemove())
        # Переход на этап получения имени
        bot.register_next_step_handler(message, get_name)


# Этап получения имени
def get_name(message):
    user_id = message.from_user.id
    user_name = message.text
    bot.send_message(user_id, 'Отлично! Теперь отправьте свой номер!',
                     reply_markup=buttons.num_button())
    # Переход на этап получения номера
    bot.register_next_step_handler(message, get_num, user_name)


# Этап получения номера
def get_num(message, user_name):
    user_id = message.from_user.id
    # Проверка на правильность номера
    if message.contact:
        user_num = message.contact.phone_number
        database.register(user_id, user_name, user_num)
        bot.send_message(user_id, 'Регистрация прошла успешно!',
                         reply_markup=telebot.types.ReplyKeyboardRemove())
    else:
        bot.send_message(user_id, 'Отправьте ваш номер по кнопке!')
        # Возвращение на этап получения номера
        bot.register_next_step_handler(message, get_num, user_name)


# Обработка выбора количества товара
@bot.callback_query_handler(lambda call: call.data in ['increment', 'decrement', 'to_cart', 'back'])
def choose_pr_count(call):
    user_id = call.message.chat.id
    if call.data == 'increment':
        user_count = users[user_id]['product_count']
        stock = database.get_exact_pr(users[user_id]['product_name'])[3]
        if user_count < stock:
            bot.edit_message_reply_markup(chat_id=user_id, message_id=call.message.message_id,
                                          reply_markup=buttons.choose_pr_count(stock,
                                                                               'increment',
                                                                               user_count))
            users[user_id]['product_count'] += 1
    elif call.data == 'decrement':
        user_count = users[user_id]['product_count']
        stock = database.get_exact_pr(users[user_id]['product_name'])[3]
        if 1 < user_count:
            bot.edit_message_reply_markup(chat_id=user_id, message_id=call.message.message_id,
                                          reply_markup=buttons.choose_pr_count(stock,
                                                                               'decrement',
                                                                               user_count))
            users[user_id]['product_count'] -= 1
    elif call.data == 'to_cart':
        user_pr = database.get_exact_pr(users[user_id]['product_name'])[1]
        user_count = users[user_id]['product_count']
        database.add_to_cart(user_id, user_pr, user_count)
        bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
        bot.send_message(user_id, 'Товар успешно занесен в корзину!',
                         reply_markup=buttons.main_menu(database.get_pr_buttons()))
    elif call.data == 'back':
        bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
        bot.send_message(user_id, 'Выберите пункт меню:',
                         reply_markup=buttons.main_menu(database.get_pr_buttons()))


# Работа с корзиной
@bot.callback_query_handler(lambda call: call.data in ['cart', 'order', 'clear'])
def cart_handle(call):
    user_id = call.message.chat.id
    if call.data == 'cart':
        text = 'Ваша корзина:\n\n'
        total = 0
        user_cart = database.show_cart(user_id)
        if user_cart:
            for i in user_cart:
                text += (f'Продукт: {i[1]}\n'
                         f'Количество: {i[2]}\n\n')
                total += database.get_price(i[1]) * i[2]
            text += f'Итого: {total}сум'
            bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
            bot.send_message(user_id, text, reply_markup=buttons.cart_buttons())
    elif call.data == 'clear':
        bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
        database.clear_cart(user_id)
        bot.send_message(user_id, 'Ваша корзина очищена!',
                         reply_markup=buttons.main_menu(database.get_pr_buttons()))
    elif call.data == 'order':
        text = (f'Новый заказ!\n'
                f'Клиент @{call.message.chat.username}\n\n')
        total = 0
        user_cart = database.show_cart(user_id)
        if user_cart:
            for i in user_cart:
                text += (f'Продукт: {i[1]}\n'
                         f'Количество: {i[2]}\n\n')
                total += database.get_price(i[1]) * i[2]
            text += f'Итого: {total}сум'
            bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
            bot.send_message(user_id, 'Отправьте локацию, куда вам доставить заказ',
                             reply_markup=buttons.loc_button())
            # Переход на этап получения локации
            bot.register_next_step_handler(call.message, get_loc, text)


# Этап получения локации
def get_loc(message, text):
    user_id = message.from_user.id
    if message.location:
        bot.send_message(-4931963577, text)
        bot.send_location(-4931963577, latitude=message.location.latitude,
                          longitude=message.location.longitude)
        database.make_order(user_id)
        bot.send_message(user_id, 'Ваш заказ успешно оформлен! Скоро с вами свяжутся!',
                         reply_markup=telebot.types.ReplyKeyboardRemove())
        start(message)
    else:
        bot.send_message(user_id, 'Отправьте локацию по кнопке!')
        # Возвращение на этап получения локации
        bot.register_next_step_handler(message, get_loc, text)


# Обработка выбора товара
@bot.callback_query_handler(lambda call: int(call.data) in [i[0] for i in database.get_all_pr()])
def choose_product(call):
    user_id = call.message.chat.id
    pr_info = database.get_exact_pr(int(call.data))
    bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
    bot.send_photo(user_id, photo=pr_info[-1], caption=f'{pr_info[1]}\n\n'
                                                       f'Описание: {pr_info[2]}\n'
                                                       f'Цена: {pr_info[4]}сум',
                   reply_markup=buttons.choose_pr_count(pr_info[3]))
    users[user_id] = {'product_name': int(call.data), 'product_count': 1}


# Запуск бота
bot.polling(non_stop=True)
