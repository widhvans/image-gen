from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import API_ID, API_HASH, BOT_TOKEN
from main import generate_image
from io import BytesIO
import asyncio
import logging

# Setup logging to debug errors
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# User data storage
user_data = {}

# Telegram Bot Setup
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start(client, message):
    try:
        await message.reply_text("Hello! Mujhe ek text bhejo, aur main uske basis par images generate karunga.")
    except Exception as e:
        logger.error(f"Error in start: {e}")

@app.on_message(filters.text)
async def handle_message(client, message):
    try:
        text = message.text
        if not text.startswith('/'):
            user_data[message.from_user.id] = {"prompt": text}
            
            buttons = [
                [InlineKeyboardButton("Portrait", callback_data="portrait")],
                [InlineKeyboardButton("Landscape", callback_data="landscape")]
            ]
            await message.reply_text(
                "Image orientation select karo:",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    except Exception as e:
        logger.error(f"Error in handle_message: {e}")

@app.on_callback_query(filters.regex(r"^(portrait|landscape)$"))
async def handle_orientation(client, callback_query):
    user_id = callback_query.from_user.id
    orientation = callback_query.data
    
    try:
        if user_id not in user_data:
            await callback_query.answer("Pehle prompt bhejo!", cache_time=5)
            return
        
        user_data[user_id]["orientation"] = "tall" if orientation == "portrait" else "wide"
        
        buttons = [
            [InlineKeyboardButton("1", callback_data="count_1"),
             InlineKeyboardButton("2", callback_data="count_2")],
            [InlineKeyboardButton("3", callback_data="count_3"),
             InlineKeyboardButton("4", callback_data="count_4")]
        ]
        await callback_query.message.edit_text(
            "Kitni images chahiye (1-4)?",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        await callback_query.answer()  # Answer callback to acknowledge
    except Exception as e:
        logger.error(f"Error in handle_orientation: {e}")
        try:
            await callback_query.answer("Kuch galat ho gaya, dobara try karo!", cache_time=5)
        except Exception:
            pass

@app.on_callback_query(filters.regex(r"^count_(\d)$"))
async def handle_count(client, callback_query):
    user_id = callback_query.from_user.id
    
    try:
        if user_id not in user_data:
            await callback_query.answer("Pehle prompt bhejo!", cache_time=5)
            return
        
        count = int(callback_query.data.split("_")[1])
        prompt = user_data[user_id]["prompt"]
        orientation = user_data[user_id]["orientation"]
        
        await callback_query.message.edit_text(f"{count} images generate kar raha hoon, thodi der wait karo...")
        
        image_data_list = generate_image(prompt, num_images=count, orientation=orientation)
        
        if image_data_list:
            for i, image_data in enumerate(image_data_list, 1):
                bio = BytesIO(image_data)
                bio.name = f'image_{i}.jpg'
                msg = await callback_query.message.reply_photo(
                    photo=bio,
                    caption=f"Image {i} of {count}"
                )
                asyncio.create_task(auto_delete_message(msg, 600))
        else:
            await callback_query.message.edit_text("Sorry, images generate nahi kar paya.")
        
        # Clear user data
        user_data.pop(user_id, None)
        await callback_query.answer()  # Answer callback to acknowledge
    except Exception as e:
        logger.error(f"Error in handle_count: {e}")
        try:
            await callback_query.message.edit_text("Kuch galat ho gaya, dobara try karo!")
            await callback_query.answer("Error ho gaya!", cache_time=5)
        except Exception:
            pass

async def auto_delete_message(message, delay):
    try:
        await asyncio.sleep(delay)
        await message.delete()
    except Exception as e:
        logger.error(f"Error deleting message: {e}")

if __name__ == "__main__":
    print("Bot is starting...")
    try:
        app.run()
    except Exception as e:
        logger.error(f"Error running bot: {e}")
