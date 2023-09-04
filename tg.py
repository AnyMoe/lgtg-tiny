import logging
import os
import uuid
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import filters, Updater, ApplicationBuilder, ContextTypes, CommandHandler, \
    MessageHandler
from pingtrace import lg
from dotenv import load_dotenv, find_dotenv


# FORMAT = '%(asctime)s %(func)-5s %(user)-15s %(username)-8s %(message)s'
# logging.basicConfig(format=FORMAT)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Hello " + update.message.chat.full_name)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.message)
    await context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.message.message_id,
                                   text=update.message.text)


async def mua(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_sticker(chat_id=update.effective_chat.id, reply_to_message_id=update.message.message_id,
                                   sticker="CAACAgUAAxkBAANaY2onc5e20NIp9e3gEbGUAAHhKh9wAAJzAwACav2BVjrZqFlFDhf5KwQ")


async def gen_uuid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = '```' + str(uuid.uuid4()) + '```'
    await context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.message.message_id,
                                   parse_mode=ParseMode.MARKDOWN_V2, text=text)


async def ping_trace_mtr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    input_msg = message.text.split()
    print(input_msg)
    # request = {
    #     'func': "ping_trace_mtr",
    #     'user': message.chat.full_name,
    #     'username': message.chat.username,
    #     'request': message.text
    # }
    # logging.debug("Get request:", extra=request)
    if len(input_msg) < 1:
        return
    if input_msg[0].startswith("ping4", 1):
        action = "ping4"
    elif input_msg[0].startswith("traceroute4", 1):
        action = "trace4"
    elif input_msg[0].startswith("trace4", 1):
        action = "trace4"
    elif input_msg[0].startswith("mtr4", 1):
        action = "mtr4"
    elif input_msg[0].startswith("ping", 1):
        action = "ping"
    elif input_msg[0].startswith("trace", 1):
        action = "trace"
    elif input_msg[0].startswith("mtr", 1):
        action = "mtr"
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.message.message_id,
                                       text="Invalid request")
        return
    if len(input_msg) < 2:
        if action == "ping":
            err_text = "pong"
        else:
            err_text = "Please check your input"
            # logging.info("Get invalid request:", extra=request)
        await context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.message.message_id,
                                       text=err_text)
        return
    res = ""
    if len(input_msg) > 2:
        res = "Unknown argv: "
        # logging.info("Get invalid request:", extra=request)
        for arg in range(2, len(input_msg)):
            if len(input_msg[arg]) < 12:
                res = res + "\'" + str(input_msg[arg]) + "\' "
            else:
                res += "too_long_param "
        res += "\n"
    target = input_msg[1]
    result = lg(action, target)
    reply = res + " <code>" + str(result) + "</code> "
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   reply_to_message_id=update.effective_message.message_id,
                                   parse_mode=ParseMode.HTML, text=reply)


if __name__ == '__main__':
    load_dotenv(verbose=True)
    TOKEN = os.getenv("TG_TOKEN")
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler('start', start)
    uuid_handler = CommandHandler('uuid', gen_uuid)
    mua_handler = CommandHandler('mua', mua)

    # echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    echo_handler = MessageHandler(filters.ALL & (~filters.COMMAND), echo)

    ptm_handler = CommandHandler(['ping', 'trace', 'mtr', 'trace4', 'traceroute', 'traceroute4', 'ping4', 'mtr4'],
                                 ping_trace_mtr)

    application.add_handler(start_handler)
    application.add_handler(uuid_handler)
    application.add_handler(mua_handler)
    application.add_handler(ptm_handler)

    application.run_polling(read_timeout=4)
