from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import API_ID, API_HASH, BOT_TOKEN
from io import BytesIO
import asyncio
import logging
import random
import string
from pyrogram.errors import QueryIdInvalid
import aiohttp

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# User data storage
user_data = {}

# Telegram Bot Setup
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Adult keywords
ADULT_KEYWORDS = ["nude", "naked", "sex", "adult", "xxx", "porn", "hot", "sexy", "erotic", "nsfw", "boobs", "pussy"]

# Current mode
CURRENT_MODE = {"mode": "image"}

def enhance_prompt(prompt, orientation="wide"):
    quality_keywords = "sharp focus, vivid colors, studio lighting, ultra HD"
    return f"A detailed, realistic {prompt}, {quality_keywords}"

async def generate_image(prompt, num_images=1, orientation="wide"):
    async with aiohttp.ClientSession() as session:
        images = []
        enhanced_prompt = enhance_prompt(prompt, orientation)
        
        tasks = []
        for _ in range(num_images):
            random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            params = {
                "prompt": enhanced_prompt,
                "improve": "true",
                "format": orientation,
                "random": random_str
            }
            tasks.append(fetch_image(session, params))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, bytes):
                images.append(result)
        
        return images if images else None

async def fetch_image(session, params):
    try:
        async with session.get("https://img.hazex.workers.dev/", params=params, timeout=aiohttp.ClientTimeout(total=15)) as response:
            if response.status == 200:
                return await response.read()
            logger.error(f"Image API Error: Status {response.status}")
    except Exception as e:
        logger.error(f"Image API Error: {e}")
    return None

async def generate_logo(prompt, num_logos=1):
    async with aiohttp.ClientSession() as session:
        logos = []
        optimized_prompt = f"Modern professional logo with clear text '{prompt}', minimalist style"
        
        tasks = []
        for _ in range(num_logos):
            tasks.append(fetch_logo(session, optimized_prompt))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, bytes):
                logos.append(result)
        
        return logos if logos else None

async def fetch_logo(session, prompt):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "image/*"
    }
    
    for attempt in range(2):  # 2 attempts max
        try:
            async with session.get(f"https://logo.itz-ashlynn.workers.dev/?prompt={prompt}", 
                                 headers=headers, 
                                 timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    json_data = await response.json()
                    if json_data.get("success") and "image_url" in json_data:
                        async with session.get(json_data["image_url"], headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as img_response:
                            if img_response.status == 200:
                                return await img_response.read()
                break
        except Exception as e:
            logger.error(f"Logo API Error (attempt {attempt + 1}): {e}")
            if attempt == 0:
                await asyncio.sleep(1)  # Short delay before retry
    
    # Fallback
    logger.info("Using fallback logo generation")
    return await generate_fallback_logo(prompt)

async def generate_fallback_logo(prompt):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://via.placeholder.com/300x300.png?text={prompt}") as response:
                if response.status == 200:
                    return await response.read()
    except Exception as e:
        logger.error(f"Fallback logo error: {e}")
    return None

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("Hello! Send me text to generate images or logos.\nUse /set to change mode.")

@app.on_message(filters.command("set"))
async def set_mode(client, message):
    buttons = [
        [InlineKeyboardButton("Images", callback_data="set_image")],
        [InlineKeyboardButton("Logo", callback_data="set_logo")]
    ]
    await message.reply_text("Select mode:", reply_markup=InlineKeyboardMarkup(buttons))

@app.on_callback_query(filters.regex(r"^set_(image|logo)$"))
async def handle_set_mode(client, callback_query):
    mode = callback_query.data.split("_")[1]
    CURRENT_MODE["mode"] = mode
    await callback_query.message.edit_text(f"Mode set to: {mode}")
    try:
        await callback_query.answer()
    except QueryIdInvalid:
        logger.warning("Callback query expired in handle_set_mode")

@app.on_message(filters.text & ~filters.command(["start", "set"]))
async def handle_message(client, message):
    user_data[message.from_user.id] = {"prompt": message.text}
    
    if CURRENT_MODE["mode"] == "image":
        buttons = [
            [InlineKeyboardButton("Portrait", callback_data="portrait")],
            [InlineKeyboardButton("Landscape", callback_data="landscape")]
        ]
        await message.reply_text("Select image orientation:", reply_markup=InlineKeyboardMarkup(buttons))
    else:
        buttons = [
            [InlineKeyboardButton("1", callback_data="count_1"), InlineKeyboardButton("2", callback_data="count_2")],
            [InlineKeyboardButton("3", callback_data="count_3"), InlineKeyboardButton("4", callback_data="count_4")]
        ]
        await message.reply_text("How many logos (1-4)?", reply_markup=InlineKeyboardMarkup(buttons))

@app.on_callback_query(filters.regex(r"^(portrait|landscape)$"))
async def handle_orientation(client, callback_query):
    user_id = callback_query.from_user.id
    if user_id not in user_data:
        try:
            await callback_query.answer("Send prompt first!", cache_time=5)
        except QueryIdInvalid:
            logger.warning("Callback query expired in handle_orientation")
        return
    
    orientation = "tall" if callback_query.data == "portrait" else "wide"
    user_data[user_id]["orientation"] = orientation
    
    buttons = [
        [InlineKeyboardButton("1", callback_data="count_1"), InlineKeyboardButton("2", callback_data="count_2")],
        [InlineKeyboardButton("3", callback_data="count_3"), InlineKeyboardButton("4", callback_data="count_4")]
    ]
    await callback_query.message.edit_text("How many images (1-4)?", reply_markup=InlineKeyboardMarkup(buttons))
    try:
        await callback_query.answer()
    except QueryIdInvalid:
        logger.warning("Callback query expired in handle_orientation")

@app.on_callback_query(filters.regex(r"^count_(\d)$"))
async def handle_count(client, callback_query):
    user_id = callback_query.from_user.id
    if user_id not in user_data:
        try:
            await callback_query.answer("Send prompt first!", cache_time=5)
        except QueryIdInvalid:
            logger.warning("Callback query expired in handle_count (no user data)")
        return
    
    count = int(callback_query.data.split("_")[1])
    prompt = user_data[user_id]["prompt"]
    
    try:
        if CURRENT_MODE["mode"] == "image":
            orientation = user_data[user_id]["orientation"]
            await callback_query.message.edit_text(f"Generating {count} images...")
            result = await generate_image(prompt, num_images=count, orientation=orientation)
            file_type = "image"
        else:
            await callback_query.message.edit_text(f"Generating {count} logos...")
            result = await generate_logo(prompt, num_logos=count)
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
            
            # Small delay to ensure photo sends before edit
            await asyncio.sleep(0.5)
            await callback_query.message.edit_text(f"{count} {file_type}s generated!")
            try:
                await callback_query.answer("Done!")
            except QueryIdInvalid:
                logger.warning("Callback query expired after successful generation")
        else:
            await callback_query.message.edit_text(f"Failed to generate {file_type}s. Try again!")
            try:
                await callback_query.answer("Generation failed!", cache_time=5)
            except QueryIdInvalid:
                logger.warning("Callback query expired after generation failure")
    
    except Exception as e:
        logger.error(f"Error in handle_count: {e}")
        await callback_query.message.edit_text("An error occurred. Try again!")
        try:
            await callback_query.answer("Error occurred!", cache_time=5)
        except QueryIdInvalid:
            logger.warning("Callback query expired in error handling")
    
    finally:
        user_data.pop(user_id, None)

async def auto_delete_message(message, delay):
    try:
        await asyncio.sleep(delay)
        await message.delete()
    except Exception as e:
        logger.error(f"Error deleting message: {e}")

if __name__ == "__main__":
    print("Bot is starting...")
    app.run()
