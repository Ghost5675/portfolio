from enum import Enum
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.sync import TelegramClient

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import os


CONFIG = {
    "MAX_LEN_STATUS": 70,
    "CHESS_PROFILE": "link_to_your_chess.com_rofile",
    "KZ_LEADERBOARD": "https://www.chess.com/leaderboard/live/rapid?country=KZ",
    "MAIN_TR_CLASS": "leaderboard-row-show-on-hover",
    "RANK_CLASS": "leaderboard-row-rank",
    "RATING_CLASS": "leaderboard-table-text-right",
    "NAME": "your_profile_name_on_chess.com",
    "FIND_NAME_CLASS": "user-tagline-username",
    "BUTTON_ARIA_LABEL": "Next Page",
    "FLAG": True,
    "FLAG_CLOSE": True,
    "BUTTON_CLOSE": "Close",
    "API_ID": "your_api_id",
    "API_HASH": 'your_api_hash',
    "PHONE": 'your_phone',
}

rating = 0
rank = 0

def change_bio(BIO_TEXT, client):
    try:
        client(UpdateProfileRequest(about=BIO_TEXT))
        return f"Био изменено на: {BIO_TEXT}"
    except Exception as e:
        return f"Ошибка при изменении био: {e}"
    
def get_rank_rating():
    
    driver = webdriver.Chrome()
    driver.get(CONFIG["KZ_LEADERBOARD"])
    while CONFIG["FLAG"]:
        WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.CLASS_NAME, CONFIG["MAIN_TR_CLASS"]))
        )

        players = driver.find_elements(By.CLASS_NAME, CONFIG["MAIN_TR_CLASS"])

        for item in players:
            if CONFIG["NAME"] in item.text:
                rank = int(
                    item.find_element(By.CLASS_NAME, CONFIG["RANK_CLASS"]).text.replace(
                        "#", ""
                    )
                )
                rating = item.find_element(
                    By.XPATH, f".//td[contains(@class, '{CONFIG['RATING_CLASS']}')][2]"
                ).text
                print("success", rank, rating)
                print(len(f"{CONFIG["CHESS_PROFILE"]} rank in KZ:{rank}, rating:{rating}"))
                print(f"{CONFIG["CHESS_PROFILE"]}, rank in KZ:{rank}, rating:{rating}")
                CONFIG["FLAG"] = False
                return f"{CONFIG["CHESS_PROFILE"]}, rank in KZ:{rank}, rating:{rating}"

        if CONFIG["FLAG_CLOSE"] and WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, f"button[aria-label='{CONFIG['BUTTON_CLOSE']}']")
            )
        ):
            btn_close = driver.find_element(
                By.CSS_SELECTOR, f"button[aria-label='{CONFIG['BUTTON_CLOSE']}']"
            )
            btn_close.click()
            CONFIG["FLAG_CLOSE"] = False

        driver.implicitly_wait(1)

        btn = driver.find_element(
            By.CSS_SELECTOR, f"button[aria-label='{CONFIG['BUTTON_ARIA_LABEL']}']"
        )
        btn.click()

    driver.close()




with TelegramClient('chess_parser_1', api_id=CONFIG["API_ID"], api_hash=CONFIG["API_HASH"]) as client:
    profile_info = get_rank_rating()
    client.sign_in(phone=CONFIG["PHONE"])
    client.start(phone=CONFIG["PHONE"])
    
    change_bio(profile_info, client)
    