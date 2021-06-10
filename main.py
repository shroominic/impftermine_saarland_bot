import impftermine_bot as ibot

# Insert email for automatic login
if 'N' in input('Use Email? (N) '):
    email = None
else:
    email = input('Email: ')

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
input('Press ENTER to start ... ')
bot.go_to_booking()

# Booking Automation
bot.try_booking()
