
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message

# --- Configuration and Global State ---
# Placeholder for global configuration
FILE_AUTO_DELETE = 60  # Default auto-delete delay in seconds

# Global variable to control auto-delete state
AUTO_DELETE_ENABLED = True  # Default state

# Configure logging
logging.basicConfig(level=logging.INFO,  # Corrected: logging.INFO
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Core Auto-Delete Logic ---

async def delete_files(messages: list[Message], client: Client, k: Message, command_payload: str = None):
    """
    Deletes a list of messages after a delay if auto-delete is enabled,
    then edits a 'k' message to inform the user.
    """
    global AUTO_DELETE_ENABLED

    if not AUTO_DELETE_ENABLED:
        logger.info(f"Auto-delete is disabled. Skipping deletion for messages: {[m.id for m in messages]}.")
        return

    logger.info(f"Auto-delete enabled. Waiting {FILE_AUTO_DELETE} seconds before deleting messages: {[m.id for m in messages]}.")
    await asyncio.sleep(FILE_AUTO_DELETE)  # Wait for the duration

    # Delete all messages
    for msg in messages:
        try:
            await client.delete_messages(chat_id=msg.chat.id, message_ids=[msg.id])
            logger.info(f"Deleted message {msg.id} in chat {msg.chat.id}")
        except Exception as e:
            logger.error(f"Failed to delete message {msg.id} in chat {msg.chat.id}: {e}")

    # Construct the inline keyboard button
    keyboard = None
    if command_payload:
        # Assuming client.username is available, if not, use a direct link like "t.me/your_bot_username"
        bot_username = (await client.get_me()).username if not client.username else client.username
        button_url = f"https://t.me/{bot_username}?start={command_payload}"
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("ɢᴇᴛ ғɪʟᴇ ᴀɢᴀɪɴ!", url=button_url)]]
        )

    # Edit the message 'k' to inform the user
    try:
        await k.edit_text(
            "ʏᴏᴜʀ ᴠɪᴅᴇᴏ / ꜰɪʟᴇ ɪꜱ ꜱᴜᴄᴇꜱꜱꜰᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ✅\nɴᴏᴡ ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ᴅᴇʟᴇᴛᴇᴅ ᴠɪᴅᴇᴏ / ꜰɪʟᴇ 👇",
            reply_markup=keyboard,
        )
        logger.info(f"Successfully edited message {k.id} in chat {k.chat.id} after deletion.")
    except Exception as e:
        logger.error(f"Error editing message {k.id} after deletion: {e}")

# --- Settings and Inline Button Logic ---

def get_settings_message_and_keyboard():
    """
    Generates the text and inline keyboard for the auto-delete settings.
    """
    current_state_text = "Enabled" if AUTO_DELETE_ENABLED else "Disabled"
    text = (
        f"⚙️ **Auto-Delete Settings**\n\n"
        f"Auto-delete is currently: **{current_state_text}**\n\n"
        f"Choose an option below to change the setting."
    )

    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Enable Auto-delete", callback_data="set_auto_delete_on")],
            [InlineKeyboardButton("❌ Disable Auto-delete", callback_data="set_auto_delete_off")]
        ]
    )
    return text, keyboard

@Client.on_message(filters.command("settings"))
async def settings_command_handler(client: Client, message: Message):
    """
    Handles the /settings command, displaying the current auto-delete state
    and inline buttons to change it.
    """
    logger.info(f"Received /settings command from user {message.from_user.id} in chat {message.chat.id}")
    text, keyboard = get_settings_message_and_keyboard()
    await message.reply_text(text, reply_markup=keyboard, parse_mode="markdown")

@Client.on_callback_query(filters.regex(r"set_auto_delete_on|set_auto_delete_off"))
async def settings_callback_handler(client: Client, callback_query: CallbackQuery):
    """
    Handles callback queries from the auto-delete settings inline keyboard.
    Toggles the AUTO_DELETE_ENABLED state and updates the settings message.
    """
    global AUTO_DELETE_ENABLED
    data = callback_query.data
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.id

    logger.info(f"Received callback query '{data}' from user {user_id} in chat {chat_id}")

    # Optional: You might want to add a check here to ensure only the user
    # who invoked the /settings command can interact with its buttons.
    # For simplicity, we'll allow any user in the chat to press for now.
    # if user_id != callback_query.message.reply_to_message.from_user.id:
    #     await callback_query.answer("You can only change settings for your own messages!", show_alert=True)
    #     return

    toast_text = ""
    if data == "set_auto_delete_on":
        if not AUTO_DELETE_ENABLED:
            AUTO_DELETE_ENABLED = True
            toast_text = "Auto-delete is now ENABLED."
            logger.info("Auto-delete state changed to ENABLED.")
        else:
            toast_text = "Auto-delete is already enabled."
    elif data == "set_auto_delete_off":
        if AUTO_DELETE_ENABLED:
            AUTO_DELETE_ENABLED = False
            toast_text = "Auto-delete is now DISABLED."
            logger.info("Auto-delete state changed to DISABLED.")
        else:
            toast_text = "Auto-delete is already disabled."

    # Regenerate the message and keyboard based on the new state
    new_text, new_keyboard = get_settings_message_and_keyboard()

    # Edit the original message to reflect the new state
    try:
        await callback_query.message.edit_text(
            new_text,
            reply_markup=new_keyboard,
            parse_mode="markdown"
        )
        # Show a small toast notification to the user
        await callback_query.answer(toast_text)
        logger.info(f"Edited settings message {message_id} in chat {chat_id} and answered callback.")
    except Exception as e:
        logger.error(f"Error editing settings message {message_id} or answering callback: {e}")
        await callback_query.answer("An error occurred while updating settings.", show_alert=True)


# --- Pyrogram Client Setup ---
# Replace with your actual API ID and hash
API_ID = 12345678 # Your API ID here
API_HASH = "your_api_hash" # Your API Hash here
BOT_TOKEN = "your_bot_token" # Your Bot Token here

app = Client("auto_delete_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


# --- Example Usage (Send Command) ---
# This part demonstrates how `delete_files` would be called in your bot.
@app.on_message(filters.command("send") & filters.private)
async def send_example_command(client: Client, message: Message):
    """
    An example command to simulate sending a file and then triggering auto-delete.
    """
    logger.info(f"Received /send command from user {message.from_user.id} in chat {message.chat.id}")

    # Send a status message that will later be edited after deletion
    status_message = await message.reply_text("⏳ Sending your example file...")

    try:
        # Simulate sending a file (replace with actual file sending logic)
        # For demonstration, we'll send a text message as a "file"
        sent_file_message = await client.send_message(
            chat_id=message.chat.id,
            text="📁 Here is your example file content. This will be deleted in a minute!"
        )
        logger.info(f"Sent example 'file' message {sent_file_message.id}.")

        # Now, call the delete_files function
        # 'messages' is the list of messages to delete (e.g., the sent file)
        # 'k' is the message to edit AFTER deletion (e.g., the status message)
        await delete_files([sent_file_message], client, status_message, command_payload="get_file_again_example")

    except Exception as e:
        logger.error(f"Error in /send command: {e}")
        await status_message.edit_text("❌ An error occurred while sending the file.")


# --- Main Execution Block ---
if __name__ == "__main__":
    logger.info("Bot starting...")
    app.run()
    logger.info("Bot stopped.")
