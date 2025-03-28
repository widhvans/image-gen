from pyrogram import Client, filters
from config import API_ID, API_HASH, BOT_TOKEN
from main import generate_image
from io import BytesIO

# Bot client setup
app = Client(
    "my_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# /start command handler
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("Hello! Mujhe ek text bhejo, aur main uske basis par ek image generate karunga.")

# Text message handler (non-command text messages only)
@app.on_message(filters.text)
async def handle_message(client, message):
    # Check karna ki message command nahi hai
    if not message.text.startswith('/'):
        text = message.text  # User ka message lena
        await message.reply_text("Image generate kar raha hoon, thodi der wait karo...")
        
        image_data = generate_image(text)  # Image generate karna
        
        if image_data:
            # Image data ko file object mein convert karna
            bio = BytesIO(image_data)
            bio.name = 'image.jpg'
            await message.reply_photo(photo=bio)
        else:
            await message.reply_text("Sorry, image generate nahi kar paya. Kuch der baad try karo.")

# Bot start karna
if __name__ == "__main__":
    print("Bot is starting...")
    app.run()
