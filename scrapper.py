import os
import time
import requests
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

load_dotenv()

login = os.getenv('LOGIN_PINTEREST')
pswd = os.getenv('PSWD_PINTEREST')

# setting up the driver
driver = webdriver.Chrome(service=ChromeService(executable_path=ChromeDriverManager().install()))

# going to login webpage
driver.get("https://www.pinterest.fr/login/")

# LOGIN
login_box = driver.find_element(by=By.ID, value="email")  # finding email field
pswd_box = driver.find_element(by=By.ID, value="password")  # finding pswd field

login_box.send_keys(login)  # writing email
pswd_box.send_keys(pswd)  # writing email

login_button = driver.find_element(by=By.CSS_SELECTOR, value=".SignupButton")  # finding login button
login_button.click()  # clicking on it

# waiting for login to happend
WebDriverWait(driver, timeout=5).until(lambda d: d.find_element(by=By.PARTIAL_LINK_TEXT, value="Accueil"))

# SCRAPING
driver.get("https://www.pinterest.fr/hervineart/bamboozle/")  # getting to the right board

n_pin = int(WebDriverWait(driver, timeout=5).until(
    lambda d: d.find_element(by=By.XPATH, value='/html/body/div[1]/div[1]/div[2]/div/div/div/div[3]/div[1]/h2')).text[
            :2])
board_name = driver.find_element(by=By.XPATH,
                                 value='//*[@id=\"__PWS_ROOT__\"]/div[1]/div[2]/div/div/div/div[1]/div/div/div/div[2]/h1').text

images_source = []
images_link = []
scrap_pin = 0
abort_count = 0

while scrap_pin < n_pin - 1:
    # get the displayed pin
    time.sleep(1)
    images_scrap = driver.find_elements(by=By.XPATH,
                                        value='/html/body/div[1]/div[1]/div[2]/div/div/div/div[4]/div[2]/div/div[1]/div/div/div[1]/div/div/div/div/div/div/div/div/div/div/div[1]/a/div/div[1]/div/div/div/div/div/img')
    # get the scr from those pin
    images_scrap_link = [pin.get_attribute('src') for pin in images_scrap]

    # add only the new link in the final list
    for link in images_scrap_link:
        if link not in images_link:
            images_link.append(link)

    # from the last scraped image
    last_image = images_scrap[-1]
    scroll_origin = ScrollOrigin.from_element(last_image)  # from its position
    # scroll !
    ActionChains(driver) \
        .scroll_from_origin(scroll_origin, 0, 500) \
        .perform()

    # verify the number of scraped pin
    if scrap_pin == len(images_link):
        abort_count += 1
        if abort_count == 3:
            break
    scrap_pin = len(images_link)
    print(scrap_pin)

os.makedirs(board_name, exist_ok=True)

for image in images_link:
    image = image.replace('236x', 'originals')
    file = requests.get(image).content
    with open(f'{board_name}/{image[-30:]}', 'wb') as handler:
        handler.write(file)

driver.quit()
