import asyncio
import base64
import re, time
from datetime import date, datetime, timedelta
from bot import Bot
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, InputMediaPhoto
from pyrogram.errors import UserNotParticipant, FloodWait, ChatAdminRequired, RPCError, PeerIdInvalid
from pyrogram.errors import InviteHashExpired, InviteRequestSent
from database.database import Seishiro
from config import *
from helper_func import *
from pyrogram.enums import ParseMode, ChatMemberStatus

PAGE_SIZE = 6

# Revoke invite link after 5 minutes
async def revoke_invite_after_5_minutes(client: Bot, channel_id: int, link: str, is_request: bool = False):
    await asyncio.sleep(300)
    try:
        await client.revoke_chat_invite_link(channel_id, link)
        print(f"{'Jᴏɪɴ ʀᴇǫᴜᴇsᴛ' if is_request else 'Iɴᴠɪᴛᴇ'} ʟɪɴᴋ ʀᴇᴠᴏᴋᴇᴅ ғᴏʀ ᴄʜᴀɴɴᴇʟ {channel_id}")
    except Exception as e:
        print(f"Fᴀɪʟᴇᴅ ᴛᴏ ʀᴇᴠᴏᴋᴇ ɪɴᴠɪᴛᴇ ғᴏʀ ᴄʜᴀɴɴᴇʟ {channel_id}: {e}")

async def is_owner_or_admin(filter, client, message):
    try:
        user_id = message.from_user.id
        return any([user_id == OWNER_ID, await Seishiro.is_admin(user_id)])
    except Exception as e:
        logger.error(f"Exception in check_admin: {e}")
        return False
        
is_owner_or_admin = filters.create(is_owner_or_admin)

async def is_admin_user(filter, client, message):
    try:
        user_id = message.from_user.id
        return any([user_id == OWNER_ID, await Seishiro.is_admin(user_id)])
    except Exception as e:
        logger.error(f"Exception in check_admin: {e}")
        return False

is_admin_user = filters.create(is_admin_user)

# Settings command to show the main menu
@Bot.on_message(filters.command('settings') & filters.private & is_owner_or_admin)
async def settings_command(client: Client, message: Message):
    try:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Lɪɴᴋ sʜᴀʀᴇ ᴍᴇɴᴜ", callback_data="link_share"), InlineKeyboardButton("Aᴅᴍɪɴ ᴍᴇɴᴜ", callback_data="admin_bna_system")],
            [InlineKeyboardButton("Bᴀɴ ᴍᴇɴᴜ", callback_data="ban_menu"), InlineKeyboardButton("Fsᴜʙ ᴍᴇɴᴜ", callback_data="fsub_settings_menu")],
            [InlineKeyboardButton("Vɪᴇᴡ sᴛᴀᴛᴜs", callback_data="status")],
            [InlineKeyboardButton("• Cʟᴏsᴇ •", callback_data="close")]
        ])
        await message.reply_photo(
            photo="https://ibb.co/mVkSySr7",
            caption="<b>Hᴇʏ ᴅᴜᴅᴇ...!!</b>\n <blockquote><b><i>Iᴛ's ᴀ ᴘᴏᴡᴇʀғᴜʟ sᴇᴛᴛɪɴɢs ᴍᴇɴᴜ ᴏғ ʟɪɴᴋ sʜᴀʀᴇ ʙᴏᴛ Iɴ ᴛʜɪs ʏᴏᴜ ᴄᴀɴ ᴄʜᴀɴɢᴇ ʏᴏᴜʀ sᴇᴛᴛɪɴɢs ᴇᴀsɪʟʏ ᴡɪᴛʜᴏᴜᴛ ᴀɴʏ ᴍɪsᴛᴀᴋᴇ.</i></b></blockquote>",
            reply_markup=keyboard
        )
    except Exception as e:
        logger.error(f"Error in settings command: {e}")
        await message.reply_text("An error occurred while opening the settings menu. Please try again later.")
        
# Callback query handler for settings
@Bot.on_callback_query()
async def settings_callback(client: Bot, callback_query):
    user_id = callback_query.from_user.id
    cb_data = callback_query.data
    print(f"Callback received: {cb_data} from user {user_id}")

    try:
        is_admin_user = user_id == OWNER_ID or await Seishiro.is_admin(user_id)

        # Main Settings Menu
        if cb_data == "settings_main":
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Lɪɴᴋ sʜᴀʀᴇ ᴍᴇɴᴜ", callback_data="link_share"), InlineKeyboardButton("Aᴅᴍɪɴ ᴍᴇɴᴜ", callback_data="admin_bna_system")],
                [InlineKeyboardButton("Bᴀɴ ᴍᴇɴᴜ", callback_data="ban_menu"), InlineKeyboardButton("Fsᴜʙ ᴍᴇɴᴜ", callback_data="fsub_settings_menu")],
                [InlineKeyboardButton("Vɪᴇᴡ sᴛᴀᴛᴜs", callback_data="view_status")],
                [InlineKeyboardButton("• Cʟᴏsᴇ •", callback_data="close")]
            ])
            await callback_query.edit_message_media(
                InputMediaPhoto(
                    "https://ibb.co/CsPWqnR4",
                    "<b>Hᴇʏ ᴅᴜᴅᴇ...!!</b>\n <blockquote><b><i>Iᴛ's ᴀ ᴘᴏᴡᴇʀғᴜʟ sᴇᴛᴛɪɴɢs ᴍᴇɴᴜ ᴏғ ʟɪɴᴋ sʜᴀʀᴇ ʙᴏᴛ Iɴ ᴛʜɪs ʏᴏᴜ ᴄᴀɴ ᴄʜᴀɴɢᴇ ʏᴏᴜʀ sᴇᴛᴛɪɴɢs ᴇᴀsɪʟʏ ᴡɪᴛʜᴏᴜᴛ ᴀɴʏ ᴍɪsᴛᴀᴋᴇ.</i></b></blockquote>"),
                reply_markup=keyboard)

        elif cb_data == "close":
            await callback_query.message.delete()
            try:
                await callback_query.message.reply_to_message.delete()
            except:
                pass

        elif cb_data == "link_share":
            btn = [
                [InlineKeyboardButton("Aᴅᴅ Cʜᴀɴɴᴇʟ", callback_data="add_channel"), InlineKeyboardButton("Dᴇʟᴇᴛᴇ Cʜᴀɴɴᴇʟ", callback_data="delete_channel")],
                [InlineKeyboardButton("Nᴏʀᴍᴀʟ Lɪɴᴋs", callback_data="channel_links"), InlineKeyboardButton("Rᴇǫᴜᴇsᴛ Lɪɴᴋs", callback_data="request_links")],
                [InlineKeyboardButton("Lɪsᴛ Cʜᴀɴɴᴇʟs", callback_data="list_channels")],
                [InlineKeyboardButton("back", callback_data="settings_main")]]
            await callback_query.message.edit_text("<blockquote><b><i>Iɴ ᴛʜɪs ʏᴏᴜ ᴄᴀɴ ᴄʜᴀɴɢᴇ ᴀɴᴅ ᴠɪᴇᴡ ʏᴏᴜʀs ᴄʜᴀɴɴᴇʟs...!!</i></b></blockquote>", reply_markup=InlineKeyboardMarkup(btn))

        elif cb_data == "view_status":
            total_users = await Seishiro.total_users_count()
            # Calculate uptime properly using datetime
            current_time = datetime.now()
            uptime_delta = current_time - client.uptime
            uptime_seconds = uptime_delta.total_seconds()
            uptime = time.strftime("%Hh%Mm%Ss", time.gmtime(uptime_seconds))
            await callback_query.answer(f"•Bᴏᴛ ᴜᴘᴛɪᴍᴇ: {uptime}\n•Tᴏᴛᴀʟ ᴜsᴇʀs: {total_users}\n•Vᴇʀsɪᴏɴ: 2.05v", show_alert=True)
            
        elif cb_data == "about":
            user = await client.get_users(OWNER_ID)
            await callback_query.edit_message_media(
                InputMediaPhoto(
                    "https://ibb.co/DHqBS4V7",
                    ABOUT_TXT
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton('• ʙᴀᴄᴋ', callback_data='start'), 
                     InlineKeyboardButton('ᴄʟᴏsᴇ •', callback_data='close')]
                ])
            )

        elif cb_data == "help":
            await callback_query.edit_message_media(
                InputMediaPhoto(
                    "https://ibb.co/CsPWqnR4",
                    HELP_TXT.format(
                        first=callback_query.from_user.first_name,
                        last=callback_query.from_user.last_name or "",
                        username=f"@{callback_query.from_user.username}" if callback_query.from_user.username else "None",
                        mention=callback_query.from_user.mention,
                        id=callback_query.from_user.id)),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton('• ʙᴀᴄᴋ', callback_data='start'), 
                     InlineKeyboardButton('ᴄʟᴏsᴇ •', callback_data='close')]
                ])
            )
        
        elif cb_data == "start":
            user_id = callback_query.from_user.id
            # Check if user is owner or admin in database
            is_admin = (user_id == OWNER_ID) or await Seishiro.is_admin(user_id)

            if is_admin:
                # Show Settings button for admins/owner
                inline_buttons = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("• ᴀʙᴏᴜᴛ", callback_data="about"),
                            InlineKeyboardButton("Hᴇʟᴘ •", callback_data="help")
                        ],
                        [
                            InlineKeyboardButton("Sᴇᴛᴛɪɴɢs", callback_data="settings_main")
                        ]
                    ]
                )
            else:
                # Hide Settings for normal users
                inline_buttons = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("• ᴀʙᴏᴜᴛ", callback_data="about"),
                            InlineKeyboardButton("Hᴇʟᴘ •", callback_data="help")
                        ]
                    ]
                )
                
            try:
                await callback_query.edit_message_media(
                    InputMediaPhoto(START_PIC, START_MSG.format(
                        first=callback_query.from_user.first_name,
                        last=callback_query.from_user.last_name or "",
                        username=f"@{callback_query.from_user.username}" if callback_query.from_user.username else "None",
                        mention=callback_query.from_user.mention,
                        id=callback_query.from_user.id)),
                    reply_markup=inline_buttons
                )
            except Exception as e:
                print(f"Error sending start/home photo: {e}")
                await callback_query.edit_message_text(
                    START_MSG.format(
                        first=callback_query.from_user.first_name,
                        last=callback_query.from_user.last_name or "",
                        username=f"@{callback_query.from_user.username}" if callback_query.from_user.username else "None",
                        mention=callback_query.from_user.mention,
                        id=callback_query.from_user.id),
                    reply_markup=inline_buttons,
                    parse_mode=ParseMode.HTML
                )

        # Ban Menu
        elif cb_data == "ban_menu":
            if not is_admin_user:
                await callback_query.answer("Only admins can access this!", show_alert=True)
                return
            
            btn = [
                [InlineKeyboardButton("Bᴀɴ Usᴇʀ", callback_data="ban_user"), 
                 InlineKeyboardButton("Uɴʙᴀɴ Usᴇʀ", callback_data="unban_user")],
                [InlineKeyboardButton("Bᴀɴɴᴇᴅ Lɪsᴛ", callback_data="banned_list")],
                [InlineKeyboardButton("back", callback_data="settings_main")]
            ]
            await callback_query.message.edit_text(
                "<blockquote><b><i>Iɴ ᴛʜɪs ʏᴏᴜ ᴄᴀɴ ʙᴀɴ, ᴜɴʙᴀɴ ᴀɴᴅ sᴇᴇ ᴛʜᴇ ʙᴀɴɴᴇᴅ ᴜsᴇʀs.</i></b></blockquote>",
                reply_markup=InlineKeyboardMarkup(btn)
            )

        # Ban User
        elif cb_data == "ban_user":
            if not is_admin_user:
                await callback_query.answer("Only admins can ban users!", show_alert=True)
                return
            
            btn = [[InlineKeyboardButton("back", callback_data="ban_menu")]]
            await callback_query.message.edit_text(
                "<b>Sᴇɴᴅ ᴛʜᴇ ᴜsᴇʀ ID ᴡʜɪᴄʜ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ʙᴀɴ (e.g., 123456789):\n\n"
                "Yᴏᴜ ᴄᴀɴ ᴀʟsᴏ ᴘʀᴏᴠɪᴅᴇ ᴀ ʀᴇᴀsᴏɴ:\n"
                "<code>user_id reason</code>\n\n"
                "/cancel ᴛᴏ ᴄᴀɴᴄᴇʟ</b>",
                reply_markup=InlineKeyboardMarkup(btn)
            )
            
            try:
                msg = await client.listen(chat_id=callback_query.message.chat.id, timeout=300)
                await callback_query.message.delete()
                
                if msg.text == '/cancel':
                    await msg.reply("ᴄᴀɴᴄᴇʟʟᴇᴅ!", reply_markup=InlineKeyboardMarkup(btn))
                    return
                
                parts = msg.text.split(maxsplit=1)
                user_id_str = parts[0]
                reason = parts[1] if len(parts) > 1 else "No reason provided"
                
                if not user_id_str.lstrip('-').isdigit():
                    await msg.reply(
                        "<b><blockquote expandable>Iɴᴠᴀʟɪᴅ ᴜsᴇʀ ID. Pʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ.</blockquote></b>",
                        reply_markup=InlineKeyboardMarkup(btn)
                    )
                    return
                
                ban_user_id = int(user_id_str)
                
                await Seishiro.ban_data.update_one(
                    {"_id": ban_user_id},
                    {"$set": {
                        "ban_status.is_banned": True,
                        "ban_status.ban_reason": reason,
                        "ban_status.banned_on": date.today().isoformat()
                    }},
                    upsert=True
                )
                
                await msg.reply(
                    f"<b>Usᴇʀ - `{ban_user_id}` Is sᴜᴄᴄᴇssғᴜʟʟʏ ʙᴀɴɴᴇᴅ. Success\nRᴇᴀsᴏɴ:- {reason}</b>",
                    reply_markup=InlineKeyboardMarkup(btn)
                )
            except asyncio.TimeoutError:
                await callback_query.message.reply(
                    "<b>Tɪᴍᴇᴏᴜᴛ! Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.</b>",
                    reply_markup=InlineKeyboardMarkup(btn)
                )
            except Exception as e:
                print(f"Error banning user: {e}")
                await msg.reply(f"Uɴᴇxᴘᴇᴄᴛᴇᴅ Eʀʀᴏʀ: {str(e)}", reply_markup=InlineKeyboardMarkup(btn))

        # Unban User
        elif cb_data == "unban_user":
            if not is_admin_user:
                await callback_query.answer("Only admins can unban users!", show_alert=True)
                return
            
            btn = [[InlineKeyboardButton("back", callback_data="ban_menu")]]
            await callback_query.message.edit_text(
                "<b>Sᴇɴᴅ ᴛʜᴇ ᴜsᴇʀ ID ᴛᴏ ᴜɴʙᴀɴ (e.g., 123456789):\n\n/cancel ᴛᴏ ᴄᴀɴᴄᴇʟ</b>",
                reply_markup=InlineKeyboardMarkup(btn)
            )
            
            try:
                msg = await client.listen(chat_id=callback_query.message.chat.id, timeout=300)
                await callback_query.message.delete()
                
                if msg.text == '/cancel':
                    await msg.reply("ᴄᴀɴᴄᴇʟʟᴇᴅ!", reply_markup=InlineKeyboardMarkup(btn))
                    return
                
                if not msg.text.lstrip('-').isdigit():
                    await msg.reply(
                        "<b><blockquote expandable>Iɴᴠᴀʟɪᴅ ᴜsᴇʀ ID. Pʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ.</blockquote></b>",
                        reply_markup=InlineKeyboardMarkup(btn)
                    )
                    return
                
                unban_user_id = int(msg.text)
                
                result = await Seishiro.ban_data.update_one(
                    {"_id": unban_user_id},
                    {"$set": {
                        "ban_status.is_banned": False,
                        "ban_status.ban_reason": "",
                        "ban_status.banned_on": None
                    }}
                )
                
                if result.matched_count == 0:
                    await msg.reply(
                        f"<b>Usᴇʀ - `{unban_user_id}` ɴᴏᴛ ғᴏᴜɴᴅ ɪɴ ᴅᴀᴛᴀʙᴀsᴇ.</b>",
                        reply_markup=InlineKeyboardMarkup(btn)
                    )
                else:
                    await msg.reply(
                        f"<b>Usᴇʀ - `{unban_user_id}` Is sᴜᴄᴄᴇssғᴜʟʟʏ ᴜɴʙᴀɴɴᴇᴅ. Success</b>",
                        reply_markup=InlineKeyboardMarkup(btn)
                    )
            except asyncio.TimeoutError:
                await callback_query.message.reply(
                    "<b>Tɪᴍᴇᴏᴜᴛ! Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.</b>",
                    reply_markup=InlineKeyboardMarkup(btn)
                )
            except Exception as e:
                print(f"Error unbanning user: {e}")
                await msg.reply(f"Uɴᴇxᴘᴇᴄᴛᴇᴅ Eʀʀᴏʀ: {str(e)}", reply_markup=InlineKeyboardMarkup(btn))

        # Banned List - FIXED: Removed reply_markup from answer()
        elif cb_data == "banned_list":
            if not is_admin_user:
                await callback_query.answer("Only admins can view banned list!", show_alert=True)
                return
            
            await callback_query.answer("Pʟᴇᴀsᴇ ᴡᴀɪᴛ...")
            
            try:
                cursor = Seishiro.ban_data.find({"ban_status.is_banned": True})
                lines = []
                
                async for user in cursor:
                    uid = user['_id']
                    reason = user.get('ban_status', {}).get('ban_reason', 'No reason')
                    try:
                        user_obj = await client.get_users(uid)
                        name = user_obj.mention
                    except PeerIdInvalid:
                        name = f"`{uid}` (Name not found)"
                    except Exception:
                        name = f"`{uid}`"
                    lines.append(f"• {name} - {reason}")
                
                btn = [[InlineKeyboardButton("back", callback_data="ban_menu")]]
                
                if not lines:
                    await callback_query.message.edit_text(
                        "<b>Nᴏ ᴜsᴇʀ(s) ɪs ᴄᴜʀʀᴇɴᴛʟʏ ʙᴀɴɴᴇᴅ</b>",
                        reply_markup=InlineKeyboardMarkup(btn)
                    )
                else:
                    await callback_query.message.edit_text(
                        "Bᴀɴɴᴇᴅ ᴜsᴇʀ(s)\n\n" + "\n".join(lines[:50]),
                        reply_markup=InlineKeyboardMarkup(btn)
                    )
            except Exception as e:
                btn = [[InlineKeyboardButton("back", callback_data="ban_menu")]]
                await callback_query.message.edit_text(
                    f"<b>An error occurred while fetching banned users:</b> `{e}`",
                    reply_markup=InlineKeyboardMarkup(btn)
                )

        # Fsub Settings Menu
        elif cb_data == "fsub_settings_menu":
            if not is_admin_user:
                await callback_query.answer("Only admins can access this!", show_alert=True)
                return
            
            btn = [
                [InlineKeyboardButton("Aᴅᴅ Cʜᴀɴɴᴇʟ", callback_data="add_fsub_channel"), InlineKeyboardButton("Rᴇᴍᴏᴠᴇ Cʜᴀɴɴᴇʟ", callback_data="delete_fsub_channel")],
                [InlineKeyboardButton("Lɪsᴛ Cʜᴀɴɴᴇʟs", callback_data="list_fsub_channels")],
                [InlineKeyboardButton("Tᴏᴏɢʟᴇ Rᴇǫ A", callback_data="fsub_all_channels"), InlineKeyboardButton("Tᴏᴏɢʟᴇ Rᴇǫ B", callback_data="fsub_particular")],
                [InlineKeyboardButton("back", callback_data="settings_main")]
            ]
            await callback_query.message.edit_text(
                "<blockquote><b><i>Iᴛ's ʏᴏᴜʀs ғᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ᴍᴇɴᴜ ɪɴ ᴛʜɪs ʏᴏᴜ ᴄᴀɴ ᴀᴅᴅ, ᴅᴇʟᴇᴛᴇ, ᴠɪᴇᴡ, ʀᴇǫᴜᴇsᴛ ʏᴏᴜʀ ғᴏʀᴄᴇ sᴜʙ ᴄʜᴀɴɴᴇʟs.</i></b></blockquote>",
                reply_markup=InlineKeyboardMarkup(btn)
            )

        # All Channels Toggle
        elif cb_data == "fsub_all_channels":
            if not is_admin_user:
                await callback_query.answer("Only admins can access this!", show_alert=True)
                return
            
            fsub_channels = await Seishiro.get_fsub_channels()
            
            if not fsub_channels:
                await callback_query.answer("No fsub channels found! Add channels first.", show_alert=True)
                return
            
            btn = [
                [InlineKeyboardButton("Eɴᴀʙʟᴇ Aʟʟ", callback_data="fsub_enable_all"),
                 InlineKeyboardButton("Dɪsᴀʙʟᴇ Aʟʟ", callback_data="fsub_disable_all")],
                [InlineKeyboardButton("back", callback_data="fsub_settings_menu")]
            ]
            
            await callback_query.message.edit_text(
                f"<blockquote><b>Iɴ ᴛʜɪs ʏᴏᴜ ᴄᴀɴ ᴛᴏɢɢʟᴇ ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ ғᴏʀᴄᴇ sᴜʙ ᴡɪᴛʜ ᴀ sɪɴɢʟᴇ ᴄʟɪᴄᴋ.\n"
                f"Tᴏᴛᴀʟ Fsᴜʙ Cʜᴀɴɴᴇʟs: {len(fsub_channels)}</b></blockquote>",
                reply_markup=InlineKeyboardMarkup(btn)
            )

        # Enable All Channels
        elif cb_data == "fsub_enable_all":
            if not is_admin_user:
                await callback_query.answer("Only admins can perform this action!", show_alert=True)
                return
            
            await callback_query.answer("Pʟᴇᴀsᴇ ᴡᴀɪᴛ")
            
            try:
                status = await Seishiro.set_channel_mode_all("on")
                
                btn = [[InlineKeyboardButton("back", callback_data="fsub_all_channels")]]
                await callback_query.message.edit_text(
                    f"<b>Rᴇǫᴜᴇsᴛ Fsᴜʙ Eɴᴀʙʟᴇᴅ!</b>",
                    reply_markup=InlineKeyboardMarkup(btn)
                )
            except Exception as e:
                btn = [[InlineKeyboardButton("back", callback_data="fsub_all_channels")]]
                await callback_query.message.edit_text(
                    f"<b>Eʀʀᴏʀ: {str(e)}</b>",
                    reply_markup=InlineKeyboardMarkup(btn)
                )

        # Disable All Channels
        elif cb_data == "fsub_disable_all":
            if not is_admin_user:
                await callback_query.answer("Only admins can perform this action!", show_alert=True)
                return
            
            await callback_query.answer("Pʟᴇᴀsᴇ ᴡᴀɪᴛ")
            
            try:
                status = await Seishiro.set_channel_mode_all("off")
                
                btn = [[InlineKeyboardButton("back", callback_data="fsub_all_channels")]]
                await callback_query.message.edit_text(
                    f"<b>Rᴇǫᴜᴇsᴛ Fsᴜʙ Dɪsᴀʙʟᴇᴅ!</b>",
                    reply_markup=InlineKeyboardMarkup(btn)
                )
            except Exception as e:
                btn = [[InlineKeyboardButton("back", callback_data="fsub_all_channels")]]
                await callback_query.message.edit_text(
                    f"<b>Eʀʀᴏʀ: {str(e)}</b>",
                    reply_markup=InlineKeyboardMarkup(btn)
                )

        # Particular Fsub Channel Management
        elif cb_data == "fsub_particular":
            if not is_admin_user:
                await callback_query.answer("Only admins can access this!", show_alert=True)
                return
            
            channels = await Seishiro.get_fsub_channels()
            if not channels:
                await callback_query.answer("No fsub channels found!", show_alert=True)
                return
            
            buttons = []
            for cid in channels:
                try:
                    chat = await client.get_chat(cid)
                    mode = await Seishiro.get_channel_mode(cid)
                    status = "ON" if mode == "on" else "OFF"
                    buttons.append([InlineKeyboardButton(
                        f"{chat.title}", 
                        callback_data=f"rfs_ch_{cid}"
                    )])
                except Exception as e:
                    print(f"Error fetching channel {cid}: {e}")
                    continue

            buttons.append([InlineKeyboardButton("back", callback_data="fsub_settings_menu")])
            
            await callback_query.message.edit_text(
                "<b><i><u>sᴇʟᴇᴄᴛ ᴀ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴛᴏɢɢʟᴇ ɪᴛs ғᴏʀᴄᴇ-sᴜʙ ᴍᴏᴅᴇ:</u></i></b>",
                reply_markup=InlineKeyboardMarkup(buttons)
            )

        # Handle specific channel fsub toggle
        elif cb_data.startswith("rfs_ch_"):
            cid = int(cb_data.split("_")[2])
            try:
                chat = await client.get_chat(cid)
                mode = await Seishiro.get_channel_mode(cid)
                status = "ON" if mode == "on" else "OFF"
                new_mode = "off" if mode == "on" else "on"
                buttons = [
                    [InlineKeyboardButton(
                        f"ʀᴇǫ ᴍᴏᴅᴇ {'OFF' if mode == 'on' else 'ON'}", 
                        callback_data=f"rfs_toggle_{cid}_{new_mode}"
                    )],
                    [InlineKeyboardButton("back", callback_data="fsub_particular")]
                ]
                await callback_query.message.edit_text(
                    f"Cʜᴀɴɴᴇʟ: {chat.title}\nCᴜʀʀᴇɴᴛ Fᴏʀᴄᴇ-Sᴜʙ Mᴏᴅᴇ: {status}",
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
            except Exception as e:
                await callback_query.answer("Failed to fetch channel info", show_alert=True)

        # Toggle specific channel mode
        elif cb_data.startswith("rfs_toggle_"):
            parts = cb_data.split("_")
            cid = int(parts[2])
            action = parts[3]
            mode = "on" if action == "on" else "off"

            await Seishiro.set_channel_mode(cid, mode)
            await callback_query.answer(f"Force-Sub set to {'ON' if mode == 'on' else 'OFF'}")

            # Refresh the channel's mode view
            chat = await client.get_chat(cid)
            status = "ON" if mode == "on" else "OFF"
            new_mode = "off" if mode == "on" else "on"
            buttons = [
                [InlineKeyboardButton(
                    f"ʀᴇǫ ᴍᴏᴅᴇ {'OFF' if mode == 'on' else 'ON'}", 
                    callback_data=f"rfs_toggle_{cid}_{new_mode}"
                )],
                [InlineKeyboardButton("back", callback_data="fsub_particular")]
            ]
            await callback_query.message.edit_text(
                f"Channel: {chat.title}\nCurrent Force-Sub Mode: {status}",
                reply_markup=InlineKeyboardMarkup(buttons)
            )

        # Add Fsub Channel
        elif cb_data == "add_fsub_channel":
            if not is_admin_user:
                await callback_query.answer("Only admins can add channels!", show_alert=True)
                return
            
            btn = [[InlineKeyboardButton("back", callback_data="fsub_settings_menu")]]
            await callback_query.message.edit_text(
                "<b>Sᴇɴᴅ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ID ᴡʜɪᴄʜ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴀᴅᴅ ɪɴ ғsᴜʙ (e.g., -100123456789):\n\n/cancel ᴛᴏ ᴄᴀɴᴄᴇʟ</b>",
                reply_markup=InlineKeyboardMarkup(btn)
            )
            
            try:
                msg = await client.listen(chat_id=callback_query.message.chat.id, timeout=300)
                temp = await msg.reply("<i>Pʟᴇᴀsᴇ ᴡᴀɪᴛ...</i>")
                await callback_query.message.delete()
                
                if msg.text == '/cancel':
                    await temp.edit("ᴄᴀɴᴄᴇʟʟᴇᴅ!", reply_markup=InlineKeyboardMarkup(btn))
                    return
                
                # Validate channel ID format
                if not re.match(r"^-100\d{10,}$", msg.text):
                    await temp.edit(
                        "<b><blockquote expandable>Iɴᴠᴀʟɪᴅ ᴄʜᴀɴɴᴇʟ ID. Mᴜsᴛ ʙᴇ ɪɴ ᴛʜᴇ ғᴏʀᴍᴀᴛ -100XXXXXXXXXX.</blockquote></b>",
                        reply_markup=InlineKeyboardMarkup(btn)
                    )
                    return
                
                channel_id = int(msg.text)
                
                # Check if bot is a member of the channel
                try:
                    chat_member = await client.get_chat_member(channel_id, client.me.id)
                    valid_statuses = [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
                    
                    if chat_member.status not in valid_statuses:
                        await temp.edit(
                            f"<b><blockquote expandable>I ᴀᴍ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ᴏғ ᴛʜɪs ᴄʜᴀɴɴᴇʟ. Sᴛᴀᴛᴜs: {chat_member.status}. Pʟᴇᴀsᴇ ᴍᴀᴋᴇ ᴍᴇ ᴀᴅᴍɪɴ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ.</blockquote></b>",
                            reply_markup=InlineKeyboardMarkup(btn)
                        )
                        return
                except UserNotParticipant:
                    await temp.edit(
                        "<b><blockquote expandable>I ᴀᴍ ɴᴏᴛ ᴀ ᴍᴇᴍʙᴇʀ ᴏғ ᴛʜɪs ᴄʜᴀɴɴᴇʟ. Pʟᴇᴀsᴇ ᴀᴅᴅ ᴍᴇ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ.</blockquote></b>",
                        reply_markup=InlineKeyboardMarkup(btn)
                    )
                    return
                except RPCError as e:
                    if "CHANNEL_INVALID" in str(e):
                        await temp.edit(
                            "<b><blockquote expandable>Iɴᴠᴀʟɪᴅ ᴄʜᴀɴɴᴇʟ ID ᴏʀ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ᴅᴏᴇs ɴᴏᴛ ᴇxɪsᴛ. Pʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ᴛʜᴇ ID ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ.</blockquote></b>",
                            reply_markup=InlineKeyboardMarkup(btn)
                        )
                        return
                    print(f"RPC Error checking membership for channel {channel_id}: {e}")
                    await temp.edit(
                        f"<b><blockquote expandable>Fᴀɪʟᴇᴅ ᴛᴏ ᴠᴇʀɪғʏ ᴍᴇᴍʙᴇʀsʜɪᴘ. Eʀʀᴏʀ: {str(e)}.</blockquote></b>",
                        reply_markup=InlineKeyboardMarkup(btn)
                    )
                    return
                
                # Fetch chat details
                try:
                    chat = await client.get_chat(channel_id)
                except RPCError as e:
                    print(f"Error fetching chat {channel_id}: {e}")
                    await temp.edit(
                        f"<b><blockquote expandable>Fᴀɪʟᴇᴅ ᴛᴏ ᴀᴄᴄᴇss ᴄʜᴀɴɴᴇʟ. Eʀʀᴏʀ: {str(e)}.</blockquote></b>",
                        reply_markup=InlineKeyboardMarkup(btn)
                    )
                    return
                
                # Get invite link
                try:
                    link = await client.export_chat_invite_link(chat.id)
                except Exception:
                    link = f"https://t.me/{chat.username}" if chat.username else f"https://t.me/c/{str(chat.id)[4:]}"
                
                # Add to fsub
                await Seishiro.add_fsub_channel(channel_id)
                
                await temp.edit(
                    f"<b>Fᴏʀᴄᴇ-sᴜʙ ᴄʜᴀɴɴᴇʟ ᴀᴅᴅᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!</b>\n\n"
                    f"<b>Nᴀᴍᴇ:</b> <a href='{link}'>{chat.title}</a>\n"
                    f"<b>Iᴅ:</b> <code>{channel_id}</code>",
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup(btn)
                )
            except asyncio.TimeoutError:
                await callback_query.message.reply(
                    "<b>Tɪᴍᴇᴏᴜᴛ! Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.</b>",
                    reply_markup=InlineKeyboardMarkup(btn)
                )
            except Exception as e:
                print(f"Error adding fsub channel: {e}")
                await temp.edit(
                    f"<b>Failed to add channel:</b>\n<code>{channel_id}</code>\n\n<i>{e}</i>",
                    reply_markup=InlineKeyboardMarkup(btn)
                )

        # Remove Fsub Channel
        elif cb_data == "delete_fsub_channel":
            if not is_admin_user:
                await callback_query.answer("Only admins can delete channels!", show_alert=True)
                return
            
            btn = [[InlineKeyboardButton("back", callback_data="fsub_settings_menu")]]
            await callback_query.message.edit_text(
                "<b>Sᴇɴᴅ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ID ᴛᴏ ʀᴇᴍᴏᴠᴇ ғʀᴏᴍ ғsᴜʙ (e.g., -100123456789):\n\n/cancel ᴛᴏ ᴄᴀɴᴄᴇʟ</b>",
                reply_markup=InlineKeyboardMarkup(btn)
            )
            
            try:
                msg = await client.listen(chat_id=callback_query.message.chat.id, timeout=300)
                await callback_query.message.delete()
                
                if msg.text == '/cancel':
                    await msg.reply("ᴄᴀɴᴄᴇʟʟᴇᴅ!", reply_markup=InlineKeyboardMarkup(btn))
                    return
                
                channel_id = int(msg.text)
                await Seishiro.remove_fsub_channel(channel_id)
                await msg.reply(
                    f"<b><blockquote expandable>Cʜᴀɴɴᴇʟ {channel_id} ʜᴀs ʙᴇᴇɴ ʀᴇᴍᴏᴠᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ.</blockquote></b>",
                    reply_markup=InlineKeyboardMarkup(btn)
                )
            except (ValueError, IndexError):
                await msg.reply(
                    "<b><blockquote expandable>Iɴᴠᴀʟɪᴅ ᴄʜᴀɴɴᴇʟ ID. Pʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ.</blockquote></b>",
                    reply_markup=InlineKeyboardMarkup(btn)
                )
            except Exception as e:
                print(f"Error deleting channel {msg.text}: {e}")
                await msg.reply(f"Unexpected Error: {str(e)}", reply_markup=InlineKeyboardMarkup(btn))

        # List Fsub Channels - NEW FEATURE
        elif cb_data == "list_fsub_channels":
            if not is_admin_user:
                await callback_query.answer("Only admins can view fsub channels!", show_alert=True)
                return
            
            await callback_query.answer("Fᴇᴛᴄʜɪɴɢ ғsᴜʙ ᴄʜᴀɴɴᴇʟs...")
            
            try:
                fsub_channels = await Seishiro.get_fsub_channels()
                
                btn = [[InlineKeyboardButton("back", callback_data="fsub_settings_menu")]]
                
                if not fsub_channels:
                    await callback_query.message.edit_text(
                        "<b>Nᴏ ғsᴜʙ ᴄʜᴀɴɴᴇʟs ғᴏᴜɴᴅ.\n\nPʟᴇᴀsᴇ ᴀᴅᴅ ᴄʜᴀɴɴᴇʟs ᴜsɪɴɢ 'Aᴅᴅ Fsᴜʙ Cʜᴀɴɴᴇʟ' ᴏᴘᴛɪᴏɴ.</b>",
                        reply_markup=InlineKeyboardMarkup(btn)
                    )
                    return
                
                fsub_list = "<b>Fsᴜʙ Cʜᴀɴɴᴇʟs Lɪsᴛ:</b>\n\n"
                
                for idx, channel_id in enumerate(fsub_channels, 1):
                    try:
                        chat = await client.get_chat(channel_id)
                        mode = await Seishiro.get_channel_mode(channel_id)
                        status_emoji = "ON" if mode == "on" else "OFF"
                        status_text = "Rᴇǫᴜᴇsᴛ ON" if mode == "on" else "Rᴇǫᴜᴇsᴛ OFF"
                        
                        # Try to get invite link
                        try:
                            link = await client.export_chat_invite_link(chat.id)
                            fsub_list += f"{idx}. <a href='{link}'>{chat.title}</a> {status_emoji}\n"
                        except:
                            if chat.username:
                                link = f"https://t.me/{chat.username}"
                                fsub_list += f"{idx}. <a href='{link}'>{chat.title}</a> {status_emoji}\n"
                            else:
                                fsub_list += f"{idx}. {chat.title} {status_emoji}\n"
                        
                        fsub_list += f"    <code>{channel_id}</code> - {status_text}\n\n"
                        
                    except Exception as e:
                        print(f"Error fetching channel {channel_id}: {e}")
                        fsub_list += f"{idx}. <code>{channel_id}</code> (Error fetching info)\n\n"
                
                fsub_list += f"<b>Tᴏᴛᴀʟ Fsᴜʙ Cʜᴀɴɴᴇʟs: {len(fsub_channels)}</b>\n"
                fsub_list += "\n<i>ON = Request Mode ON | OFF = Request Mode OFF</i>"
                
                await callback_query.message.edit_text(
                    fsub_list,
                    reply_markup=InlineKeyboardMarkup(btn),
                    disable_web_page_preview=True
                )
            except Exception as e:
                btn = [[InlineKeyboardButton("back", callback_data="fsub_settings_menu")]]
                await callback_query.message.edit_text(
                    f"<b>Eʀʀᴏʀ ғᴇᴛᴄʜɪɴɢ ғsᴜʙ ᴄʜᴀɴɴᴇʟs:</b> {str(e)}",
                    reply_markup=InlineKeyboardMarkup(btn)
                )

    
