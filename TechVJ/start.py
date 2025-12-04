# Don't Remove Credit Tg - @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import asyncio 
import time
import pyrogram
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message 
from config import API_ID, API_HASH, ERROR_MESSAGE, LOGIN_SYSTEM, STRING_SESSION, CHANNEL_ID, WAITING_TIME
from database.db import db
from TechVJ.strings import HELP_TXT
from bot import TechVJUser

class batch_temp(object):
    IS_BATCH = {}

class ProgressTracker:
    def __init__(self, message, type):
        self.message = message
        self.type = type
        self.start_time = time.time()
        self.last_update_time = self.start_time
        self.last_bytes = 0

    def format_bytes(self, bytes):
        if bytes >= 1024 * 1024 * 1024:
            return f"{bytes / (1024 * 1024 * 1024):.2f} GB"
        elif bytes >= 1024 * 1024:
            return f"{bytes / (1024 * 1024):.2f} MB"
        elif bytes >= 1024:
            return f"{bytes / 1024:.2f} KB"
        else:
            return f"{bytes} B"

    def format_time(self, seconds):
        if seconds >= 3600:
            return f"{int(seconds // 3600)}h {int((seconds % 3600) // 60)}m {int(seconds % 60)}s"
        elif seconds >= 60:
            return f"{int(seconds // 60)}m {int(seconds % 60)}s"
        else:
            return f"{int(seconds)}s"

    def get_progress_bar(self, percentage):
        filled_length = int(20 * percentage // 100)
        bar = '█' * filled_length + '░' * (20 - filled_length)
        return f"[{bar}]"

    def calculate_speed(self, current_bytes):
        current_time = time.time()
        time_diff = current_time - self.last_update_time
        bytes_diff = current_bytes - self.last_bytes
        
        if time_diff > 0:
            speed = bytes_diff / time_diff
        else:
            speed = 0
            
        self.last_update_time = current_time
        self.last_bytes = current_bytes
        return speed

    def calculate_eta(self, current, total, speed):
        if speed > 0:
            remaining_bytes = total - current
            eta = remaining_bytes / speed
            return eta
        return 0

async def downstatus(client, statusfile, message, chat):
    while True:
        if os.path.exists(statusfile):
            break
        await asyncio.sleep(3)
      
    while os.path.exists(statusfile):
        with open(statusfile, "r") as downread:
            txt = downread.read()
        try:
            await client.edit_message_text(chat, message.id, f"**Download Progress:**\n{txt}")
            await asyncio.sleep(10)
        except:
            await asyncio.sleep(5)

async def upstatus(client, statusfile, message, chat):
    while True:
        if os.path.exists(statusfile):
            break
        await asyncio.sleep(3)      
    
    while os.path.exists(statusfile):
        with open(statusfile, "r") as upread:
            txt = upread.read()
        try:
            await client.edit_message_text(chat, message.id, f"**Upload Progress:**\n{txt}")
            await asyncio.sleep(10)
        except:
            await asyncio.sleep(5)

def progress(current, total, message, type):
    tracker = getattr(message, f'{type}_tracker', None)
    if tracker is None:
        tracker = ProgressTracker(message, type)
        setattr(message, f'{type}_tracker', tracker)
    
    percentage = current * 100 / total
    progress_bar = tracker.get_progress_bar(percentage)
    
    speed = tracker.calculate_speed(current)
    speed_text = tracker.format_bytes(speed) + "/s"
    
    eta = tracker.calculate_eta(current, total, speed)
    eta_text = tracker.format_time(eta) if eta > 0 else "Calculating..."
    
    current_size = tracker.format_bytes(current)
    total_size = tracker.format_bytes(total)
    
    elapsed_time = time.time() - tracker.start_time
    elapsed_text = tracker.format_time(elapsed_time)
    
    progress_text = (
        f"{progress_bar} {percentage:.1f}%\n"
        f"📊 **Progress:** {current_size} / {total_size}\n"
        f"🚀 **Speed:** {speed_text}\n"
        f"⏱️ **Elapsed:** {elapsed_text}\n"
        f"⏳ **ETA:** {eta_text}"
    )
    
    with open(f'{message.id}{type}status.txt', "w", encoding='utf-8') as fileup:
        fileup.write(progress_text)

# start command
@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
    buttons = [[
        InlineKeyboardButton("❣️ Developer", url = "https://t.me/kingvj01")
    ],[
        InlineKeyboardButton('🔍 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url='https://t.me/vj_bot_disscussion'),
        InlineKeyboardButton('🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/vj_bots')
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await client.send_message(
        chat_id=message.chat.id, 
        text=f"<b>👋 Hi {message.from_user.mention}, I am Save Restricted Content Bot, I can send you restricted content by its post link.\n\nFor downloading restricted content /login first.\n\nKnow how to use bot by - /help</b>", 
        reply_markup=reply_markup, 
        reply_to_message_id=message.id
    )
    return

# help command
@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    await client.send_message(
        chat_id=message.chat.id, 
        text=f"{HELP_TXT}"
    )

# cancel command
@Client.on_message(filters.command(["cancel"]))
async def send_cancel(client: Client, message: Message):
    batch_temp.IS_BATCH[message.from_user.id] = True
    await client.send_message(
        chat_id=message.chat.id, 
        text="**Batch Successfully Cancelled.**"
    )

@Client.on_message(filters.text & filters.private)
async def save(client: Client, message: Message):
    # Joining chat
    if ("https://t.me/+" in message.text or "https://t.me/joinchat/" in message.text) and LOGIN_SYSTEM == False:
        if TechVJUser is None:
            await client.send_message(message.chat.id, "String Session is not Set", reply_to_message_id=message.id)
            return
        try:
            try:
                await TechVJUser.join_chat(message.text)
            except Exception as e: 
                await client.send_message(message.chat.id, f"Error : {e}", reply_to_message_id=message.id)
                return
            await client.send_message(message.chat.id, "Chat Joined", reply_to_message_id=message.id)
        except UserAlreadyParticipant:
            await client.send_message(message.chat.id, "Chat already Joined", reply_to_message_id=message.id)
        except InviteHashExpired:
            await client.send_message(message.chat.id, "Invalid Link", reply_to_message_id=message.id)
        return
    
    if "https://t.me/" in message.text:
        if batch_temp.IS_BATCH.get(message.from_user.id) == False:
            return await message.reply_text("**One Task Is Already Processing. Wait For Complete It. If You Want To Cancel This Task Then Use - /cancel**")
        datas = message.text.split("/")
        temp = datas[-1].replace("?single","").split("-")
        fromID = int(temp[0].strip())
        try:
            toID = int(temp[1].strip())
        except:
            toID = fromID

        if LOGIN_SYSTEM == True:
            user_data = await db.get_session(message.from_user.id)
            if user_data is None:
                await message.reply("**For Downloading Restricted Content You Have To /login First.**")
                return
            api_id = int(await db.get_api_id(message.from_user.id))
            api_hash = await db.get_api_hash(message.from_user.id)
            try:
                acc = Client("saverestricted", session_string=user_data, api_hash=api_hash, api_id=api_id)
                await acc.connect()
            except:
                return await message.reply("**Your Login Session Expired. So /logout First Then Login Again By - /login**")
        else:
            if TechVJUser is None:
                await client.send_message(message.chat.id, f"**String Session is not Set**", reply_to_message_id=message.id)
                return
            acc = TechVJUser
				
        batch_temp.IS_BATCH[message.from_user.id] = False
        for msgid in range(fromID, toID+1):
            if batch_temp.IS_BATCH.get(message.from_user.id): break
            
            # private
            if "https://t.me/c/" in message.text:
                chatid = int("-100" + datas[4])
                try:
                    await handle_private(client, acc, message, chatid, msgid)
                except Exception as e:
                    if ERROR_MESSAGE == True:
                        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
    
            # bot
            elif "https://t.me/b/" in message.text:
                username = datas[4]
                try:
                    await handle_private(client, acc, message, username, msgid)
                except Exception as e:
                    if ERROR_MESSAGE == True:
                        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
            
            # public
            else:
                username = datas[3]

                try:
                    msg = await client.get_messages(username, msgid)
                except UsernameNotOccupied: 
                    await client.send_message(message.chat.id, "The username is not occupied by anyone", reply_to_message_id=message.id)
                    return
                try:
                    # Send to user
                    user_msg = await client.copy_message(message.chat.id, msg.chat.id, msg.id, reply_to_message_id=message.id)
                    
                    # Forward to channel if CHANNEL_ID is set (instant - no re-upload)
                    if CHANNEL_ID:
                        try:
                            await client.forward_messages(CHANNEL_ID, message.chat.id, user_msg.id)
                        except Exception as e:
                            if ERROR_MESSAGE == True:
                                await client.send_message(message.chat.id, f"Error forwarding to channel: {e}", reply_to_message_id=message.id)
                except:
                    try:    
                        await handle_private(client, acc, message, username, msgid)               
                    except Exception as e:
                        if ERROR_MESSAGE == True:
                            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

            # wait time
            await asyncio.sleep(WAITING_TIME)
        if LOGIN_SYSTEM == True:
            try:
                await acc.disconnect()
            except:
                pass                				
        batch_temp.IS_BATCH[message.from_user.id] = True

# handle private
async def handle_private(client: Client, acc, message: Message, chatid: int, msgid: int):
    msg: Message = await acc.get_messages(chatid, msgid)
    if msg.empty: return 
    msg_type = get_message_type(msg)
    if not msg_type: return 
    
    # Always send to user
    user_chat = message.chat.id
    
    if batch_temp.IS_BATCH.get(message.from_user.id): return 
    
    if "Text" == msg_type:
        try:
            # Send to user
            user_msg = await client.send_message(user_chat, msg.text, entities=msg.entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            
            # Forward to channel if CHANNEL_ID is set (instant - no re-upload)
            if CHANNEL_ID:
                try:
                    await client.forward_messages(CHANNEL_ID, user_chat, user_msg.id)
                except Exception as e:
                    if ERROR_MESSAGE == True:
                        await client.send_message(message.chat.id, f"Error forwarding text to channel: {e}", reply_to_message_id=message.id)
            return 
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            return 

    smsg = await client.send_message(message.chat.id, '**📥 Downloading...**', reply_to_message_id=message.id)
    asyncio.create_task(downstatus(client, f'{message.id}downstatus.txt', smsg, user_chat))
    try:
        file = await acc.download_media(msg, progress=progress, progress_args=[message,"down"])
        os.remove(f'{message.id}downstatus.txt')
    except Exception as e:
        if ERROR_MESSAGE == True:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML) 
        return await smsg.delete()
    
    if batch_temp.IS_BATCH.get(message.from_user.id): return 
    asyncio.create_task(upstatus(client, f'{message.id}upstatus.txt', smsg, user_chat))

    if msg.caption:
        caption = msg.caption
    else:
        caption = None
        
    if batch_temp.IS_BATCH.get(message.from_user.id): return 
    
    # Function to send media to user (with progress) and get the sent message
    async def send_media_to_user():
        user_msg = None
        
        if "Document" == msg_type:
            try:
                ph_path = await acc.download_media(msg.document.thumbs[0].file_id)
            except:
                ph_path = None
            
            try:
                user_msg = await client.send_document(user_chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
            except Exception as e:
                if ERROR_MESSAGE == True:
                    await client.send_message(message.chat.id, f"Error sending document to user: {e}", reply_to_message_id=message.id)
            finally:
                if ph_path and os.path.exists(ph_path):
                    os.remove(ph_path)

        elif "Video" == msg_type:
            try:
                ph_path = await acc.download_media(msg.video.thumbs[0].file_id)
            except:
                ph_path = None
            
            try:
                user_msg = await client.send_video(user_chat, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
            except Exception as e:
                if ERROR_MESSAGE == True:
                    await client.send_message(message.chat.id, f"Error sending video to user: {e}", reply_to_message_id=message.id)
            finally:
                if ph_path and os.path.exists(ph_path):
                    os.remove(ph_path)

        elif "Animation" == msg_type:
            try:
                user_msg = await client.send_animation(user_chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            except Exception as e:
                if ERROR_MESSAGE == True:
                    await client.send_message(message.chat.id, f"Error sending animation to user: {e}", reply_to_message_id=message.id)
            
        elif "Sticker" == msg_type:
            try:
                user_msg = await client.send_sticker(user_chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            except Exception as e:
                if ERROR_MESSAGE == True:
                    await client.send_message(message.chat.id, f"Error sending sticker to user: {e}", reply_to_message_id=message.id)     

        elif "Voice" == msg_type:
            try:
                user_msg = await client.send_voice(user_chat, file, caption=caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
            except Exception as e:
                if ERROR_MESSAGE == True:
                    await client.send_message(message.chat.id, f"Error sending voice to user: {e}", reply_to_message_id=message.id)

        elif "Audio" == msg_type:
            try:
                ph_path = await acc.download_media(msg.audio.thumbs[0].file_id)
            except:
                ph_path = None

            try:
                user_msg = await client.send_audio(user_chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])   
            except Exception as e:
                if ERROR_MESSAGE == True:
                    await client.send_message(message.chat.id, f"Error sending audio to user: {e}", reply_to_message_id=message.id)
            finally:
                if ph_path and os.path.exists(ph_path):
                    os.remove(ph_path)

        elif "Photo" == msg_type:
            try:
                user_msg = await client.send_photo(user_chat, file, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            except Exception as e:
                if ERROR_MESSAGE == True:
                    await client.send_message(message.chat.id, f"Error sending photo to user: {e}", reply_to_message_id=message.id)
        
        return user_msg

    # Send to user first and get the message object
    user_msg = await send_media_to_user()
    
    # Forward to channel if exists (instant - no re-upload)
    if CHANNEL_ID and user_msg:
        try:
            await client.forward_messages(CHANNEL_ID, user_chat, user_msg.id)
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error forwarding to channel: {e}", reply_to_message_id=message.id)
    
    # Cleanup
    if os.path.exists(f'{message.id}upstatus.txt'): 
        os.remove(f'{message.id}upstatus.txt')
    if os.path.exists(file):
        os.remove(file)
    await client.delete_messages(message.chat.id,[smsg.id])

# get the type of message
def get_message_type(msg: pyrogram.types.messages_and_media.message.Message):
    try:
        msg.document.file_id
        return "Document"
    except:
        pass

    try:
        msg.video.file_id
        return "Video"
    except:
        pass

    try:
        msg.animation.file_id
        return "Animation"
    except:
        pass

    try:
        msg.sticker.file_id
        return "Sticker"
    except:
        pass

    try:
        msg.voice.file_id
        return "Voice"
    except:
        pass

    try:
        msg.audio.file_id
        return "Audio"
    except:
        pass

    try:
        msg.photo.file_id
        return "Photo"
    except:
        pass

    try:
        msg.text
        return "Text"
    except:
        pass
