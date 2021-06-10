import os
import random
import time

from bs4 import BeautifulSoup as BS
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# URL's
url = 'https://www.impfen-saarland.de/'
login_url = f'{url}service/login'


# Static Functions
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


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


# Impftermin Bot Class
class ImpfterminBot:

    # Initialisation
    def __init__(self, impfzentren, email=None):
        self.email = email
        self.impfzentren = impfzentren

        if self.email is None:
            self.anonymous = True
        else:
            self.anonymous = False

        self.driver = None
        self.soup = None

        self.attempts = 0

    def init_chrome(self, chromedriver_path):
        chrome_options = Options()
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--window-size=720,1080")
        self.driver = webdriver.Chrome(
            executable_path=chromedriver_path,
            options=chrome_options)

    # Utility Methods
    def refresh_soup(self):
        self.soup = BS(self.driver.page_source, 'lxml')

    def click_button(self, text):
        btn_element = None

        for btn in self.soup.find_all('button'):
            if text in str(btn):
                btn_element = btn
        try:
            xpath = xpath_soup(btn_element)
            self.driver.find_element_by_xpath(xpath).click()
        except Exception as e:
            print(e)

    def click_time_selector(self):
        div = self.soup.find_all('div')
        selector_element = []
        for time_S in div:
            if 'SelectList' in str(time_S):
                if 'LanguageSelector' and 'flex-layout' not in str(time_S):
                    selector_element.append(time_S)
        random_element = random.choice(selector_element)
        self.driver.find_element_by_xpath(xpath_soup(random_element)).click()

    def page_contains_string(self, text):
        for t in self.soup.find_all(["h1", "h2", "h3", "h4", "p"]):
            if text in str(t):
                return True
        return False

    # Scripting Methods
    def open_target_page(self):
        if self.anonymous:
            self.driver.get(url)
        else:
            self.driver.get(login_url)
        time.sleep(1)
        self.refresh_soup()

    def login(self):
        if not self.anonymous:
            self.refresh_soup()

            # Email Input
            input_element = None
            for i in self.soup.find_all('input'):
                if 'name="email"' in str(i):
                    input_element = i

            form_element = self.driver.find_element_by_xpath(xpath_soup(input_element))
            form_element.send_keys(self.email)
            form_element.submit()

            # Session Toke Input
            code_is_valid = False
            while not code_is_valid:
                self.refresh_soup()

                if self.page_contains_string('Der eingegebene Code ist nicht gültig'):
                    print('Code not valid, try again.\n')

                input_element = None
                for i in self.soup.find_all('input'):
                    if '"session[token]"' in str(i):
                        input_element = i

                if input_element is not None:
                    session_token = input('Code: ')

                    form_element = self.driver.find_element_by_xpath(xpath_soup(input_element))
                    form_element.send_keys(session_token)
                    form_element.submit()
                else:
                    code_is_valid = True

            time.sleep(2)

    def go_to_booking(self):
        # Change Language
        self.click_button('DE')
        time.sleep(1)

        self.refresh_soup()
        self.click_button('Buchung')
        time.sleep(1)

    def try_booking(self):
        vaccination_appointment_is_bookable = False
        while not vaccination_appointment_is_bookable:

            self.refresh_soup()
            self.attempts += 1

            choice = random.choice(self.impfzentren)
            clear()
            print(f'{self.attempts} - {choice}')
            try:
                self.click_button(choice)
                self.click_button('Weiter')

            except Exception as e:
                print(e)

            time.sleep(.25)
            self.refresh_soup()

            if self.page_contains_string('Aktuell sind alle Impftermine belegt.'):
                self.click_button('PrimaryButton')
                time.sleep(.1)

            elif self.page_contains_string('gewünschten Impftermine'):
                clear()
                print('- - - - Appointment found - - - -')
                self.click_time_selector()
                self.click_button('Weiter')
                print(f'Attempt: {self.attempts}')
                print(f'Location: {choice} \n')

                time.sleep(1)
                self.refresh_soup()
                if self.page_contains_string('verbindlichen Buchung'):
                    try:
                        self.click_button('Termine buchen')
                    except Exception as e:
                        print(e)

                if 'q' in input('Type "q" to quit: '):
                    vaccination_appointment_is_bookable = True

            else:
                clear()
                print("\nLoading ... ")
                time.sleep(3)
                self.refresh_soup()
                self.click_button('PrimaryButton')
                time.sleep(.15)

        self.driver.quit()


