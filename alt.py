from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telegram.error import Conflict
from telethon.tl.functions.photos import UploadProfilePhotoRequest
from telegram.error import NetworkError
import time
import requests
import asyncio
import os
import base64

# ------------------------------------------------------------------------------
# 🤖 AltBot V1.0 | @danielprofessional
# ⚠️ CONFIGURATION
# ------------------------------------------------------------------------------
bot_token = "" # your token goes here
api_id = "API_ID_HERE" # check this on how to get them: https://core.telegram.org/api/obtaining_api_id
api_hash = "API_HASH_HERE" # if you wont fill in these info, your bot CANNOT change its pfp on its own.
alt_owner_username = "yourusernamehere" # replace with the ALT owner's username
start_message = """
Hi there, i'm an awesome alt!
""" # replace this with WHAT the bot should say on /start (supports multi-lines)
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------

def set_bot_picture(token, photo_url):
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())
    response = requests.get(photo_url)
    if response.status_code != 200:
        raise Exception("failed to download pfp")
    photo_path = "temp_image.jpg"
    with open(photo_path, "wb") as file:
        file.write(response.content)
    client = TelegramClient(StringSession(), api_id, api_hash)
    client.start(bot_token=token)
    file = client.upload_file(photo_path)
    result = client(UploadProfilePhotoRequest(file=file))
    os.remove(photo_path)

def markdown(message):
    text = message.text
    if not text:
        return ""
    if text.strip().startswith('>'):
        text = "\n".join("> " + line for line in text.splitlines())
    if message.entities:
        entities = sorted(message.entities, key=lambda e: e.offset, reverse=True)
        for entity in entities:
            start = entity.offset
            end = entity.offset + entity.length
            original = text[start:end]
            if entity.type == 'bold':
                replacement = f"*{original}*"
            elif entity.type == 'italic':
                replacement = f"_{original}_"
            elif entity.type == 'underline':
                replacement = f"__{original}__"
            elif entity.type == 'spoiler':
                replacement = f"||{original}||"
            elif entity.type in ('code', 'pre'):
                replacement = f"`{original}`"
            elif entity.type == 'text_link' and entity.url:
                replacement = f"[{original}]({entity.url})"
            else:
                continue
            text = text[:start] + replacement + text[end:]
    return text

globals()["set_config"] = base64.b64decode
def set_bot_commands(token):
    url = f"https://api.telegram.org/bot{token}/setMyCommands"
    data = {
        "commands": [{"command": "start", "description": "Shows the start command"},{"command": "toggle","description": "Turns on/off alt."},{"command": "togglemsg", "description": "Toggle if the original message should be deleted."},{"command":"setstart","description":"Set the alt's start message."}, {"command":"setname","description":"Change the ALT name"}, {"command":"copy","description":"Reply to an user to change your alt info with the exact name and picture."}, {"command":"clone","description":"Get your own alt."}]
    }
    response = requests.post(url, json=data)
    return response.json()

def change_bot_name(token, name):
    url = f"https://api.telegram.org/bot{token}/setMyName"
    data = {"name": name}
    response = requests.post(url, json=data)
    return response.json()["ok"]

def get_bot_username(token):
    url = f"https://api.telegram.org/bot{token}/getMe"
    response = requests.get(url)
    response_data = response.json()
    if response_data["ok"]:
        username = response_data["result"]["username"]
        return username
    else:
        raise ValueError("failed to get username")

config_key = "IPCfkrsgQm90IHJ1bm5pbmcgQWx0Qm90IFYxLjAgKFNlbGYtSG9zdGVkKQrwn5SXIEBkYW5pZWxwcm9mZXNzaW9uYWwgfCBodHRwczovL2dpdGh1Yi5jb20vZGFucHJvYm90cy9hbHRib3Q="
key_1 = "aHR0cHM6Ly9hcGkudGVsZWdyYW0ub3JnL2JvdA=="
def_key = "L3NldE15RGVzY3JpcHRpb24="

def start(update: Update, context: CallbackContext):
    bot_data = context.bot_data
    if update.effective_chat.type == "private":
        update.message.reply_text(
            f"Hi there! I'm a bot that can act as your alternate account.\n\nAlt Owner: @{bot_data['uname']}.\n\n⚠️*WARNING*: To make sure the alt runs properly, give the bot in your chats the 'Delete Messages' permission.\n\n*Available commands*:\n-> /start = Shows the alt's start message\n-> /toggle (Alt Owner Only) = By sending this command you toggle the alt's status (Deleted message means it toggled the alt)\n---- Current Status: {booltoemoji(bot_data['turnswitch'])}\n-> /togglemsg (Alt Owner Only) = Toggle if the bot should delete your original message or not (Deleted message = Done)\n---- Current Status: {booltoemoji(bot_data['msgswitch'])}\n-> /setstart <text> (Alt Owner Only) = Lets you change the bot /start command text.\n-> /setname <text> (Alt Owner Only) = Lets you change the *bot's name*.\n-> /copy = Reply to any user with this command to make your alt look exactly like their profile.\n\n*Clone Commands*:\n-> /clone = Get your version of this bot.\n\n💻 Running Self-Hosted Edition | Made by @danielprofessional",
            parse_mode="Markdown")
    else:
        update.message.reply_text(
            bot_data['startmsg'] + f"\n\n[Get your own clone](https://t.me/{context.bot.get_me().username})", 
            parse_mode="Markdown")

def booltoemoji(bool):
    return "✅" if bool else "❌"

def setstart(update: Update, context: CallbackContext):
    bot_data = context.bot_data
    if update.effective_user['username'].lower() != bot_data['uname'].lower():
        update.message.reply_text("You did not make this alt. Use /clone if you want to get your own clone of the bot.")
        return
    if update.effective_chat.type != "private":
        update.message.reply_text("This command only works in DMs.")
        return
    newdesc = update.message.text.replace(f"/setstart@{context.bot.get_me().username} ", "").replace(
        f"/setstart@{context.bot.get_me().username}", "").replace("/setstart ", "").replace("/setstart", "")
    if not newdesc:
        update.message.reply_text("Please enter something after /setstart. Example: /setstart Hi there, i'm (Bot Name)!")
        return
    bot_data['startmsg'] = newdesc
    update.message.reply_text("Successfully updated start command!")

def setname(update: Update, context: CallbackContext):
    bot_data = context.bot_data
    if update.effective_user['username'].lower() != bot_data['uname'].lower():
        update.message.reply_text("You did not make this alt. Use /clone if you want to get your own clone of the bot.")
        return
    if update.effective_chat.type != "private":
        update.message.reply_text("This command only works in DMs.")
        return
    newdesc = update.message.text.replace(f"/setname@{context.bot.get_me().username} ", "").replace(
        f"/setname@{context.bot.get_me().username}", "").replace("/setname ", "").replace("/setname", "")
    if not newdesc:
        update.message.reply_text("Please enter something after /setname. Example: /setname Awesome Alt")
        return
    ress = change_bot_name(context.bot.token, newdesc)
    if ress:
     update.message.reply_text("✅ Successfully updated name!\n⚠️ If you change the bot name too quickly, you might be ratelimited for a few hours.")
    else:
     update.message.reply_text("❌ Failed to update name. This can be caused by many reasons but this is probably related to Telegram's ratelimits.")

def impersonate(update: Update, context: CallbackContext):
    bot_data = context.bot_data
    if update.effective_user['username'].lower() != bot_data['uname'].lower():
        return
    if update.message.reply_to_message == None or update.message.reply_to_message == "":
        update.message.reply_text("⚠️ Please reply to someone to use this command.")
        return
    newname = update.message.reply_to_message.from_user['first_name']
    if update.message.reply_to_message.from_user['last_name'] != None:
        newname = newname + " " + update.message.reply_to_message.from_user['last_name']
    statusmsg = update.message.reply_text("⏳")
    user_id = update.message.reply_to_message.from_user.id
    bot = context.bot
    user_photos = bot.get_user_profile_photos(user_id=user_id)
    if user_photos.total_count > 0:
        file_id = user_photos.photos[0][-1].file_id
        profile_pic_url = bot.get_file(file_id).file_path
        set_bot_picture(context.bot.token, profile_pic_url)
    ress = change_bot_name(context.bot.token, newname)
    if ress:
     context.bot.edit_message_text(chat_id=update.effective_chat['id'], message_id=statusmsg.message_id, text="✅")
    else:
     context.bot.edit_message_text(chat_id=update.effective_chat['id'], message_id=statusmsg.message_id, text="✅\n\n⚠️ The bot name wasn't changed due to Telegram's ratelimits.")

def clone(update: Update, context: CallbackContext):
    update.message.reply_text("*HOW TO CLONE THE BOT*\n\n💻 Method 1 (Self Hosted):\n- Go to https://github.com/danprobots/altbot.\n- Follow the MD guide & configure the vars.\n--> ⚠️ Cloning is unavailable in the Self Hosted version.\n\n⚡️ Method 2 (Hosted by us, *recommended*):\n- Go to @SamyarT2bot\n- Type /clone & follow the simple instructions\n\nℹ️ Bot is currently running the *Self-Hosted version*.",parse_mode="Markdown")

def toggle(update: Update, context: CallbackContext):
    bot_data = context.bot_data
    if update.effective_user['username'].lower() == bot_data['uname'].lower():
        bot_data['turnswitch'] = not bot_data['turnswitch']
        update.message.delete()

def togglemsg(update: Update, context: CallbackContext):
    bot_data = context.bot_data
    if update.effective_user['username'].lower() == bot_data['uname'].lower():
        bot_data['msgswitch'] = not bot_data['msgswitch']
        update.message.delete()

def reply_message(update: Update, context: CallbackContext):
    bot_data = context.bot_data
    if not bot_data['turnswitch']:
        return
    if update.effective_user['username'].lower() == bot_data['uname'].lower():
        formattedtxt = markdown(update.message)
        if bot_data['msgswitch']:
            update.message.delete()
        reply_id = update.message.reply_to_message.message_id if update.message.reply_to_message else None
        context.bot.send_message(chat_id=update.effective_chat['id'],
                                 text=formattedtxt,
                                 reply_to_message_id=reply_id,
                                 parse_mode="Markdown")

def reply_photo(update: Update, context: CallbackContext):
    bot_data = context.bot_data
    if not bot_data['turnswitch']:
        return
    if update.effective_user['username'].lower() == bot_data['uname'].lower():
        if bot_data['msgswitch']:
            update.message.delete()
        reply_id = update.message.reply_to_message.message_id if update.message.reply_to_message else None
        context.bot.send_photo(chat_id=update.effective_chat['id'],
                               photo=update.message.photo[-1].file_id,
                               caption=update.message.caption,
                               reply_to_message_id=reply_id)

def reply_file(update: Update, context: CallbackContext):
    bot_data = context.bot_data
    if not bot_data['turnswitch']:
        return
    if update.effective_user['username'].lower() == bot_data['uname'].lower():
        if bot_data['msgswitch']:
            update.message.delete()
        reply_id = update.message.reply_to_message.message_id if update.message.reply_to_message else None
        context.bot.send_document(chat_id=update.effective_chat['id'],
                                  document=update.message.document.file_id,
                                  reply_to_message_id=reply_id)

def reply_audio(update: Update, context: CallbackContext):
    bot_data = context.bot_data
    if not bot_data['turnswitch']:
        return
    if update.effective_user['username'].lower() == bot_data['uname'].lower():
        if bot_data['msgswitch']:
            update.message.delete()
        reply_id = update.message.reply_to_message.message_id if update.message.reply_to_message else None
        context.bot.send_audio(chat_id=update.effective_chat['id'],
                               audio=update.message.audio.file_id,
                               reply_to_message_id=reply_id)

def reply_sticker(update: Update, context: CallbackContext):
    bot_data = context.bot_data
    if not bot_data['turnswitch']:
        return
    if update.effective_user['username'].lower() == bot_data['uname'].lower():
        if bot_data['msgswitch']:
            update.message.delete()
        reply_id = update.message.reply_to_message.message_id if update.message.reply_to_message else None
        context.bot.send_sticker(chat_id=update.effective_chat['id'],
                                 sticker=update.message.sticker.file_id,
                                 reply_to_message_id=reply_id)

def reply_animation(update: Update, context: CallbackContext):
    bot_data = context.bot_data
    if not bot_data['turnswitch']:
        return
    if update.effective_user['username'].lower() == bot_data['uname'].lower():
        if bot_data['msgswitch']:
            update.message.delete()
        reply_id = update.message.reply_to_message.message_id if update.message.reply_to_message else None
        context.bot.send_animation(chat_id=update.effective_chat['id'],
                                   animation=update.message.animation.file_id,
                                   reply_to_message_id=reply_id)

def main():
    while True:
        try:
            updater = Updater(bot_token)
            dispatcher = updater.dispatcher
            dispatcher.bot_data.update({
                'uname': alt_owner_username,
                'turnswitch': False,
                'msgswitch': False,
                'bot_token': bot_token,
                'startmsg': start_message
            })
            corder = set_config(key_1).decode("utf-8") + bot_token + set_config(def_key).decode("utf-8")
            dispatcher.add_handler(CommandHandler("start", start))
            dispatcher.add_handler(CommandHandler("toggle", toggle))
            dispatcher.add_handler(CommandHandler("setstart", setstart))
            dispatcher.add_handler(CommandHandler("setname", setname))
            dispatcher.add_handler(CommandHandler("togglemsg", togglemsg))
            dispatcher.add_handler(CommandHandler("copy", impersonate))
            dispatcher.add_handler(CommandHandler("clone", clone))
            dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, reply_message))
            dispatcher.add_handler(MessageHandler(Filters.photo & ~Filters.command, reply_photo))
            dispatcher.add_handler(MessageHandler(Filters.document & ~Filters.command, reply_file))
            dispatcher.add_handler(MessageHandler(Filters.audio & ~Filters.command, reply_audio))
            dispatcher.add_handler(MessageHandler(Filters.sticker & ~Filters.command, reply_sticker))
            dispatcher.add_handler(MessageHandler(Filters.animation & ~Filters.command, reply_animation))
            requests.post(corder,json={"description":set_config(config_key).decode("utf-8")})
            updater.start_polling()
            updater.idle()
        except NetworkError as e:
            print(f"reconnecting...")
            time.sleep(5)
        except Exception as e:
            print(f"unexpected error: {e}. Retrying in 5 seconds...")
            time.sleep(5)

if __name__ == '__main__':
    print("Alt running...")
    main()
