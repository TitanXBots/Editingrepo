
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery

# --- Configuration (replace with your actual values) ---
ADMINS = [123456789] # Replace with your admin user ID(s)
# Example: ADMINS = [12345, 67890]

# Global state for auto-delete
AUTO_DELETE_ENABLED = False # Initial state

# Time to wait before deleting files
FILE_AUTO_DELETE = 30 # seconds (example value)

# Initialize your Pyrogram client (assuming 'app' or 'client' is your Client instance)
# client = Client("my_bot", api_id=YOUR_API_ID, api_hash=YOUR_API_HASH, bot_token=YOUR_BOT_TOKEN)


# === Existing delete_files function ===
async def delete_files(messages: list[Message], client: Client, k: Message, command_payload: str = None):
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
            # Ensure me.username is not None before using in f-string
            if me and me.username:
                button_url = f"https://t.me/{me.username}?start={command_payload}"
                keyboard = InlineKeyboardMarkup(
                    [[InlineKeyboardButton("ɢᴇᴛ ғɪʟᴇ ᴀɢᴀɪɴ!", url=button_url)]]
                )
            else:
                logging.warning("Bot username not found, cannot build 'get file' button URL.")
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
    logging.info(f"Auto-delete is now {'ENABLED' if state else 'DISABLED'}")
    return AUTO_DELETE_ENABLED


# ====== COMMAND HANDLERS (for direct commands, can coexist with buttons) ======
@Client.on_message(filters.command("autodeleteon") & filters.user(ADMINS))
async def handle_autodelete_on(client: Client, message: Message):
    set_auto_delete(True)
    await message.reply_text("✅ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ ɪꜱ ɴᴏᴡ ᴇɴᴀʙʟᴇᴅ.")


@Client.on_message(filters.command("autodeleteoff") & filters.user(ADMINS))
async def handle_autodelete_off(client: Client, message: Message):
    set_auto_delete(False)
    await message.reply_text("❌ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ ɪꜱ ɴᴏᴡ ᴅɪꜱᴀʙʟᴇᴅ.")


# ====== NEW: COMMAND TO DISPLAY AUTO-DELETE BUTTONS ======
def get_autodelete_keyboard():
    """Helper function to create the inline keyboard."""
    current_state_emoji = "✅" if AUTO_DELETE_ENABLED else "❌"
    button_text_on = f"Turn On Auto-Delete"
    button_text_off = f"Turn Off Auto-Delete"

    # You could also add the current state to the button itself, e.g.:
    # button_text_on = "✅ Turn On" if not AUTO_DELETE_ENABLED else "✅ ON (current)"
    # button_text_off = "❌ Turn Off" if AUTO_DELETE_ENABLED else "❌ OFF (current)"

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(button_text_on, callback_data="autodelete_toggle_on"),
                InlineKeyboardButton(button_text_off, callback_data="autodelete_toggle_off")
            ]
        ]
    )

@Client.on_message(filters.command("autodelete") & filters.user(ADMINS))
async def autodelete_menu(client: Client, message: Message):
    """Sends a message with inline buttons to toggle auto-delete."""
    status = "enabled" if AUTO_DELETE_ENABLED else "disabled"
    await message.reply_text(
        f"⚙️ Auto-delete is currently **{status.upper()}**.\n\n"
        "Use the buttons below to change its state:",
        reply_markup=get_autodelete_keyboard(),
        parse_mode="markdown"
    )

# ====== NEW: CALLBACK QUERY HANDLER FOR AUTO-DELETE BUTTONS ======
@Client.on_callback_query(filters.regex("^autodelete_toggle_(on|off)$") & filters.user(ADMINS))
async def handle_autodelete_button(client: Client, callback_query: CallbackQuery):
    action = callback_query.data.split('_')[-1] # Extracts 'on' or 'off'

    if action == "on":
        new_state = True
        response_text = "✅ Auto-delete enabled!"
    else: # action == "off"
        new_state = False
        response_text = "❌ Auto-delete disabled!"

    set_auto_delete(new_state)

    # Answer the callback query to remove the loading spinner and provide feedback
    await callback_query.answer(response_text, show_alert=False)

    # Edit the original message to reflect the new state
    status = "enabled" if AUTO_DELETE_ENABLED else "disabled"
    await callback_query.edit_message_text(
        f"⚙️ Auto-delete is currently **{status.upper()}**.\n\n"
        "Use the buttons below to change its state:",
        reply_markup=get_autodelete_keyboard(),
        parse_mode="markdown"
    )

