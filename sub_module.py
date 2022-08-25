import os
import telebot
from config import SUB_TOKEN, recipient_id
from telebot import types

sub_bot = telebot.TeleBot(SUB_TOKEN)


bot_msg = {
    'creator': 'Contact creator: walkfate@gmail.com',
    'cscs_request': 'Do you have right to work(Share code for employer) and CSCS card?\nPlease, pick your option below ⬇',
    'no_docs_respond':
    'Unfortunately, we cannot offer anything if you don\'t have necessary rights to work. 😔',
    'success_msg':
    'Thank you!\n\nWe will look for places closer to your location📍 and contact you soon with our offers. 💼\n\n'
    'You can contact <a href="t.me/+447915639132">our manager</a> by yourself. 💬',
    'help': ", via this bot you are able to find job much faster.\n\n"
            "Please, when it's able, use button replies instead of typing messages manually.",
}


btn_replies = {
    'intro': 'I want to find a job. 👨‍💼',
    'docs_pos_one': "I have right to work and CSCS card. ✅",
    'docs_pos_two': "I have right to work but no CSCS card. ☑️",
    'docs_negative': "I don't have right to work or both. ❌",
    'docs_sent': 'I have sent all required information and photos. ✔'
               }


user_info_questions = [
    'Please, send me your name and surname.',
    'Send me your phone number, please.',
    'Send your postcode, please.',
    'If you have sent everything you wanted - press button "I have sent...✔" in keyboard menu '
    'or just type message: "I have sent".\n'
    'This will submit your information.'
]


user_screenshot_inquiries = (
    'Send screenshot of your share code, please.\n\nExample is attached to this message. 🖼',
    'Send screenshot of your share code and CSCS card photo, please.\n\nExamples is attached to this message. 🖼'
)


files = {
    'sharecode': 'pics/docs_examples/sharecode.jpg',
    'cscs': 'pics/docs_examples/cscs.jpg'
}

info_box = []


def add_screenshot_question(idx):
    user_info_questions.insert(3, user_screenshot_inquiries[idx])


def name_for_greeting(from_user):
    first_name, last_name = from_user.first_name, from_user.last_name

    first_name = ' ' + first_name if first_name else ''
    last_name = ' ' + last_name if last_name else ''

    return f'<strong>{first_name}{last_name}</strong>'


# constructing message text with help, respond to 'help' command
def construct_help(from_user):
    return 'Dear' + name_for_greeting(from_user) + bot_msg['help']


def construct_greeting(from_user):
    return f'Hello, dear{name_for_greeting(from_user)} ✋. How may I help you?'


def instruction(cscs=True):
    line1 = '\n5. CSCS card photo.\n\n' if cscs else '\n\n'
    photo_title = 'Examples of required photos 🖼' if cscs else 'Example of required screenshot 🖼'
    return  ('Great! 😉\n\nPlease, send me:\n'
             "1. First and Last name.\n2. Phone number.\n"
             f"3. Your postcode.\n4. 'Share code' screenshot.{line1}"
             'After you send the photos and information, press the button below.\n\n'
             'We will look for places closer to your location.📍'), photo_title


def pos_docs_responds(): return btn_replies['docs_pos_one'], btn_replies['docs_pos_two']


def send_employee_info(user_id, username):
    employee_link = f't.me/{username}' if username else f'tg://user?id={user_id}'

    user_info_msg_header = f'New [employee]({employee_link}) 👷‍♂\n\n'

    if len(info_box) >= 3:
        user_name, user_number, user_postcode = info_box[:3]
        msg_user_info = f'Name: {user_name} \nPhone number: {user_number} \nPostcode: {user_postcode}'
        if len(info_box) > 3:
            extra_user_info = '\nAdditional info:\n' + '\n'.join(info_box[3:])
            msg_user_info += extra_user_info

        user_info = user_info_msg_header + msg_user_info
    else:
        user_info = user_info_msg_header + '\n'.join(info_box)

    sub_bot.send_message(recipient_id, user_info, parse_mode='Markdown')

    pics_directory = f'pics/users/{user_id}/'

    pics = os.listdir(pics_directory)

    if pics:
        sub_bot.send_media_group(recipient_id,
                             [types.InputMediaPhoto(open(pics_directory + pic, 'rb')) for pic in pics],
                             disable_notification=True)

    # deleting user's info
    info_box.clear()

    for pic in pics:
        os.remove(pics_directory + pic)
