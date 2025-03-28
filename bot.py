from pyrogram import Client, filters
from config import API_ID, API_HASH, BOT_TOKEN
from main import generate_image
from io import BytesIO

app = Client(
    "my_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("Hello! Mujhe ek text bhejo, aur main uske basis par ek image generate karunga.")

@app.on_message(filters.text)
async def handle_message(client, message):
    if not message.text.startswith('/'):
        text = message.text
        await message.reply_text("Image generate kar raha hoon, thodi der wait karo...")
        
        image_data = generate_image(text)
        
        if image_data:
            bio = BytesIO(image_data)
            bio.name = 'image.jpg'
            await message.reply_photo(photo=bio)
        else:
            await message.reply_text("Sorry, image generate nahi kar paya. Kuch der baad try karo.")

if __name__ == "__main__":
    print("Bot is starting...")
    app.run()
