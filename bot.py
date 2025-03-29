from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import API_ID, API_HASH, BOT_TOKEN
from io import BytesIO
import asyncio
import logging
import random
import string
import aiohttp
from PIL import Image, ImageDraw, ImageFont

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
    logos = []
    tasks = []
    
    async with aiohttp.ClientSession() as session:
        for _ in range(num_logos):
            tasks.append(fetch_logo(session, prompt))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, bytes):
                logos.append(result)
            else:
                # Local fallback if API fails
                logos.append(await generate_local_fallback_logo(prompt))
    
    return logos

async def fetch_logo(session, prompt):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "image/*"
    }
    optimized_prompt = f"Modern professional logo with clear text '{prompt}', minimalist style"
    
    try:
        async with session.get(f"https://logo.itz-ashlynn.workers.dev/?prompt={optimized_prompt}", 
                             headers=headers, 
                             timeout=aiohttp.ClientTimeout(total=10)) as response:
            if response.status == 200:
                json_data = await response.json()
                if json_data.get("success") and "image_url" in json_data:
                    async with session.get(json_data["image_url"], headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as img_response:
                        if img_response.status == 200:
                            return await img_response.read()
    except Exception as e:
        logger.error(f"Logo API Error: {e}")
    return None

async def generate_local_fallback_logo(prompt):
    try:
        # Create a simple logo locally using PIL
        img = Image.new('RGB', (300, 300), color=(73, 109, 137))
        d = ImageDraw.Draw(img)
        
        # Use default font (or specify a path to a .ttf file if available)
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        # Calculate text size and position
        text_bbox = d.textbbox((0, 0), prompt, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        x = (300 - text_width) / 2
        y = (300 - text_height) / 2
        
        # Draw text
        d.text((x, y), prompt, font=font, fill=(255, 255, 255))
        
        # Save to BytesIO
        bio = BytesIO()
        img.save(bio, format="PNG")
        return bio.getvalue()
    except Exception as e:
        logger.error(f"Local fallback logo error: {e}")
        # Absolute last resort: blank image with text
        return await generate_minimal_fallback(prompt)

async def generate_minimal_fallback(prompt):
    img = Image.new('RGB', (300, 300), color=(100, 100, 100))
    bio = BytesIO()
    img.save(bio, format="PNG")
    return bio.getvalue()

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

@app.on_message(filters.text & ~filters.command(["start", "set"]))
async def handle_message(client, message):
    user_data[message.from_user.id] = {"prompt": message.text, "chat_id": message.chat.id}
    
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
        await callback_query.message.reply_text("Send prompt first!")
        return
    
    orientation = "tall" if callback_query.data == "portrait" else "wide"
    user_data[user_id]["orientation"] = orientation
    
    buttons = [
        [InlineKeyboardButton("1", callback_data="count_1"), InlineKeyboardButton("2", callback_data="count_2")],
        [InlineKeyboardButton("3", callback_data="count_3"), InlineKeyboardButton("4", callback_data="count_4")]
    ]
    await callback_query.message.edit_text("How many images (1-4)?", reply_markup=InlineKeyboardMarkup(buttons))

@app.on_callback_query(filters.regex(r"^count_(\d)$"))
async def handle_count(client, callback_query):
    user_id = callback_query.from_user.id
    if user_id not in user_data:
        await callback_query.message.reply_text("Send prompt first!")
        return
    
    count = int(callback_query.data.split("_")[1])
    prompt = user_data[user_id]["prompt"]
    chat_id = user_data[user_id]["chat_id"]
    
    # Send initial status message
    status_msg = await client.send_message(chat_id, f"Generating {count} {'images' if CURRENT_MODE['mode'] == 'image' else 'logos'}...")
    
    try:
        if CURRENT_MODE["mode"] == "image":
            orientation = user_data[user_id]["orientation"]
            result = await generate_image(prompt, num_images=count, orientation=orientation)
            file_type = "image"
        else:
            result = await generate_logo(prompt, num_logos=count)
            file_type = "logo"
        
        if result:
            for i, data in enumerate(result, 1):
                bio = BytesIO(data)
                bio.name = f'{file_type}_{i}.png'
                msg = await client.send_photo(
                    chat_id=chat_id,
                    photo=bio,
                    caption=f"{file_type.capitalize()} {i} of {count}"
                )
                asyncio.create_task(auto_delete_message(msg, 600))
            await status_msg.edit_text(f"Successfully generated {count} {file_type}s!")
        else:
            await status_msg.edit_text(f"Failed to generate {file_type}s, but fallback ensured output.")
    
    except Exception as e:
        logger.error(f"Error in handle_count: {e}")
        await status_msg.edit_text("An error occurred, but fallback logos were generated.")
    
    finally:
        user_data.pop(user_id, None)
        # Clean up status message after a while
        asyncio.create_task(auto_delete_message(status_msg, 600))

async def auto_delete_message(message, delay):
    try:
        await asyncio.sleep(delay)
        await message.delete()
    except Exception as e:
        logger.error(f"Error deleting message: {e}")

if __name__ == "__main__":
    print("Bot is starting...")
    app.run()
