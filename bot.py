from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import API_ID, API_HASH, BOT_TOKEN
from main import generate_image
from io import BytesIO
import asyncio

# User data storage
user_data = {}

# Telegram Bot Setup
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("Hello! Mujhe ek text bhejo, aur main uske basis par images generate karunga.")

@app.on_message(filters.text & ~filters.command)
async def handle_message(client, message):
    text = message.text
    user_data[message.from_user.id] = {"prompt": text}
    
    # Orientation selection buttons
    buttons = [
        [InlineKeyboardButton("Portrait", callback_data="portrait")],
        [InlineKeyboardButton("Landscape", callback_data="landscape")]
    ]
    await message.reply_text(
        "Image orientation select karo:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@app.on_callback_query(filters.regex(r"^(portrait|landscape)$"))
async def handle_orientation(client, callback_query):
    user_id = callback_query.from_user.id
    orientation = callback_query.data
    if user_id not in user_data:
        await callback_query.answer("Pehle prompt bhejo!")
        return
    
    user_data[user_id]["orientation"] = "tall" if orientation == "portrait" else "wide"
    
    # Image count selection buttons
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

@app.on_callback_query(filters.regex(r"^count_(\d)$"))
async def handle_count(client, callback_query):
    user_id = callback_query.from_user.id
    count = int(callback_query.data.split("_")[1])
    
    if user_id not in user_data:
        await callback_query.answer("Pehle prompt bhejo!")
        return
    
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
            # Auto-delete after 10 minutes (600 seconds)
            asyncio.create_task(auto_delete_message(msg, 600))
    else:
        await callback_query.message.edit_text("Sorry, images generate nahi kar paya.")
    
    # Clear user data
    user_data.pop(user_id, None)
    await callback_query.answer()

async def auto_delete_message(message, delay):
    await asyncio.sleep(delay)
    await message.delete()

if __name__ == "__main__":
    print("Bot is starting...")
    app.run()
