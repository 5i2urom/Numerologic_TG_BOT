import telebot
from telebot import types
from calculate import *
from config import TG_TOKEN, PASSWORD
import datetime

bot = telebot.TeleBot(TG_TOKEN)


# Список команд и их описания
commands = [
    telebot.types.BotCommand("/start", "Старт"),
    telebot.types.BotCommand("/count", "Вычислить")
]

# Установка команд
bot.set_my_commands(commands)
my_commands = [com.command for com in bot.get_my_commands()]

with open('users.txt', 'r') as file:
    authorized = [int(line.rstrip()) for line in file]

# выполнить команду
def handle_command(message):
    command = message.text
    if command == '/start':
        start(message)
    elif command == '/count':
        count(message)

def authorize(message):
    if message.chat.id not in authorized:
        bot.send_message(message.chat.id, "Введите пароль")
        bot.register_next_step_handler(message, input_password)
    else:
        bot.send_message(message.chat.id, "Вы уже авторизованы!")

def input_password(message):
    if message.text[1:] in my_commands:
        handle_command(message)
    elif message.text == PASSWORD:
        authorized.append(message.chat.id)
        with open('users.txt', 'a') as file:
            file.write(f'{message.chat.id}\n')
        go_count = types.InlineKeyboardMarkup()
        go_count_button = types.InlineKeyboardButton(text='Посчитать человека', callback_data='go_count')
        go_count.add(go_count_button)
        bot.send_message(message.chat.id, f"Привет, {message.chat.first_name} :)", reply_markup=go_count)
    else:
        bot.send_message(message.chat.id, "Неверный пароль. Попробуйте еще раз!")
        bot.register_next_step_handler(message, input_password)

# Старт
@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id not in authorized:
        authorize(message)
    else:
        go_count = types.InlineKeyboardMarkup()
        go_count_button = types.InlineKeyboardButton(text='Посчитать человека', callback_data='go_count')
        go_count.add(go_count_button)
        bot.send_message(message.chat.id, f"Привет, {message.chat.first_name} :)", reply_markup=go_count)

# Посчитать человека
@bot.message_handler(commands=['count'])
def count(message):
    if message.chat.id not in authorized:
        authorize(message)
    else:    
        # удаление кнопок Верно/Исправить
        bot.send_message(message.chat.id, "Введите имя человека")
        th_msgs = [message.message_id, message.message_id+1]
        bot.register_next_step_handler(message, input_name, th_msgs) # ожидание ввода имени

# Ввод имени
def input_name(message, th_msgs):
    if message.chat.id not in authorized:
        authorize(message)
    elif message.text[1:] in my_commands: handle_command(message)
    else:        
        name = message.text
        th_msgs.append(message.message_id)
        th_msgs.append(message.message_id+1)
        bot.send_message(message.chat.id, "Введите дату рождения человека в формате ДД.ММ.ГГГГ")
        bot.register_next_step_handler(message, input_date, name, th_msgs) # ожидание ввода др

# Ввод др
def input_date(message, name, th_msgs): 
    if message.chat.id not in authorized:
        authorize(message)
    elif message.text[1:] in my_commands: handle_command(message)
    else:
        th_msgs.append(message.message_id)
        date = message.text
        if check_date(date):
            check_info(message, name, date, th_msgs)
        else:
            bot.send_message(message.chat.id, "Введите дату рождения человека в формате ДД.ММ.ГГГГ")
            th_msgs.append(message.message_id+1)
            bot.register_next_step_handler(message, input_date, name, th_msgs)

# Предложение проверить инфу
def check_info(message, name, date, th_msgs):
    if message.chat.id not in authorized:
        authorize(message)
    else:
        for each_msg in th_msgs:
            try:
                bot.delete_message(message.chat.id, each_msg)
            except telebot.apihelper.ApiTelegramException as e:
                print(f"Ошибка удаления сообщения: {e}")
        check_keyboard = types.InlineKeyboardMarkup()
        check_keyboard.add(types.InlineKeyboardButton(text = "Верно", callback_data = f"correct_{name}_{date}"))
        check_keyboard.add(types.InlineKeyboardButton(text = "Исправить", callback_data = "change"))
        bot.send_message(message.chat.id, f"{name}\n{date}\n",
                        reply_markup = check_keyboard)

# обработка кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.message.chat.id not in authorized:
        bot.answer_callback_query(call.id) 
        authorize(call.message)

    elif call.data == "go_count":
        bot.answer_callback_query(call.id) 
        bot.clear_step_handler(call.message)
        count(call.message)
        
    elif call.data == "change":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id) 
        bot.clear_step_handler(call.message)
        count(call.message)

    elif call.data.startswith("correct"):    
        bot.answer_callback_query(call.id) 
        bot.clear_step_handler(call.message)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                        message_id=call.message.message_id, reply_markup=None)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        data = call.data.split("_")
        name = data[1]
        date = data[2]
        show_info(call.message, name, date)

def show_info(message, name, date):
    if message.chat.id not in authorized:
        authorize(message)
    else:   
        res_dict = calculate(date)[0]
        res_str = calculate(date)[1]
        all_str = ''
        for v in res_dict.values():
            my_str = '\t• ' + v + '\n'
            all_str = all_str + my_str
        final_msg = f"Имя: {name}\nДата рождения: {res_str}\n{all_str}" 
        bot.send_message(message.chat.id, final_msg)
        with open('info.txt', 'a') as file2:
            cur_time = datetime.datetime.now()
            file2.write(f'User: {message.chat.first_name} Date: {cur_time}\n{final_msg}\n')        
if __name__ == "__main__":
    # Запуск бота
    bot.infinity_polling()