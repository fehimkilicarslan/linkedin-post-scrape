# selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
# time
from datetime import datetime, timedelta
from time import sleep
# bs4
from bs4 import BeautifulSoup

# local variables
loginURL = 'https://www.linkedin.com'
username = 'your_email_adress'  # your email adress
password = 'your_password'  # your password
current_date = datetime.utcnow()
keywords = [
    "microsoft",
    "bill gates",
    "elon musk",
]

# selenium setup
driver = webdriver.Firefox()


def login(username, password):
    """login to linkedin account"""

    username_input = driver.find_element(
        "xpath", "//input[@name='session_key']")
    password_input = driver.find_element(
        "xpath", "//input[@name='session_password']")
    login_button = driver.find_element("xpath", "//button[@type='submit']")

    username_input.send_keys(username)
    password_input.send_keys(password)
    login_button.click()
    for keyword in keywords:
        sleep(1)
        print(f'\n\n\nnow working for: {keyword}\n\n\n')
        searchFromKeyword(keyword)


def searchFromKeyword(keyword):
    """Search posts with specific keywords"""

    data = []
    driver.get(
        f'https://www.linkedin.com/search/results/content/?datePosted="past-24h"&keywords={keyword}&origin=FACETED_SEARCH&sortBy="date_posted"')

    initial_post_count = len(driver.find_elements(By.TAG_NAME, 'li'))

    while True:
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        sleep(2)

        current_post_count = len(driver.find_elements(By.TAG_NAME, 'li'))

        if current_post_count == initial_post_count:
            break

        initial_post_count = current_post_count

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    if soup:
        main = soup.find('main', {'class': 'scaffold-layout__main'})
        if main:
            postAreaList = main.find_all(
                'ul', class_='reusable-search__entity-result-list list-style-none')
            if postAreaList:
                for postList in postAreaList:
                    posts = postList.find_all('li', class_=False)
                    if posts:
                        for post in posts:
                            usernameObj = post.find('span', {'dir': 'ltr'})
                            userUrlObj = post.find(
                                'a', {'class': 'app-aware-link update-components-actor__image relative'})
                            linkObj = post.find(
                                'div', class_='feed-shared-update-v2')
                            dateArea = post.find(
                                'div', class_='update-components-text-view break-words')
                            valueArea = post.find(
                                'div', class_='update-components-update-v2__commentary')
                            if valueArea:
                                valueObj = valueArea.find(
                                    'span', {'dir': 'ltr'})
                                if valueObj:
                                    if valueObj.text:
                                        content = valueObj.text
                                        postedAt = datetime.now()
                                        if dateArea:
                                            try:
                                                dateObj = dateArea.find(
                                                    'span', class_='visually-hidden')
                                                if dateObj:
                                                    timeData = dateObj.text.lower().replace(" ", '').replace(
                                                        "•", '').replace('edited', '').replace('düzenlendi', '').replace('\n', '')
                                                    if 'm' in timeData and 'o' not in timeData:
                                                        timeData = timeData[:-1]
                                                        postedAt = datetime.now() - timedelta(minutes=int(timeData))
                                                    elif 'h' in timeData:
                                                        timeData = timeData[:-1]
                                                        postedAt = datetime.now() - timedelta(hours=int(timeData))
                                                    elif 'd' in timeData:
                                                        timeData = timeData[:-1]
                                                        postedAt = datetime.now() - timedelta(days=int(timeData))
                                            except:
                                                pass
                                        if dateComparison(postedAt):
                                            pass
                                        else:
                                            if usernameObj and userUrlObj:
                                                if linkObj:
                                                    data_urn_value = linkObj.get(
                                                        'data-urn')
                                                    if data_urn_value:
                                                        data.append({
                                                            "author": {
                                                                "username": str(usernameObj.text),
                                                                "link": str(userUrlObj.get('href')),
                                                            },
                                                            "post": {
                                                                "suid": f'Linkedin_{str(data_urn_value.split("activity:")[1])}',
                                                                "posted_at": str(postedAt),
                                                                "content": content,
                                                                "link": f"https://www.linkedin.com/feed/update/{data_urn_value}",
                                                            }
                                                        })
    print(data)


def dateComparison(date_str):
    last_week = current_date - timedelta(days=1)
    return date_str < last_week  # == true ? break : false continue


if __name__ == "__main__":
    try:
        driver.get(loginURL)
        login(username, password)
    except Exception as err:
        print(err)
    finally:
        driver.quit()
