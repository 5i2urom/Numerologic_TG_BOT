import telebot
from telebot import types
from calculate import *
from config import TG_TOKEN
from script import insert_execute

bot = telebot.TeleBot(TG_TOKEN)


# Список команд и их описания
commands = [
    telebot.types.BotCommand("/start", "Старт"),
    #telebot.types.BotCommand("/help", "Получить справку"),
    telebot.types.BotCommand("/count", "Посчитать человека")
]

# Установка команд
bot.set_my_commands(commands)
my_commands = [com.command for com in bot.get_my_commands()]

CORRECT_ID = -1
SKIP_ID = -1

# выполнить команду
def handle_command(message):
    command = message.text
    if command == '/start':
        start(message)
    elif command == '/count':
        count(message)

# Старт
@bot.message_handler(commands=['start'])
def start(message):
    global CORRECT_ID, SKIP_ID
    # удаление кнопок Верно/Исправить
    if CORRECT_ID > -1:
        bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=CORRECT_ID, reply_markup=None)
        CORRECT_ID = -1
    if SKIP_ID > -1:
        bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=SKIP_ID, reply_markup=None)
        SKIP_ID = -1

    go_count = types.InlineKeyboardMarkup()
    go_count_button = types.InlineKeyboardButton(text='Посчитать человека', callback_data='go_count')
    go_count.add(go_count_button)
    bot.send_message(message.chat.id, f"Добро пожаловать, {message.from_user.first_name}! С помощью этого бота Вы сможете получить "
                      "информацию о человеке на основании его даты рождения :)", reply_markup=go_count)

# Посчитать человека
@bot.message_handler(commands=['count'])
def count(message):
    global CORRECT_ID, SKIP_ID
    # удаление кнопок Верно/Исправить
    if CORRECT_ID > -1:
        bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=CORRECT_ID, reply_markup=None)
        CORRECT_ID = -1
   
    if SKIP_ID > -1:
        bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=SKIP_ID, reply_markup=None)
        SKIP_ID = -1

    bot.send_message(message.chat.id, "Введите ФИО человека")
    bot.register_next_step_handler(message, input_name) # ожидание ввода имени

# Ввод имени
def input_name(message):
    if message.text[1:] in my_commands: handle_command(message)
    else:
        name = message.text
        bot.send_message(message.chat.id, "Введите дату рождения человека в формате ДД.ММ.ГГГГ")
        bot.register_next_step_handler(message, input_date, name) # ожидание ввода др

# Ввод др
def input_date(message, name): 
    global SKIP_ID
    if message.text[1:] in my_commands: handle_command(message)
    else: 
        date = message.text
        if check_date(date):
            add_info = types.InlineKeyboardMarkup() 
            add_info.add(types.InlineKeyboardButton(text = "Пропустить", callback_data = f"skip_{name}_{date}"))
            bot.send_message(message.chat.id, "Введите дополнительную информацию о человеке",
                            reply_markup=add_info)
            SKIP_ID = message.message_id + 1
            bot.register_next_step_handler(message, input_add, name, date) # ожидание ввода доп. инфы
        else:
            bot.send_message(message.chat.id, "Введите дату рождения человека в формате ДД.ММ.ГГГГ")
            bot.register_next_step_handler(message, input_date, name)

# Ввод доп. инфы
def input_add(message, name, date, default=False):  
    global SKIP_ID    
    if message.text[1:] in my_commands: handle_command(message)
    else:
        if SKIP_ID > -1:
            bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=SKIP_ID, reply_markup=None)
            SKIP_ID = -1
        add = '-' if default else message.text
        check_info(message, name, date, add)

# Предложение проверить инфу
def check_info(message, name, date, add):
    global CORRECT_ID
    check_keyboard = types.InlineKeyboardMarkup()
    check_keyboard.add(types.InlineKeyboardButton(text = "Верно", callback_data = f"correct_{name}_{date}_{add}"))
    check_keyboard.add(types.InlineKeyboardButton(text = "Исправить", callback_data = "change"))
    bot.send_message(message.chat.id, f"ФИО: {name}\nДата рождения: {date}\nДоп. информация: {add}",
                      reply_markup = check_keyboard)
    CORRECT_ID = message.message_id + 1

# обработка кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    global CORRECT_ID, SKIP_ID
    if call.data == "go_count":
        bot.answer_callback_query(call.id) 
        bot.clear_step_handler(call.message)
        count(call.message)
        
    elif call.data.startswith("skip"):
        bot.answer_callback_query(call.id) 
        bot.clear_step_handler(call.message)
        SKIP_ID = -1
        data = call.data.split("_")
        name = data[1]
        date = data[2]
        input_add(call.message, name, date, default=True)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                message_id=call.message.message_id, reply_markup=None)
        
    elif call.data == "change":
        bot.answer_callback_query(call.id) 
        bot.clear_step_handler(call.message)
        count(call.message)

    elif call.data.startswith("correct"):
        bot.answer_callback_query(call.id) 
        bot.clear_step_handler(call.message)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                        message_id=call.message.message_id, reply_markup=None)
        CORRECT_ID = -1
        data = call.data.split("_")
        name = data[1]
        date = data[2]
        add = data[3]
        show_info(call.message, name, date, add)

def show_info(message, name, date, add):
    res = calculate(date)
    q = 0
    all_str = ''
    for v in res.values():
        my_str = nums[q] + ') ' + v + '\n'
        all_str = all_str + my_str
        q+=1
    bot.send_message(message.chat.id, all_str)

    date_f = datetime.strptime(date, '%d.%m.%Y').date()
    insert_execute(name, date_f, add, message.from_user.id)
if __name__ == "__main__":
    # Запуск бота
    bot.infinity_polling()