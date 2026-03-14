import os
import asyncio
import humanize
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from Script import NEW_USER_TXT
from bot import Bot
from config import *
from helper_func import subscribed, encode, decode, get_messages
from database.database import add_user, del_user, full_userbase, present_user, banned_users, ban_user, unban_user, is_banned, get_ban_reason
import logging
from pymongo import MongoClient

client = MongoClient(DB_URI)
db = client[DB_NAME]
collection = db["TelegramFiles"]

AUTO_DELETE_ENABLED = True  # Default state  

titanxofficials = FILE_AUTO_DELETE
titandeveloper = titanxofficials
file_auto_delete = humanize.naturaldelta(titandeveloper)


async def is_maintenance(client, user_id:int)->bool:
    check_msg = collection.find_one({"maintenance": "on"})
    if check_msg and user_id not in ADMINS:
        return True
    return False


@Bot.on_message(filters.command('start') & filters.private & subscribed)
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id

    # 🚫 Ban check first
    if await is_banned(user_id):
        reason = await get_ban_reason(user_id)
        await message.reply_text(
            f"🚫 You are banned from using this bot.\n\n**Reason:** {reason}"
        )
        return

    # ✅ Proceed normally if not banned
    if not await present_user(user_id):
        try:
            await add_user(user_id)
            user_name = message.from_user.first_name or "Unknown"
            message_text = NEW_USER_TXT.format(message.from_user.mention, user_id, user_name)
            await client.send_message(LOG_CHANNEL_ID, message_text)
        except:
            pass

    if await is_maintenance(client, user_id):
        await message.reply_text("⚙️ Maintenance mode is currently active. Please try again later.")
        return
    text = message.text
    if len(text)>7:
        try:
            base64_string = text.split(" ", 1)[1]
        except:
            return
        string = await decode(base64_string)
        argument = string.split("-")
        if len(argument) == 3:
            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
            except:
                return
            if start <= end:
                ids = range(start,end+1)
            else:
                ids = []
                i = start
                while True:
                    ids.append(i)
                    i -= 1
                    if i < end:
                        break
        elif len(argument) == 2:
            try:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except:
                return
        temp_msg = await message.reply("Wait Bro...")
        try:
            messages = await get_messages(client, ids)
        except:
            await message.reply_text("Something went wrong..!")
            return
        await temp_msg.delete()

        titanx_msgs = [] # List to keep track of sent message 

        for msg in messages:

            if bool(CUSTOM_CAPTION) & bool(msg.document):
                caption = CUSTOM_CAPTION.format(previouscaption = "" if not msg.caption else msg.caption.html, filename = msg.document.file_name)
            else:
                caption = "" if not msg.caption else msg.caption.html

            if DISABLE_CHANNEL_BUTTON:
                reply_markup = msg.reply_markup
            else:
                reply_markup = None

            try:
                titanx_msg = await msg.copy(chat_id=message.from_user.id, caption = caption, parse_mode = ParseMode.HTML, reply_markup = reply_markup, protect_content=PROTECT_CONTENT)
                titanx_msgs.append(titanx_msg)
                
            except FloodWait as e:
                await asyncio.sleep(e.value)
                titanx_msg = await msg.copy(chat_id=message.from_user.id, caption = caption, parse_mode = ParseMode.HTML, reply_markup = reply_markup, protect_content=PROTECT_CONTENT)
                titanx_msgs.append(titanx_msg)
            except Exception as e:
                print(f"Error coping message: {e}")
                pass

        k = await client.send_message(chat_id=message.from_user.id, text=f"<b>❗️ <u>IMPORTANT</u> ❗️</b>\n\nThis Video / File Will Be Deleted In {file_auto_delete} (Due To Copyright Issues).\n\n📌 Please Forward This Video / File To Somewhere Else And Start Downloading There.")

        # Schedule the file deletion
        asyncio.create_task(delete_files(titanx_msgs, client, k, base64_string if 'base64_string' in locals() else None))
        
        
        return
    else:
        reply_markup = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("🧠 ʜᴇʟᴘ", callback_data="help"),
            InlineKeyboardButton("🔰 ᴀʙᴏᴜᴛ", callback_data="about")
        ],
        [
            InlineKeyboardButton("⚙️  Sᴇᴛᴛɪɴɢs", callback_data="settings")
        ],
        [
            InlineKeyboardButton("🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ", url="https://t.me/TitanXBots"),
            InlineKeyboardButton("🔍 ꜱᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ", url="https://t.me/TitanMattersSupport")
        ]
    ]
        )  
        await message.reply_photo(
            photo=START_PIC,
            caption=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=reply_markup,
        )
        return
    

#=====================================================================================##

WAIT_MSG = "<b>Working....</b>"

REPLY_ERROR = "<code>Use this command as a reply to any telegram message without any spaces.</code>"

#=====================================================================================##

    
    
@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):
    buttons = [
        [
            InlineKeyboardButton(text="ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=client.invitelink),
            InlineKeyboardButton(text="ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=client.invitelink2),
        ],
        [
            InlineKeyboardButton(text="ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=client.invitelink3),
            InlineKeyboardButton(text="ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=client.invitelink4),
        ]
    ]
    try:
        buttons.append(
            [
                InlineKeyboardButton(
                    text = '☢ ɴᴏᴡ ᴄʟɪᴄᴋ ʜᴇʀᴇ •',
                    url = f"https://t.me/{client.username}?start={message.command[1]}"
                )
            ]
        )
    except IndexError:
        pass

    await message.reply_photo(
    photo=FORCE_PIC, 
    caption=FORCE_MSG.format(
        first=message.from_user.first_name,
        last=message.from_user.last_name,
        username=None if not message.from_user.username else '@' + message.from_user.username,
        mention=message.from_user.mention,
        id=message.from_user.id
    ),
    reply_markup=InlineKeyboardMarkup(buttons)
)

@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    msg = await client.send_message(chat_id=message.chat.id, text=WAIT_MSG)
    users = await full_userbase()
    await msg.edit(f"{len(users)} users are using this bot")

@Bot.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
async def send_text(client: Bot, message: Message):
    if message.reply_to_message:
        query = await full_userbase()
        broadcast_msg = message.reply_to_message
        total = 0
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0
        
        pls_wait = await message.reply("<i>ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴘʀᴏᴄᴇꜱꜱɪɴɢ....</i>")
        for chat_id in query:
            try:
                await broadcast_msg.copy(chat_id)
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await broadcast_msg.copy(chat_id)
                successful += 1
            except UserIsBlocked:
                await del_user(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await del_user(chat_id)
                deleted += 1
            except:
                unsuccessful += 1
                pass
            total += 1
        
        status = f"""<b><u>ʙʀᴏᴀᴅᴄᴀꜱᴛ...</u>

Total Users: <code>{total}</code>
Successful: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code></b>"""
        
        return await pls_wait.edit(status)

    else:
        msg = await message.reply(REPLY_ERROR)
        await asyncio.sleep(8)
        await msg.delete()


# -------------------------------
# BAN COMMAND
# -------------------------------
@Bot.on_message(filters.command("ban") & filters.user(ADMINS))
async def ban_command(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage:\n`/ban user_id [reason]`", quote=True)

    try:
        user_id = int(message.command[1])
        reason = " ".join(message.command[2:]) or "ɴᴏ ʀᴇᴀꜱᴏɴ ᴘʀᴏᴠɪᴅᴇᴅ"

        # Fetch user info
        user = await client.get_users(user_id)
        name = user.first_name or "Unknown"
        if user.last_name:
            name += f" {user.last_name}"
        if user.username:
            name += f" (@{user.username})"

        # Check if already banned
        if await is_banned(user_id):
            current_reason = await get_ban_reason(user_id)
            return await message.reply_text(
                f"⚠️ {name} ɪꜱ ᴀʟʀᴇᴀᴅʏ ʙᴀɴɴᴇᴅ.\n📝 ʀᴇᴀꜱᴏɴ: {current_reason}"
            )

        # Add user to banned list
        await ban_user(user_id, reason)

        await message.reply_text(
            f"🚫 User Banned: {name}\n"
            f"👤 User ID: `{user_id}`\n"
            f"📄 Reason: {reason}"
        )

        # Notify banned user
        try:
            await client.send_message(
                user_id,
                f"⚠️ ʏᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ʙᴀɴɴᴇᴅ ꜰʀᴏᴍ ᴜꜱɪɴɢ ᴛʜɪꜱ ʙᴏᴛ.\nʀᴇᴀꜱᴏɴ: {reason}"
            )
        except:
            pass

    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")


# -------------------------------
# UNBAN COMMAND
# -------------------------------
@Bot.on_message(filters.command("unban") & filters.user(ADMINS))
async def unban_command(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage:\n`/unban user_id`", quote=True)

    try:
        user_id = int(message.command[1])

        user = await client.get_users(user_id)
        name = user.first_name or "Unknown"
        if user.last_name:
            name += f" {user.last_name}"
        if user.username:
            name += f" (@{user.username})"

        if not await is_banned(user_id):
            return await message.reply_text(f"ℹ️ {name} ɪꜱ ɴᴏᴛ ʙᴀɴɴᴇᴅ.")

        await unban_user(user_id)

        await message.reply_text(
            f"✅ User Unbanned: {name}\n"
            f"👤 User ID: `{user_id}`"
        )

        try:
            await client.send_message(
                user_id,
                "✅ ʏᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ᴜɴʙᴀɴɴᴇᴅ. ʏᴏᴜ ᴄᴀɴ ɴᴏᴡ ᴜꜱᴇ ᴛʜᴇ ʙᴏᴛ ᴀɢᴀɪɴ!"
            )
        except:
            pass

    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")


# -------------------------------
# BANNED LIST COMMAND
# -------------------------------
@Bot.on_message(filters.command("bannedlist") & filters.user(ADMINS))
async def banned_list(client: Client, message: Message):
    try:
        banned = list(banned_users.find())
        if not banned:
            return await message.reply_text("✅ ɴᴏ ᴜꜱᴇʀꜱ ᴀʀᴇ ᴄᴜʀʀᴇɴᴛʟʏ ʙᴀɴɴᴇᴅ.")

        text = "🚫 𝐁𝐀𝐍𝐍𝐄𝐃 𝐔𝐒𝐄𝐑𝐒 𝐋𝐈𝐒𝐓 🚫\n\n"
        for count, user in enumerate(banned, start=1):
            user_id = user["_id"]
            reason = user.get("ʀᴇᴀꜱᴏɴ", "ɴᴏ ʀᴇᴀꜱᴏɴ ᴘʀᴏᴠɪᴅᴇᴅ")

            try:
                tg_user = await client.get_users(user_id)
                name = tg_user.first_name or "Unknown"
                if tg_user.last_name:
                    name += f" {tg_user.last_name}"
                if tg_user.username:                    name += f" (@{tg_user.username})"
            except:
                name = "ᴜꜱᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ (ʟᴇꜰᴛ ᴛᴇʟᴇɢʀᴀᴍ)"

            text += f"{count}. {name}\n🆔 `{user_id}`\n📝 {reason}\n\n"

            if count >= 50:
                text += f"⚠️ Showing first {count} banned users only."
                break

        await message.reply_text(text)

    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")


# ====== CORE FUNCTION =====


# ====== AUTO DELETE FUNCTION ======
async def delete_files(messages, client, k, command_payload=None):
    """Deletes messages after FILE_AUTO_DELETE seconds if enabled."""
    global AUTO_DELETE_ENABLED

    if not AUTO_DELETE_ENABLED:
        logging.info("Auto-delete is disabled. Skipping deletion.")
        return

    await asyncio.sleep(FILE_AUTO_DELETE)

    # Delete all messages in list
    for msg in messages:
        try:
            await client.delete_messages(chat_id=msg.chat.id, message_ids=[msg.id])
            logging.info(f"Deleted message {msg.id} in chat {msg.chat.id}")
        except Exception as e:
            logging.error(f"Failed to delete message {msg.id}: {e}")

    # Add “get file again” button if payload is present
    keyboard = None
    if command_payload:
        try:
            me = await client.get_me()
            button_url = f"https://t.me/{me.username}?start={command_payload}"
            keyboard = InlineKeyboardMarkup(
                [[InlineKeyboardButton("ɢᴇᴛ ғɪʟᴇ ᴀɢᴀɪɴ!", url=button_url)]]
            )
        except Exception as e:
            logging.error(f"Failed to build 'get file' button: {e}")

    # Edit the main message after deletion
    try:
        await k.edit_text(
            "ʏᴏᴜʀ ᴠɪᴅᴇᴏ / ꜰɪʟᴇ ɪꜱ ꜱᴜᴄᴇꜱꜰᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ✅\n"
            "ɴᴏᴡ ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ᴅᴇʟᴇᴛᴇᴅ ᴠɪᴅᴇᴏ / ꜰɪʟᴇ 👇",
            reply_markup=keyboard,
        )
        logging.info(f"Edited message {k.id} in chat {k.chat.id}")
    except Exception as e:
        logging.error(f"Error editing message after deletion: {e}")


# ====== TOGGLE STATE ======
def set_auto_delete(state: bool):
    """Toggle global auto-delete."""
    global AUTO_DELETE_ENABLED
    AUTO_DELETE_ENABLED = state
    return AUTO_DELETE_ENABLED


# ====== COMMAND HANDLERS ======
@Client.on_message(filters.command("autodeleteon") & filters.user(ADMINS))
async def handle_autodelete_on(client, message):
    set_auto_delete(True)
    await message.reply_text("✅ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ ɪꜱ ɴᴏᴡ ᴇɴᴀʙʟᴇᴅ.")


@Client.on_message(filters.command("autodeleteoff") & filters.user(ADMINS))
async def handle_autodelete_off(client, message):
    set_auto_delete(False)
    await message.reply_text("❌ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ ɪꜱ ɴᴏᴡ ᴅɪꜱᴀʙʟᴇᴅ.")

# Dont Remove Credit
# Update Channel - TitanXBots
# Ask Any Doubt on Telegram - @TitanOwner
# Support Group - @TitanMattersSupport
