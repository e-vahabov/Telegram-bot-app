import telebot
import sub_module as sub
import requests
import os
from config import TOKEN
from telebot import types
from io import BytesIO
from PIL import Image
from sub_module import btn_replies, bot_msg, files

bot = telebot.TeleBot(TOKEN)

engaged_saving = False

# 'help' command
@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id, sub.construct_help(message.from_user), parse_mode='html')

# 'creator' command
@bot.message_handler(commands=['creator'])
def creator(message):
    bot.send_message(message.chat.id, bot_msg['creator'])

# 'start' command or start of the conversation
@bot.message_handler(commands=['start'])
def start(message):
    # constructing first button with intro text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(btn_replies['intro']))

    # sending greeting + button
    bot.send_message(message.chat.id, sub.construct_greeting(message.from_user),
            parse_mode='html', reply_markup=markup)


@bot.message_handler(func=lambda m: m.text == btn_replies['intro'])
def docs_request(message):
    # ASKING, DOES USER HAVE REQUIRED DOCS, THROWING THREE OPTIONS TO CHOOSE IN REPLY BUTTONS

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for reply in ('docs_pos_one', 'docs_pos_two', 'docs_negative'):
        markup.add(types.KeyboardButton(btn_replies[reply]))

    bot.send_message(message.chat.id, bot_msg['cscs_request'], reply_markup=markup)


@bot.message_handler(func=lambda m: m.text == btn_replies['docs_negative'])
def docs_negative_respond_handler(message):
    # SENDING REFUSE MESSAGE TO USER (RESPOND TO HIS NEGATIVE REPLY ABOUT NECESSARY DOCS), REMOVING BUTTONS
    bot.send_message(message.chat.id, bot_msg['no_docs_respond'], reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(func=lambda m: m.text in sub.pos_docs_responds())
def respond_with_instructions(message):
    global engaged_saving

    engaged_saving = True

    bot.send_message(message.chat.id, 'Great! 😉', reply_markup=types.ReplyKeyboardRemove())

    # adding screenshot question to info user questions based on user docs respond
    idx = 1 if message.text == btn_replies['docs_pos_one'] else 0
    sub.add_screenshot_question(idx)

    # reactivating iterable with questions for sending consecutive questions with the help of 'next()'
    sub.user_info_questions_iter = iter(sub.user_info_questions)

    try:
        bot.send_message(message.chat.id, next(sub.user_info_questions_iter))
    except StopIteration:
        pass


@bot.message_handler(func=lambda m: m.text in (btn_replies['docs_sent'], 'I have sent'))
def user_sent_docs_handler(message):

    global engaged_saving

    if engaged_saving:
        # SENDING USER'S INFO THROUGH SECOND BOT
        sub.send_employee_info(message.from_user.id, message.from_user.username)
        engaged_saving = False

    # SENDING SUCCESS MESSAGE
    bot.send_message(message.chat.id, bot_msg['success_msg'],
                     parse_mode='html', reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(content_types=['text'])
def text(message):

    if engaged_saving: # global variable 'engaged_saving' accessed inside function
                       # cause later won't be overridden
        sub.info_box.append(message.text)
        # sending text request for certain type of info from user
        try:
            msg = next(sub.user_info_questions_iter)

            if msg in sub.user_screenshot_inquiries:
                sharecode, cscs = open(files['sharecode'], 'rb'), \
                                  types.InputMediaPhoto(open(files['cscs'], 'rb'), caption=msg)
                #asking only for sharecode with example
                if msg == sub.user_screenshot_inquiries[0]:
                    bot.send_photo(chat_id=message.chat.id, photo=sharecode, caption=msg)
                #asking for sharecode and CSCS with examples
                else:
                    bot.send_media_group(message.chat.id, [types.InputMediaPhoto(sharecode), cscs])
            elif msg == sub.user_info_questions[-1]:
                reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                reply_markup.add(types.KeyboardButton(btn_replies['docs_sent']))
                bot.send_message(message.chat.id, msg, reply_markup=reply_markup)
            else:
                bot.send_message(message.chat.id, msg)
        except StopIteration:
            pass


@bot.message_handler(content_types=['photo'])
def photo(message):

    if engaged_saving:
        try:
            msg = next(sub.user_info_questions_iter)
            if msg == sub.user_info_questions[-1]:
                reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                reply_markup.add(types.KeyboardButton(btn_replies['docs_sent']))
                bot.send_message(message.chat.id, msg, reply_markup=reply_markup)
        except StopIteration:
            pass

        file = bot.get_file(message.photo[-1].file_id)

        response = requests.get(f'https://api.telegram.org/file/bot{TOKEN}/{file.file_path}')

        img = Image.open(BytesIO(response.content))

        directory = f'pics/users/{message.from_user.id}/'

        if not os.path.isdir(directory):
            os.mkdir(directory)

        img.save(directory + file.file_path[7:])


bot.polling(none_stop=True)