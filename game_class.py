from pyrogram.types import (ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton)
from pyromod import listen
import random


#game class system 
class System:
    def choose_option(self):
        return random.choice(['سنگ 🪨', 'کاغذ 📄', 'قیچی ✂️'])#using of library random


#Waiting for the robot to answer the user
class Response:
    async def respons_txt(self,app, chat_id):
        return await app.listen(chat_id)  



#General game class
class Game:
    def __init__(self,app, db_manager):
        self.system =System()# input random system
        self.response = Response()
        self.app = app
        self.db_manager = db_manager
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
                response = await self.response.respons_txt(self.app, message.chat.id)
                print(response.text)
                if response.text == 'خروج از بازی':
                    return 'خروج از بازی'
                elif not(response.text in ['سنگ 🪨', 'کاغذ 📄', 'قیچی ✂️']) :
                    await message.reply_text('به صورت اتوماتیک از بازی خارج شدید گزینه مورد نظر خود را دوباره وارد کنید')
                    return 'خروج از بازی'
                system_choice = self.system.choose_option() #new system selection
                result = self.determine_winner(response.text, system_choice) # new user selection
        # Update the results in the database
        try:
            if systm == user:
                self.db_manager.update_results(message.chat.id, 'equal')
                await message.reply_text('تبریک مگم سیستم به شما  زورش نرسید مساوی شدین')
            elif user == 3 :
                self.db_manager.update_results(message.chat.id, 'winner')
                result_game =   user - systm
                await message.reply_text(f' بازی تمام شد    {result_game}:با اختلاف امتیاز \nنتیجه بازی: شما بردید')
            elif systm == 3 :
                self.db_manager.update_results(message.chat.id, 'lost')
                result_game = systm - user
                await message.reply_text(f' بازی تمام شد  {result_game}_:با اختلاف امتیاز \nنتیجه بازی: شما باختید ')
        finally:
            pass
    #Determining the winner between the system and the user
    def determine_winner(self, user_choice, system_choice):
        if user_choice  == system_choice :
            return 'مساوی'
        elif ((user_choice == 'کاغذ 📄') and   (system_choice == 'سنگ 🪨')) or ((user_choice == 'سنگ 🪨') and (system_choice == 'قیچی ✂️' ) ) or ((user_choice == 'قیچی ✂️') and (system_choice == 'کاغذ 📄')):
            return 'شما بردید'
        else :
            return 'شما باختید سیستم برنده شد'

