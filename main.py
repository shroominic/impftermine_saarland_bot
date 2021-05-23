import impftermine_bot as ibot

# Insert email for automatic login
email = None

bot = ibot.ImpfterminBot(email)

# Download: https://chromedriver.chromium.org/
bot.init_chrome(chromedriver_path='./chromedriver')

bot.open_target_page()
bot.login()
bot.go_to_booking()

bot.try_booking()





