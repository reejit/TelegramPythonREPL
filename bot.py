import logging
import sys
import contextlib
from io import StringIO
from collections import defaultdict

from telegram.ext import Updater, CommandHandler
from telegram import ParseMode

log = logging.getLogger(__name__)
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)-15s %(name)s %(message)s'
)

token = "CHANGE ME"

memory = defaultdict(dict)


@contextlib.contextmanager
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
    content = update.message.text[6:]
    chat_id = update.effective_chat.id

    output = ""

    try:
        with redirected_stdout() as stdout:
            func_return = func(content, globals(), memory[chat_id])
            func_stdout = stdout.getvalue() if stdout.getvalue() != '' else None

            if func_return is not None:
                output += str(func_return)

            if func_stdout is not None:
                output += str(func_stdout)

    except Exception as e:
        output = str(e)

    output = output.strip()

    if output == "":
        output = "No output."

    send(output, bot, update)


def clear(bot, update):
    log_input(update)
    global memory
    memory[update.message.chat_id] = {}
    send("Cleared locals.", bot, update)


def local_vars(bot, update):
    log_input(update)
    log.info(f"")
    send(dict(memory[update.message.chat_id]), bot, update)


def main():
    log.info("Initializing bot")
    updater = Updater(token)
    updater.dispatcher.add_handler(CommandHandler('eval', evaluate))
    updater.dispatcher.add_handler(CommandHandler('exec', execute))
    updater.dispatcher.add_handler(CommandHandler('clear', clear))
    updater.dispatcher.add_handler(CommandHandler('locals', local_vars))
    updater.start_polling()

    log.info("Bot initialized")
    updater.idle()


if __name__ == '__main__':
    main()
