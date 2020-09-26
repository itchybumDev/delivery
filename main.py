import configparser
import logging
import sys

import requests
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.ext.dispatcher import run_async

import Admin as ad
from PortfolioUpdate import generate_email
from const import START_TEXT, HELP_TEXT, HELP_ADMIN_TEXT, CONTACT_INFO_TEXT, PLEASE_TRY_AGAIN
from logging_handler import logInline
from model.Job import Job

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

config = configparser.ConfigParser()
config.read('config.ini')

chanel_id = [-1001208445787]



@run_async
def unknown(update, context):
    send_plain_text(update, context, "Sorry, I didn't understand that command.\nRun /help to see available options")


@logInline
def start(update, context):
    ad.addUser(update.effective_chat.id, update.effective_user)
    send_html_text(update, context, START_TEXT.format(update.effective_user.full_name))

def send_plain_text(update, context, text):
    context.bot.send_message(update.effective_chat.id, text=text)


def send_html_text(update, context, text):
    context.bot.send_message(update.effective_chat.id, text=text, parse_mode=telegram.ParseMode.HTML)


def get_url():
    contents = requests.get('https://random.dog/woof.json').json()
    url = contents['url']
    return url


@run_async
@logInline
def dog(update, context):
    url = get_url()
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=url)


@run_async
@logInline
def email(update, context):
    # my_portfolio = {'AMZN': [5,1895.85], 'BLK': [10, 538.505],'TWTR': [280, 36.2], 'C':[50, 79.8]}
    user = ad.getUser(update.effective_chat.id)
    email_address = context.args[0]
    try:
        generate_email(user.my_portfolio, email_address)
        send_plain_text(update, context, "Email Sent")
    except:
        send_plain_text(update, context, PLEASE_TRY_AGAIN)


@run_async
@logInline
def _help(update, context):
    send_html_text(update, context, HELP_TEXT)


@logInline
@run_async
def contact_us(update, context):
    send_html_text(update, context, CONTACT_INFO_TEXT)


@logInline
@run_async
def contact(update, context):
    msg = ' '.join(context.args)
    msg_edited = "chat_id {} \nmsg: {}".format(update.effective_chat.id, msg)
    dev_team = ad.getDevTeam()
    for dev in dev_team:
        context.bot.send_message(dev, text=msg_edited)
    send_plain_text(update, context, "We have received your message, we will respond in a short while!")


def error_handler(update, context):
    send_plain_text(update, context, str("Something is missing! Please try again"))
    logger.error(" Error in Telegram Module has Occurred:", exc_info=True)


class authorize:
    def __init__(self, f):
        self._f = f

    def __call__(self, *args):
        if str(args[0].effective_chat.id) in ad.getDevTeam():
            return self._f(*args)
        else:
            raise Exception('Alpaca does not want to you use this command.')


@authorize
@run_async
def get_all_user(update, context):
    msg = ad.getAllUser()
    send_plain_text(update, context, msg)


@authorize
@run_async
def number_of_user(update, context):
    numb_user = ad.getNumberOfUser(update.effective_chat.id)
    send_plain_text(update, context, "Number of users: {}".format(numb_user))


@authorize
@run_async
def help_admin(update, context):
    send_html_text(update, context, HELP_ADMIN_TEXT)


@authorize
@run_async
def add_admin(update, context):
    ad.addDevTeam(update.effective_chat.id)
    send_plain_text(update, context,
                    "Added Dev: {} \n{}".format(update.effective_chat.id, update.effective_chat.full_name))

@authorize
@run_async
def broadcast(update, context):
    msg = ' '.join(context.args)
    user_dict = ad.getUserDict()
    for chat_id in user_dict.keys():
        context.bot.send_message(chat_id, text=msg)
    send_plain_text(update, context, "Broadcast the message to {} users".format(len(user_dict.keys())))


@authorize
@run_async
def reply(update, context):
    reply_chat_id = context.args[0]
    msg = ' '.join(context.args[1:])
    context.bot.send_message(reply_chat_id, text=msg)
    send_plain_text(update, context, "Reply to {} done".format(reply_chat_id))


def notifyAdmin(text, context):
    dev_team = ad.getDevTeam()
    for dev in dev_team:
        context.bot.send_message(dev, text=text)

@authorize
def remove_job(update, context):
    # address,note
    jobId = context.args[0]
    ad.removeJob(jobId)
    for i in ad.getCurrentJobs():
        send_plain_text(update, context, i.toString())


@authorize
def add_job(update, context):
    # address,note
    msg = ' '.join(context.args).split('#')
    ad.createNewJob(msg[0], msg[1])
    for job in ad.getCurrentJobs().values():
        send_plain_text(update, context, job.toString())
    publishJobsOnChanel(context, update)


def publishJobsOnChanel(context, update):
    finalMsg = ''
    for job in ad.getCurrentJobs().values():
        # Publish to channel
        if job.state == "Unassigned":
            finalMsg += job.toString() + '\n'
    if finalMsg != '':
        keyboard = [
            [InlineKeyboardButton("Register for job", url="https://t.me/Portfolo_Bot")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        # Send message with text and appended InlineKeyboard
    for chanel in chanel_id:
        context.bot.send_message(chanel, text=finalMsg, reply_markup=reply_markup)


@authorize
def mark_done(update, context):
    jobId = context.args[0]

    if int(jobId) not in ad.getCurrentJobs().keys():
        msg = 'The job that you are looking for is no longer exist'
        send_plain_text(update, context, msg)
    else:
        assignee = ad.getCurrentJobs()[int(jobId)].assignee
        text = "You have successfully DONE \n{}".format(ad.getCurrentJobs()[int(jobId)].toString())
        context.bot.send_message(assignee, text=text)
        msg = ad.markDone(jobId)
        notifyAdmin(msg, context)


@authorize
@run_async
def list_job(update, context):
    msg = ''
    for job in ad.getCurrentJobs().values():
        msg += job.toStringAdmin()
        if job.assignee is not None and job.assignee != '':
            msg += ad.getUser(job.assignee).toString() + '\n'
        msg += '-----------------\n'

    send_plain_text(update, context, msg)


@run_async
def active_job(update, context):
    msg = ''
    for job in ad.getCurrentJobs().values():
        if job.state == "Unassigned":
            msg += job.toString() + '\n'

    if msg == '':
        msg = 'There is currently no active job, please check back later'

    send_plain_text(update, context, msg)


@run_async
def take_job(update, context):
    jobId = context.args[0]
    if int(jobId) not in ad.getCurrentJobs().keys() or ad.getCurrentJobs()[int(jobId)].state != 'Unassigned':
        msg = 'The job that you are looking for is no longer exist'
        send_plain_text(update, context, msg)
    else:
        curr_job = ad.getCurrentJobs()[int(jobId)]
        msg = "You have successfully registered your interest for \n{}".format(curr_job.toString())
        curr_job.set_state('Assigned')
        curr_job.set_assignee(update.effective_chat.id)
        send_plain_text(update, context, msg)
        # Notify Admin
        text = ad.getUser(curr_job.assignee).toString() + '\n'
        text += '\nhas taken job' + '\n\n'
        text += ad.getCurrentJobs()[int(jobId)].toString()
        notifyAdmin(text, context)
        ad.saveJobs()

        publishJobsOnChanel(context, update)


@run_async
def abandon_job(update, context):
    jobId = context.args[0]
    if int(jobId) in ad.getCurrentJobs().keys() \
            and ad.getCurrentJobs()[int(jobId)].state == 'Assigned' \
            and ad.getCurrentJobs()[int(jobId)].assignee == update.effective_chat.id:
        msg = 'You have abandoned job\n{}'.format(ad.getCurrentJobs()[int(jobId)].toString())
        send_plain_text(update, context, msg)
        ad.getCurrentJobs()[int(jobId)].state = 'Unassigned'
        ad.getCurrentJobs()[int(jobId)].assignee = None

        text = ad.getUser(update.effective_chat.id).toString() + '\n'
        text += '\nhas abandoned job' + '\n\n'
        text += ad.getCurrentJobs()[int(jobId)].toString()
        notifyAdmin(text, context)
        ad.saveJobs()
    else:
        msg = 'The job you are trying to access is no longer there'
        send_plain_text(update, context, msg)



@run_async
def my_current_job(update, context):
    userId = update.effective_chat.id
    msg = ''
    for job in ad.getCurrentJobs().values():
        if job.assignee == userId:
            msg = job.toString() + '\n'
    send_plain_text(update, context, msg)


def main():
    ad.startAdmin()
    updater = Updater(config['telegram']['token_dev'], use_context=True)
    dp = updater.dispatcher

    commands = [
        ["start", start],
        ["help", _help],
        ["my_current_job", my_current_job],
        ["jobs", active_job],
        ["take_job", take_job],
        ["abandon", abandon_job],
        ["contact_us", contact_us],
        ["contact", contact]
    ]
    for command, function in commands:
        updater.dispatcher.add_handler(CommandHandler(command, function))

    admin_commands = [
        ["get_all_user", get_all_user],
        ["number_of_user", number_of_user],
        ["add_job", add_job],
        ["remove_job", remove_job],
        ["list_job", list_job],
        ["help_admin", help_admin],
        ["add_admin", add_admin],
        ["broadcast", broadcast],
        ["mark_done", mark_done],
        ["reply", reply],
    ]

    for command, function in admin_commands:
        updater.dispatcher.add_handler(CommandHandler(command, function))

    dp.add_handler(MessageHandler(Filters.command, unknown))
    dp.add_handler(MessageHandler(Filters.text, unknown))

    dp.add_error_handler(error_handler)
    updater.start_polling(poll_interval=1.0, timeout=20)
    updater.idle()


if __name__ == '__main__':
    logger.info("Starting Bot")
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Terminated using Ctrl + C")
    ad.stopAdmin()
    logger.info("Exiting Bot")
    sys.exit()
