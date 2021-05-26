import impftermine_bot as ibot

# Insert email for automatic login
email = None

impfzentren = ['Saarbrücken',
               'Saarlouis',
               'Neunkirchen',
               'Lebach',
               'Nacht-Termine']

bot = ibot.ImpfterminBot(impfzentren, email)

# Download: https://chromedriver.chromium.org/
bot.init_chrome(chromedriver_path='./chromedriver')

# Scripted Page Navigation
bot.open_target_page()
bot.login()
# input('Select Person: ')
bot.go_to_booking()

# Booking Automation
bot.try_booking()
