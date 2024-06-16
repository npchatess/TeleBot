from pyrogram import Client, filters
import re, logging, random, nltk
from info import TG_NAME, PREFIX

logging.basicConfig(level=logging.INFO)

nltk.download('words')
english_words = set(nltk.corpus.words.words())

ONE9 = False
used_words = set()  # Store used words here
trigger_pattern = re.compile(f"Turn: {TG_NAME}")

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
        
        # Classic Mode Patterns
        classic_pattern = re.compile(r"start with ([A-Z]) and include at least (\d+) letters")
        classic_match = re.search(classic_pattern, puzzle_text)
        
        # Required Letter Mode Patterns
        required_letter_pattern = re.compile(r"start with ([A-Z]), include ([A-Z]) and at least (\d+) letters")
        required_letter_match = re.search(required_letter_pattern, puzzle_text)

        if classic_match:
            starting_letter = classic_match.group(1)
            min_length = int(classic_match.group(2))

            valid_words = [word for word in english_words if word.startswith(starting_letter) and len(word) >= min_length and word not in used_words]

            if valid_words:
                random_word = random.choice(valid_words)
                used_words.add(random_word)
                response_message = random_word
                await client.send_message(message.chat.id, response_message)
            else:
                await message.reply("No valid words found for the given criteria.")
        
        elif required_letter_match:
            starting_letter = required_letter_match.group(1)
            required_letter = required_letter_match.group(2)
            min_length = int(required_letter_match.group(3))

            valid_words = [word for word in english_words if word.startswith(starting_letter) and required_letter in word and len(word) >= min_length and word not in used_words]

            if valid_words:
                random_word = random.choice(valid_words)
                used_words.add(random_word)
                response_message = random_word
                await client.send_message(message.chat.id, response_message)
            else:
                await message.reply("No valid words found for the given criteria.")

        else:
            await message.reply("Criteria not found in the puzzle text.")
