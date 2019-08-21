import logging
import sys
import os
from contextlib import contextmanager
from io import StringIO

from telegram.ext import Updater, CommandHandler
from telegram.error import TimedOut, NetworkError
from telegram import ParseMode

log = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)-15s %(name)s %(message)s',
    stream=sys.stdout
)


namespaces = {}


def namespace_of(chat):
    if chat not in namespaces:
        namespaces[chat] = {'__builtins__': globals()['__builtins__']}

    return namespaces[chat]


@contextmanager
def redirected_stdout():
    old = sys.stdout
    stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old


def log_input(update):
    user = update.effective_user.id
    chat = update.effective_chat.id
    log.info(f"IN: {update.message.text} (user={user}, chat={chat})")


def send(msg, bot, update):
    log.info(f"OUT: '{msg}'")
    bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"`{msg}`",
        parse_mode=ParseMode.MARKDOWN
    )


def evaluate(bot, update):
    do(eval, bot, update)


def execute(bot, update):
    do(exec, bot, update)


def do(func, bot, update):
    log_input(update)
    content = update.message.text.split(' ', 1)[-1]

    output = ""

    try:
        with redirected_stdout() as stdout:
            func_return = func(content, namespace_of(update.message.chat_id))

            if stdout.getvalue():
                output += str(stdout.getvalue()) + "\n"

            if func_return is not None:
                output += str(func_return)

    except Exception as e:
        output = str(e)

    output = output.strip()

    if output == "":
        output = "No output."

    send(output, bot, update)


def clear(bot, update):
    log_input(update)
    global namespaces
    if update.message.chat_id in namespaces:
        del namespaces[update.message.chat_id]
    send("Cleared locals.", bot, update)


def error_callback(bot, update, error):
    try:
        raise error
    except (TimedOut, NetworkError):
        log.debug(error, exc_info=True)
    except:
        log.info(error, exc_info=True)


if __name__ == '__main__':
    log.info("Initializing bot")
    token = os.environ.get("BOT_TOKEN")
    updater = Updater(token)
    updater.dispatcher.add_handler(CommandHandler(('e', 'ev', 'eva', 'eval'), evaluate))
    updater.dispatcher.add_handler(CommandHandler(('x', 'ex', 'exe', 'exec'), execute))
    updater.dispatcher.add_handler(CommandHandler('clear', clear))
    updater.dispatcher.add_error_handler(error_callback)
    updater.start_polling()

    log.info("Bot initialized")
    updater.idle()
