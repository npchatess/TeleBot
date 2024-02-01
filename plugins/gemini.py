import asyncio
import time
import re
import google.generativeai as genai
from pyrogram import Client, filters
from info import GENAI_API_KEY
from plugins.modules.emoji import emoji
from plugins.modules.spam import spam
from plugins.modules.urban import urban, meaning
from plugins.modules.facts import get_facts
from plugins.modules.quotes import get_quotes


SUDO = set()
ACCESS = False
DUMB = False

genai.configure(api_key=GENAI_API_KEY)

def gemini(text):
    try:
        generation_config = {
            "temperature": 0.6,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
        }
        safety_settings = [
          {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_ONLY_HIGH"
          },
          {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_ONLY_HIGH"
          },
          {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_ONLY_HIGH"
          },
          {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_ONLY_HIGH"
          },
        ]
        model = genai.GenerativeModel(model_name="gemini-pro",
                                      generation_config=generation_config,
                                      safety_settings=safety_settings)
        convo = model.start_chat()
        convo.send_message(text)
        return f"{convo.last.text}"
    except Exception as e:
        print(f"Error generating text: {str(e)}")
        return f"Error generating text: {str(e)}"

@Client.on_message(filters.command("start", prefixes=".") & filters.me)
async def start(_, message):
    await message.reply_text("Hello, World!")

GREETING_REGEX = re.compile(r"(?i)\b(hi+|hello+|hey+)\b", re.IGNORECASE)
TIME_OF_DAY_REGEX = re.compile(r"(?i)\b(good\s+(morning|night|evening|afternoon))\b", re.IGNORECASE)

@Client.on_message(filters.regex(GREETING_REGEX) & filters.private & ~filters.me)
async def greet(_, message):
    await message.reply(f"Hello {message.from_user.mention}*")

@Client.on_message(filters.regex(TIME_OF_DAY_REGEX) & filters.private & ~filters.me)
async def time_of_day_greet(_, message):
    time_of_day = TIME_OF_DAY_REGEX.search(message.text).group(2)
    greeting = f"Good {time_of_day.capitalize()} {message.from_user.mention}"
    await message.reply(greeting)

@Client.on_message(filters.command("ping", prefixes=".") & filters.me)   
async def ping(_, message):
    start = time.time()
    await message.edit("Pong!")
    end = time.time()
    await message.edit(f"Pong! {round(end-start, 2)}s") 

@Client.on_message(filters.command(["urban", "ud"], prefixes="."))
async def get_urban(_, message):
    if message.text:
        await message.delete()
    await urban(message)

@Client.on_message(filters.command(["meaning", "m"], prefixes="."))
async def get_meaning(_, message):
    if message.text:
        await message.delete()
    await meaning(message)

@Client.on_message(filters.command("emoji", prefixes=".") & filters.private)
async def get_emoji(_, message):
    if message.text:
        await message.delete()
    await emoji(message)

@Client.on_message(filters.command("spam", prefixes=".") & filters.me)
async def spam_message(_, message):
    await spam(message)

@Client.on_message(filters.command(["facts", "f"], prefixes=".") & filters.private)
async def fact_msg(_, message):
    if message.text:
        await message.delete()
    await get_facts(message)

@Client.on_message(filters.command(["quotes", "q", "quote"], prefixes="."))
async def get_quote(_, message):
    if message.text:
        await message.delete()
    await get_quotes(message)

@Client.on_message(filters.command("sudo", prefixes=".") & filters.me)
async def sudo(client, message):
    user_id = message.reply_to_message.from_user.id if message.reply_to_message else None
    if user_id:
        SUDO.add(user_id)
        k = await client.get_users(user_id)
        name = k.first_name if not k.last_name else k.first_name + " " + k.last_name
        m = await message.edit(f"<b>{name}</b> has been given sudo access.")
        await asyncio.sleep(5)
        await m.delete()
    else:
        m = await message.edit("Reply to a message to give sudo access to the user.")
        await asyncio.sleep(2)
        await m.delete()

@Client.on_message(filters.command("unsudo", prefixes=".") & filters.me)
async def unsudo(client, message):
    user_id = message.reply_to_message.from_user.id if message.reply_to_message else None
    if user_id and user_id in SUDO:
        SUDO.remove(user_id)
        k = await client.get_users(user_id)
        name = k.first_name if not k.last_name else k.first_name + " " + k.last_name
        m = await message.edit(f"<b>{name}</b> has been removed from sudo access.")
        await asyncio.sleep(5)
        await m.delete()
    else:
        m = await message.edit("Reply to a message to remove sudo access from the user.")
        await asyncio.sleep(3)
        await m.delete()

@Client.on_message(filters.command("access", prefixes=".") & filters.me)
async def access(_, message):
    global ACCESS
    ACCESS = not ACCESS
    m = await message.edit("Access has been granted" if ACCESS else "Access has been revoked")
    await asyncio.sleep(2)
    await m.delete()

@Client.on_message(filters.command("babo", prefixes="."))
async def gaccess(_, message):
    if message.from_user.id == 2012121532:
        global DUMB
        DUMB = not DUMB
        m = await message.edit("Now babo will shout" if DUMB else "Now babo will shut up")
        await asyncio.sleep(2)
        await m.delete()
    else:
        m = await message.edit("You are not my dumbo.")   

@Client.on_message(filters.text & filters.me)
async def genmessage(_, message):
    if ACCESS:
        await message.edit(gemini(message.text))

@Client.on_message(filters.text)
async def gen_message(_, message):
    user_id = message.from_user.id
    if ACCESS and message.from_user.id in list(SUDO):
        await message.reply(gemini(message.text))
    if DUMB and user_id == 2012121532:
        await message.reply(gemini(message.text))


