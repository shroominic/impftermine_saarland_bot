import impftermine_bot as ibot

email = None

bot = ibot.ImpfterminBot(email)
try:
    bot.init_chrome(chromedriver_path='./chromedriver')
except Exception as e:
    print(e)

bot.open_target_page()
bot.login()
bot.go_to_booking()

bot.try_booking()





