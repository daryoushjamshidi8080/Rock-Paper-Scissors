#librarys
from pyrogram import Client, filters
from pyrogram.types import (ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton)
from pyromod import listen
from pyrogram.errors import PeerIdInvalid,BadRequest
from pgsql import DatabaseManager
from game_class import Game



# Server information to connect to the database
db_manager = DatabaseManager(
    "rockpaperscissor",
    "postgres",
    "12345",
    "127.0.0.1",
    "5432"
)





#id and hash telegram 
api_id =19900466 
api_hash = 'fc393ce306361ef2bb938ec8d2aa84fc'
bot_token = '5414065076:AAE3R7VPCDnP5k9CDirz3ABJk0VHVGvYOSg'

app = Client("my_account", api_id=api_id, api_hash=api_hash,  bot_token=bot_token)


game = Game(app, db_manager)


#command start game 
@app.on_message(filters.command("start"))
async def main(client,message):
    #insert chat id ueser to users table 
    db_manager.insert_users(message.chat.id)
    #fetch data of table results----------------------------------------------
    db_manager.fetch_results(message.chat.id)

    #welcom message and  strat buttons
    reply_markup = ReplyKeyboardMarkup(
        [
            ['بازی سنگ کاغذ قچی']
        ],
        resize_keyboard=True 
    )

    await message.reply_text("""سلام به ربات بازی های جذاب خوش اومدین 💋
    یک از بازی های زیر را انتخاب کنید""",reply_markup=reply_markup )



#start game with buttom
@app.on_message(filters.regex("بازی سنگ کاغذ قچی"))
async def main(client,message):

    #Choosing the type of rock,paper,scissors game 
    inline_keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton('بازی بادوست', callback_data='playWithFrien')],
            [InlineKeyboardButton('بازی با سیستم', callback_data='playWithSystem')]
        ]
    )

    await message.reply_text('''لطفا یکی از گزینه های زیر را انتخاب کنید''',reply_markup=inline_keyboard)



#plye game with Friend or System
@app.on_callback_query()
async def handel_callback_query(client, callback_query):

    #play game with System 
    if callback_query.data == 'playWithSystem':
        await game.start_game(callback_query.message)
    #play game with Firend
    elif callback_query.data == 'playWithFriend':
        pass
#command to display points to the user
@app.on_message(filters.command('My_results'))
async def on_message(client, message):
    #fetch data of results table of column lost winner equal
    results = db_manager.fetch_results(message.chat.id)
    await message.reply_text(f""" امتیازات تا این لحظه
                            برد: {results[0][3]}
                            باخت:{results[0][1]}
                            مساوی:{results[0][4]}
                            .   """)



@app.on_message(filters.text)
async def on_user_choice(client, message):
    # Check if the user's message is one of the valid options
    if message.text in ['سنگ 🪨', 'کاغذ 📄', 'قیچی ✂️']:  
    # z = Calling out of the game in the middle of the game 
    # Send the option in the middle of the loop(while True)
        z = await game.handle_user_choice(message, message.text)
    try:
        # Remove unnecessary errors
        # Checking if the user has requested to exit the game
        if message.text == 'خروج از بازی' or z == 'خروج از بازی'  :
            reply_markup = ReplyKeyboardMarkup(
            [
                ['بازی سنگ کاغذ قچی']
            ],
            resize_keyboard=True 
            ) 
            
            #Send the game selection message to the user
            await message.reply_text("""یکی از بازی های زیر را انتخاب کنید""",reply_markup=reply_markup )
    except:
        await message.reply_text('چرا چرت پرت میگی چیزی بگو بفهمم از دکمه ها و کامند ها استفاده کن')





# raun libray pyrogram
app.run()
    