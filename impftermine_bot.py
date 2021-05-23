from bs4 import BeautifulSoup as BS
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import random
import time


def xpath_soup(soup_element):
    components = []
    child = soup_element if soup_element.name else soup_element.parent
    for parent in child.parents:
        siblings = parent.find_all(child.name, recursive=False)
        components.append(
            child.name
            if siblings == [child] else
            '%s[%d]' % (child.name, 1 + siblings.index(child))
        )
        child = parent
    components.reverse()
    return '/%s' % '/'.join(components)


def click_button(web_driver, text_de, text_en=None):
    btn_element = None
    if text_en is not None:
        for btn in soup.find_all('button'):
            if text_de or text_en in str(btn):
                btn_element = btn
    else:
        for btn in soup.find_all('button'):
            if text_de in str(btn):
                btn_element = btn

    web_driver.find_element_by_xpath(xpath_soup(btn_element)).click()


def click_time_selector(web_driver):
    div = soup.find_all('div')
    selector_element = []
    for time_S in div:
        if 'SelectList' in str(time_S):
            if 'LanguageSelector' and 'flex-layout' not in str(time_S):
                selector_element.append(time_S)
    print(selector_element)
    random_element = random.choice(selector_element)
    web_driver.find_element_by_xpath(xpath_soup(random_element)).click()


def page_contains_string(text):
    for t in soup.find_all(["h1", "h2", "h3", "h4", "p"]):
        if text in str(t):
            return True
    return False


chrome_options = Options()
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--window-size=720,1080")
driver = webdriver.Chrome(executable_path='/Users/drminic/Development/sdk/chromedriver', options=chrome_options)

url = 'https://www.impfen-saarland.de/service/login'
email = None

driver.get(url)
time.sleep(0.2)

#################
# Login Process #
#################

# Email Input
soup = BS(driver.page_source, 'lxml')

click_button(driver, 'DE')

input_element = None
for i in soup.find_all('input'):
    if 'name="email"' in str(i):
        input_element = i

if email is None:
    email = input('Email: ')

form_element = driver.find_element_by_xpath(xpath_soup(input_element))
form_element.send_keys(email)
form_element.submit()

# Session Toke Input
code_is_valid = False
while not code_is_valid:
    soup = BS(driver.page_source, 'lxml')

    if page_contains_string('Der eingegebene Code ist nicht gültig'):
        print('Code not valid, try again.\n')

    input_element = None
    for i in soup.find_all('input'):
        if '"session[token]"' in str(i):
            input_element = i

    if input_element is not None:
        session_token = input('Code: ')

        form_element = driver.find_element_by_xpath(xpath_soup(input_element))
        form_element.send_keys(session_token)
        form_element.submit()
    else:
        code_is_valid = True


# Choose Booking
soup = BS(driver.page_source, 'lxml')
click_button(driver, 'Buchung', 'Booking')

######################
# Booking Automation #
######################

vaccination_appointment_is_booked = False
vaccination_appointment_is_bookable = False

while not vaccination_appointment_is_booked:
    while not vaccination_appointment_is_bookable:

        time.sleep(0.1)
        soup = BS(driver.page_source, 'lxml')

        impfzentrum = ['Saarbrücken', 'Saarlouis', 'Neunkirchen', 'Lebach'] #, 'Nacht-Termine']
        choice = random.choice(impfzentrum)
        print(choice)
        try:
            click_button(driver, choice)
            click_button(driver, 'Weiter')
        except:
            print('To Fast lel')

        time.sleep(0.2)
        soup = BS(driver.page_source, 'lxml')

        if page_contains_string('Aktuell sind alle Impftermine belegt.'):
            click_button(driver, 'PrimaryButton')
        elif page_contains_string('gewünschten Impftermine'):
            vaccination_appointment_is_bookable = True
            print('-------termin gefunden--------')

    click_time_selector(driver)
    click_button(driver, 'Weiter')

    if page_contains_string('Impftermine bestätigen'):
        vaccination_appointment_is_booked = True
        print('Booking successful!')
    elif page_contains_string('Aktuell sind alle Impftermine belegt.'):
        continue
    else:
        print('Error')
        break

