#librarys
from pyrogram import Client, filters
from pyrogram.types import (ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton)
from pyromod import listen
from pyrogram.errors import PeerIdInvalid,BadRequest
import random
import psycopg2 # libary connect to databas
from pgsql import DatabaseManager


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
bot_token = '5414065076:AAH5RsguSf0OYmgRX8a2LREWidsIRPgbBbk'

app = Client("my_account", api_id=api_id, api_hash=api_hash,  bot_token=bot_token)



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
        await Game().start_game(callback_query.message)
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


#game class system 
class System:
    def choose_option(self):
        return random.choice(['سنگ 🪨', 'کاغذ 📄', 'قیچی ✂️'])#using of library random

#General game class
class Game:
    def __init__(self) :
        self.system =System()# input random system
    #start game 
    async def start_game(self, message):
        reply_keyboard = ReplyKeyboardMarkup(
            [
                ['سنگ 🪨', 'کاغذ 📄', 'قیچی ✂️'],
                ['خروج از بازی']
            ],resize_keyboard=True
        )
        await message.reply_text("""شما به بخش بازی با سیستم هدایت شدید 
        با سه بازی برنده مشخص میشود موفق باشد""", reply_markup=reply_keyboard)
    # Management of user choices in the game
    async def handle_user_choice(self, message, user_choice):
        systm = 0 # System score
        user = 0 # user score
        system_choice = self.system.choose_option()
        result = self.determine_winner(user_choice, system_choice)
        while True :            
            if result == 'مساوی' :
                systm += 1
                user +=1
                await message.reply_text(f'''شما مساوی کردین برای هر دو یک امتیاز اضافه شد
                انتخاب سیتم :{system_choice}
                امیتاز سیستم:{systm}
                امتیازشما:{user}''')
            elif result == 'شما بردید' :
                user +=1
                await message.reply_text(f'''شما بردیدبرای شما یک امتیاز اضافه شد
                انتخاب سیتم :{system_choice}
                امیتاز سیستم:{systm}
                امتیازشما:{user}''')
            else :
                systm += 1
                await message.reply_text(f'''شما باختیدبرای سیستم یک امتیاز اضافه شد
                انتخاب سیتم :{system_choice}
                امیتاز سیستم:{systm}
                امتیازشما:{user}''')
            #Check the end of the game
            if systm == 3 or user == 3 :
                break
            else:
                #Waiting for the user to send a message
                response = await app.listen(message.chat.id)  
                if response.text == 'خروج از بازی':
                    return 'خروج از بازی'
                elif not(response.text in ['سنگ 🪨', 'کاغذ 📄', 'قیچی ✂️']) :
                    await message.reply_text('به صورت اتوماتیک از بازی خارج شدید گزینه مورد نظر خود را دوباره وارد کنید')
                    return 'خروج از بازی'
                system_choice = self.system.choose_option() #new system selection
                result = self.determine_winner(response.text, system_choice) # new user selection
        # Update the results in the database
        if systm == user:
            db_manager.update_results(message.chat.id, 'equal')
            await message.reply_text('تبریک مگم سیستم به شما  زورش نرسید مساوی شدین')
        elif user == 3 :
            db_manager.update_results(message.chat.id, 'winner')
            result_game =   user - systm
            await message.reply_text(f' بازی تمام شد    {result_game}:با اختلاف امتیاز \nنتیجه بازی: شما بردید')
        elif systm == 3 :
            db_manager.update_results(message.chat.id, 'lost')
            result_game = systm - user
            await message.reply_text(f' بازی تمام شد  {result_game}_:با اختلاف امتیاز \nنتیجه بازی: شما باختید ')
        
    #Determining the winner between the system and the user
    def determine_winner(self, user_choice, system_choice):
        if user_choice  == system_choice :
            return 'مساوی'
        elif ((user_choice == 'کاغذ 📄') and   (system_choice == 'سنگ 🪨')) or ((user_choice == 'سنگ 🪨') and (system_choice == 'قیچی ✂️' ) ) or ((user_choice == 'قیچی ✂️') and (system_choice == 'کاغذ 📄')):
            return 'شما بردید'
        else :
            return 'شما باختید سیستم برنده شد'








@app.on_message(filters.text)
async def on_user_choice(client, message):
    # Check if the user's message is one of the valid options
    if message.text in ['سنگ 🪨', 'کاغذ 📄', 'قیچی ✂️']:  
       # z = Calling out of the game in the middle of the game 
       # Send the option in the middle of the loop(while True)
       z = await Game().handle_user_choice(message, message.text)

    else :
        # If the user's message is one of the valid options, the appropriate response will be sent
        await message.reply_text('چرا چرت پرت میگی چیزی بگو بفهمم از دکمه ها و کامند ها استفاده کن')
    try:# Remove unnecessary errors
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
        pass


# raun libray pyrogram
app.run()
    
        



