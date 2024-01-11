import json
from pyrogram import *
from pyrogram.types import *
from pyromod import listen
from prettytable import PrettyTable
import sqlite3
# =====================================================================
with open('config.json', 'r') as config_file:
    config_data = json.load(config_file)
api_id = config_data['api_id']
api_hash = config_data['api_hash']
bot_token = config_data['bot_token']
# =====================================================================
app = Client("FlashCardBot", api_id=api_id,api_hash=api_hash, bot_token=bot_token)
# =====================================================================
con = sqlite3.connect("db/words.db")
cur = con.cursor()
cur.execute('''
CREATE TABLE IF NOT EXISTS words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT NOT NULL UNIQUE,
    correct INTEGER DEFAULT 0,
    incorrect INTEGER DEFAULT 0
)
''')
con.commit()
# =====================================================================
Keyboard = ReplyKeyboardMarkup(
    [
        ["📥 Add Words 📥", "👁 Display Words 👁"],
        ["📝 Edit Word 📝", "🧹 Delete Word 🧹"],
        ["📚 Take Test 📚"],
        ["🗂 Display Test Results 🗂"],
        ["👨‍💻 Developer 👨‍💻"]
    ], resize_keyboard=True
)
Keyboard_Section_Add = ReplyKeyboardMarkup(
    [
        ["🔙 Back 🔙"],

    ], resize_keyboard=True
)
Keyboard_Take_Test = ReplyKeyboardMarkup(
    [
        ["yes","no"],

    ], resize_keyboard=True
)
# =====================================================================
@app.on_message(filters.command("start"))
async def Start(client, message):
    cur = con.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS words (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word TEXT NOT NULL UNIQUE,
        correct INTEGER DEFAULT 0,
        incorrect INTEGER DEFAULT 0
    )
''')
    con.commit()
    await message.reply_text(f"""🔥Hello <b>{message.from_user.mention}</b> ,
With this robot, you can remember the words well, test yourself with tests""",
                             reply_markup=Keyboard, parse_mode=enums.ParseMode.HTML)
# =====================================================================
async def Home(client, message):
        await message.reply_text(f"""What can I do?
Use the options below👇""",reply_markup=Keyboard)
# =====================================================================
@app.on_message(filters.regex("^📥 Add Words 📥$"))
async def Add_Word(client, message):
    while True:
        add_word = await message.chat.ask("[?] Please enter the word you want to add : ",reply_markup=Keyboard_Section_Add)
        word = add_word.text
        try:
            # Check if the word already exists in the database
            cur.execute('SELECT id FROM words WHERE word = ?', (word,))
            existing_word = cur.fetchone()
            if existing_word:
                await message.reply_text(f'❗️ The word "**{word}**" already exists in the database.')
            else:
                # Add the word to the database
                cur.execute('INSERT INTO words (word) VALUES (?)', (word,))
                con.commit()
                await message.reply_text(f'✅ The word "**{word}**" has been added to the database.')
        except Exception as e:
            await message.reply_text(f'❌ Error: {e}')
        if word == "🔙 Back 🔙":
            await Home(client, message)
            break
# =====================================================================
@app.on_message(filters.regex("^👁 Display Words 👁$"))
async def Display_Words(client, message):
    try:
        # Display all words
        cur.execute('SELECT id, word FROM words')
        result = cur.fetchall()
        table = PrettyTable(['ID', 'Word'])
        for row in result:
            table.add_row([row[0], row[1]])
        with open("display_words.txt", "w") as f:
            f.write(f"{table}")
        await app.send_document(message.chat.id,"display_words.txt",reply_markup=Keyboard)
    except Exception as e:
        await message.reply_text(f'❌ Error: {e}')
# =====================================================================
@app.on_message(filters.regex("^📝 Edit Word 📝$"))
async def Edit_Word(client, message):
    word_id = await message.chat.ask("[?] Please enter the ID of the word you want to edit: : ",reply_markup=Keyboard)
    new_word = await message.chat.ask("[?] Please enter the new word : ",reply_markup=Keyboard)
    try:
        # Edit a word by ID
        cur.execute('UPDATE words SET word = ? WHERE id = ?', (new_word.text, word_id.text))
        con.commit()
        await message.reply_text(f'✅ The word with ID {word_id.text} has been edited to "{new_word.text}".')
    except Exception as e:
        await message.reply_text(f'❌ Error: {e}')
# =====================================================================
@app.on_message(filters.regex("^🧹 Delete Word 🧹$"))
async def Delete_Word(client, message):
    word_id = await message.chat.ask("[?] Please enter the ID of the word you want to edit: : ",reply_markup=Keyboard)
    try:
        # Delete a word by ID
        cur.execute('DELETE FROM words WHERE id = ?', (word_id.text,))
        con.commit()
        await message.reply_text(f'✅ The word with ID {word_id.text} has been deleted.')
    except Exception as e:
        await message.reply_text(f'❌ Error: {e}')
# =====================================================================
def get_random_words(count):
    # Get a specified number of random words
    cur.execute('SELECT word FROM words ORDER BY RANDOM() LIMIT ?', (count,))
    result = cur.fetchall()
    return [row[0] for row in result]
# =====================================================================
@app.on_message(filters.regex("^📚 Take Test 📚$"))
async def Take_Test(client, message):
    try:
        # Take a test
        num_random_words = await message.chat.ask(f'[?] Enter the number of test questions you want to be asked')
        random_words = get_random_words(num_random_words.text)
        for i, word in enumerate(random_words, start=1):
            user_input = await message.chat.ask(f'[?] {i}. Do you know the meaning of "**{word}**"? (yes/no): ',reply_markup=Keyboard_Take_Test)
            if user_input.text == 'yes':
                cur.execute('UPDATE words SET correct = correct + 1 WHERE word = ?', (word,))
            else:
                cur.execute('UPDATE words SET incorrect = incorrect + 1 WHERE word = ?', (word,))
        con.commit()
        await Home(client, message)
    except Exception as e:
        print(f'Error: {e}')
# =====================================================================
# @app.on_message(filters.regex("^🗂 Display Test Results 🗂$"))
# async def Display_Test_Results(client, message):
#     try:
#         # Display test results
#         cur.execute('SELECT correct, incorrect FROM words')
#         result = cur.fetchall()
#         correct = [row[0] for row in result]
#         incorrect = [row[1] for row in result]
#         await message.reply_text(f'{correct}')
#         await message.reply_text(f'{incorrect}')
#     except Exception as e:
#         print(f'❌ Error: {e}')
# =====================================================================
@app.on_message(filters.regex("^👨‍💻 Developer 👨‍💻$"))
async def Developer(client, message):
    await message.reply_text("Communication with programming", reply_markup=InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Telegram",
                    url="https://t.me/MrTakDev"
                ),
                InlineKeyboardButton(
                    "Twitter",
                    url="https://twitter.com/erfan_banaei"
                ),
            ],
            [ 
                InlineKeyboardButton(
                    "Linkedin",
                    url="https://www.linkedin.com/in/erfanbanaeii"
                ),
                InlineKeyboardButton(
                    "Github",
                    url="https://github.com/erfanbanaei/"
                )
        ]
        ]
    )
    )
# =====================================================================
app.run()
