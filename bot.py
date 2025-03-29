
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import API_ID, API_HASH, BOT_TOKEN
from io import BytesIO
import asyncio
import logging
import requests
import random
import string
from pyrogram.errors import QueryIdInvalid

# Setup logging to debug errors
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# User data storage
user_data = {}

# Telegram Bot Setup
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Adult keywords (kept but not used in prompt enhancement)
ADULT_KEYWORDS = ["nude", "naked", "sex", "adult", "xxx", "porn", "hot", "sexy", "erotic", "nsfw", "boobs", "pussy"]

# Current mode (default: image generation)
CURRENT_MODE = {"mode": "image"}  # Can be "image" or "logo"

def enhance_prompt(prompt, orientation="wide"):
    quality_keywords = "with perfect anatomy, sharp focus, vivid colors, and studio lighting, photographed with a professional DSLR camera, 50mm lens, f/1.8 aperture, in ultra HD quality"
    enhanced_prompt = f"A highly detailed, hyper-realistic, award-winning photograph of {prompt}, {quality_keywords}"
    return enhanced_prompt

def generate_image(prompt, num_images=1, orientation="wide"):
    images = []
    enhanced_prompt = enhance_prompt(prompt, orientation)
    
    for _ in range(num_images):
        random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        params = {
            "prompt": enhanced_prompt,
            "improve": "true",
            "format": orientation,
            "random": random_str
        }
        
        try:
            response = requests.get("https://img.hazex.workers.dev/", params=params, timeout=10)
            if response.status_code == 200:
                images.append(response.content)
            else:
                logger.error(f"Image API Error: Status code {response.status_code}")
        except requests.RequestException as e:
            logger.error(f"Image API Error: {e}")
    
    return images if images else None

def generate_logo(prompt, num_logos=1):
    logos = []
    for _ in range(num_logos):
        try:
            # Step 1: Call the logo API to get the JSON response
            url = f"https://logo.itz-ashlynn.workers.dev/?prompt={prompt}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                json_data = response.json()
                if json_data.get("success") and "image_url" in json_data:
                    # Step 2: Fetch the actual image from the image_url
                    image_response = requests.get(json_data["image_url"], timeout=10)
                    if image_response.status_code == 200:
                        logos.append(image_response.content)
                    else:
                        logger.error(f"Logo Image Fetch Error: Status code {image_response.status_code}")
                else:
                    logger.error(f"Logo API Response Error: {json_data.get('msg', 'Unknown error')}")
            else:
                logger.error(f"Logo API Error: Status code {response.status_code}")
        except requests.RequestException as e:
            logger.error(f"Logo API Error: {e}")
    
    return logos if logos else None

@app.on_message(filters.command("start"))
async def start(client, message):
    try:
        await message.reply_text("Hello! Mujhe ek text bhejo, aur main uske basis par images ya logos generate karunga.\nUse /set to change mode (image/logo).")
    except Exception as e:
        logger.error(f"Error in start: {e}")

@app.on_message(filters.command("set"))
async def set_mode(client, message):
    try:
        args = message.text.split()
        if len(args) != 2 or args[1] not in ["image", "logo"]:
            await message.reply_text("Usage: /set [image|logo]")
            return
        mode = args[1]
        CURRENT_MODE["mode"] = mode
        await message.reply_text(f"Mode set to: {mode}")
    except Exception as e:
        logger.error(f"Error in set_mode: {e}")

@app.on_message(filters.text & ~filters.command(["start", "set"]))
async def handle_message(client, message):
    try:
        text = message.text
        user_data[message.from_user.id] = {"prompt": text}
        
        if CURRENT_MODE["mode"] == "image":
            buttons = [
                [InlineKeyboardButton("Portrait", callback_data="portrait")],
                [InlineKeyboardButton("Landscape", callback_data="landscape")]
            ]
            await message.reply_text(
                "Image orientation select karo:",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        elif CURRENT_MODE["mode"] == "logo":
            buttons = [
                [InlineKeyboardButton("1", callback_data="count_1"),
                 InlineKeyboardButton("2", callback_data="count_2")],
                [InlineKeyboardButton("3", callback_data="count_3"),
                 InlineKeyboardButton("4", callback_data="count_4")]
            ]
            await message.reply_text(
                "Kitne logos chahiye (1-4)?",
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
        await callback_query.answer()
    except Exception as e:
        logger.error(f"Error in handle_orientation: {e}")
        await callback_query.answer("Kuch galat ho gaya, dobara try karo!", cache_time=5)

@app.on_callback_query(filters.regex(r"^count_(\d)$"))
async def handle_count(client, callback_query):
    user_id = callback_query.from_user.id
    
    try:
        if user_id not in user_data:
            await callback_query.answer("Pehle prompt bhejo!", cache_time=5)
            return
        
        count = int(callback_query.data.split("_")[1])
        prompt = user_data[user_id]["prompt"]
        
        if CURRENT_MODE["mode"] == "image":
            orientation = user_data[user_id]["orientation"]
            await callback_query.message.edit_text(f"{count} images generate kar raha hoon, thodi der wait karo...")
            result = generate_image(prompt, num_images=count, orientation=orientation)
            file_type = "image"
        else:  # logo mode
            await callback_query.message.edit_text(f"{count} logos generate kar raha hoon, thodi der wait karo...")
            result = generate_logo(prompt, num_logos=count)
            file_type = "logo"
        
        if result:
            for i, data in enumerate(result, 1):
                bio = BytesIO(data)
                bio.name = f'{file_type}_{i}.jpg'
                msg = await callback_query.message.reply_photo(
                    photo=bio,
                    caption=f"{file_type.capitalize()} {i} of {count}"
                )
                asyncio.create_task(auto_delete_message(msg, 600))
            await callback_query.answer(f"{count} {file_type}s generated!")
        else:
            await callback_query.message.edit_text(f"Sorry, {file_type}s generate nahi kar paya.")
            await callback_query.answer(f"Failed to generate {file_type}s!", cache_time=5)
        
        # Clear user data
        user_data.pop(user_id, None)
    except QueryIdInvalid:
        logger.warning("Query ID invalid, likely expired. Skipping answer.")
        await callback_query.message.edit_text("Callback expired, please try again!")
    except Exception as e:
        logger.error(f"Error in handle_count: {e}")
        try:
            await callback_query.message.edit_text("Kuch galat ho gaya, dobara try karo!")
            await callback_query.answer("Error ho gaya!", cache_time=5)
        except QueryIdInvalid:
            logger.warning("Query ID invalid in error handling, skipping answer.")

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
