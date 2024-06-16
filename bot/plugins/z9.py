from pyrogram import Client, filters
import re, logging, random, nltk
from info import TG_NAME, PREFIX

logging.basicConfig(level=logging.INFO)

nltk.download('words')
english_words = set(nltk.corpus.words.words())

ONE9 = False
used_words = set()  # Store used words here
trigger_pattern = re.compile(r"Turn: (.*?) \(Next: (.*?)\)\nYour word must start with ([A-Z]) and include at least (\d+) letters.")
game_start_pattern = re.compile(r"Game is starting\.\.\.")

@Client.on_message(filters.command("on9", PREFIX) & filters.me)
async def one9word(client, message):
    global ONE9, used_words
    msg = message.text.split(None, 1)
    if len(msg) > 1:
        command = msg[1].lower()
        if command in ["on", "start", "true"]:
            await message.edit("On9word plugin enabled")
            ONE9 = True
        elif command in ["off", "stop", "false"]:
            await message.edit("On9word plugin disabled")
            ONE9 = False
            used_words.clear()  # Clear the used words when ONE9 is False

@Client.on_message(filters.regex(trigger_pattern))
async def handle_incoming_message(client, message):
    global ONE9, used_words
    if ONE9:
        puzzle_text = message.text

        match = re.search(trigger_pattern, puzzle_text)
        if match:
            current_player = match.group(1)
            next_player = match.group(2)
            starting_letter = match.group(3)
            min_length = int(match.group(4))

            valid_words = [word for word in english_words if word.startswith(starting_letter) and len(word) >= min_length and word not in used_words]

            if valid_words:
                random_word = random.choice(valid_words)
                used_words.add(random_word)
                response_message = f"{current_player}:\n{random_word}"
                await client.send_message(message.chat.id, response_message)
            else:
                await message.reply("No valid words found for the given criteria.")

@Client.on_message(filters.regex(game_start_pattern))
async def handle_game_start(client, message):
    global ONE9, used_words
    used_words.clear()  # Clear used words when a new game starts
    await message.reply("Game has started. Let the word chain begin!")
