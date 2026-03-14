#TitanXBots - Admin Commands
from pyrogram import Client, filters
from config import OWNER_ID
from database.database import add_admin, remove_admin, list_admins, is_admin

# -------------------------------
# Owner-only Commands
# -------------------------------

@Client.on_message(filters.command("addadmin") & filters.private)
async def add_admin_cmd(client, message):
    """Add a user as admin (Owner only)."""

    # Security check: Only owner can use
    if message.from_user.id != OWNER_ID:
        return await message.reply_text("⛔ Only the owner can add admins.")

    if len(message.command) < 2:
        return await message.reply_text("Usage: `/addadmin user_id`", quote=True)

    try:
        user_id = int(message.command[1])
        await add_admin(user_id)
        await message.reply_text(f"✅ User `{user_id}` has been added as admin.")
    except ValueError:
        await message.reply_text("⚠️ Invalid user ID format.")


@Client.on_message(filters.command("removeadmin") & filters.private)
async def remove_admin_cmd(client, message):
    """Remove a user from the admin list (Owner only)."""

    # Security check: Only owner can remove admins
    if message.from_user.id != OWNER_ID:
        return await message.reply_text("⛔ Only the owner can remove admins.")

    if len(message.command) < 2:
        return await message.reply_text("Usage: `/removeadmin user_id`", quote=True)

    try:
        user_id = int(message.command[1])
        await remove_admin(user_id)
        await message.reply_text(f"❌ User `{user_id}` has been removed from admin list.")
    except ValueError:
        await message.reply_text("⚠️ Invalid user ID format.")


# -------------------------------
# Admin + Owner Commands
# -------------------------------

@Client.on_message(filters.command("adminlist") & filters.private)
async def admin_list_cmd(client, message):
    """View all admins (Accessible by Admins + Owner)."""

    # Check if user is admin or owner
    if message.from_user.id != OWNER_ID and not await is_admin(message.from_user.id):
        return await message.reply_text("⛔ Only admins can view the admin list.")

    admins = await list_admins()
    if not admins:
        return await message.reply_text("📭 No admins found in the database.")
    
    text = "<b>👑 Current Admins:</b>\n" + "\n".join([f"• <code>{x}</code>" for x in admins])
    await message.reply_text(text)
