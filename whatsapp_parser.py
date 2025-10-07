from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from contextlib import contextmanager
import pandas as pd
import time
from pathlib import Path

CONFIG = {
    "timeouts": {"QR_timeout": 1000, "wait": 5},
    "selectors": {
        "qr_code": "div.x1c4vz4f.xs83m0k.xdl72j9.x1g77sc7.xeuugli.x2lwn1j.xozqiw3",
        "load_screen": "div.x1c3i2sq.x14ug900.xk82a7y.x1sy10c2",
        "new_chat_xpath": "//span[@data-icon='new-chat-outline']",
        "new_contact_xpath": "//div[@aria-label='Новый контакт' or @aria-label='New contact']",
        "name_input_css": "div[contenteditable='true']",
        "phone_input_xpath": "//input[@aria-label='Номер телефона' or @aria-label='Phone number']",
        "sync_checkbox_xpath": "//input[@aria-label='Синхронизировать контакт на телефоне' or @aria-label='Sync contact to phone']",
        "save_button_xpath": "//div[@aria-label='Сохранить контакт' or @aria-label='Save contact']",
        "back_button_xpath": "//span[@data-icon='back-refreshed']",
        "duplicate_message_xpath": "//div[contains(text(), 'Этот номер телефона уже есть в вашем списке контактов.') or contains(text(), 'This phone number is already in your contacts.')]",
        "not_whatsapp_phone": "contact-phone-number-fields-error",
    },
}


class WhatsappParser:
    def __init__(self, driver, name: str, phone: str):
        self.driver = driver
        self.name = name
        self.phone = phone

    def wait_for_element_invincible(
        self, by, value, timeout=CONFIG["timeouts"]["wait"]
    ):
        return WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located((by, value))
        )

    def wait_for_element(self, by, value, timeout=CONFIG["timeouts"]["wait"]):
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )

    def new_chat(self):
        print("Clicking new chat button")
        self.wait_for_element(By.XPATH, CONFIG["selectors"]["new_chat_xpath"]).click()

    def new_contact_button(self):
        print("Clicking new contact button")
        self.wait_for_element(
            By.XPATH, CONFIG["selectors"]["new_contact_xpath"]
        ).click()

    def input_name(self):
        print(f"Entering name: {self.name}")
        name_input = self.wait_for_element(
            By.CSS_SELECTOR, CONFIG["selectors"]["name_input_css"]
        )
        name_input.click()
        name_input.send_keys(self.name)

    def input_phone(self):
        print(f"Entering phone: {self.phone}")
        phone_input = self.wait_for_element(
            By.XPATH, CONFIG["selectors"]["phone_input_xpath"]
        )
        phone_input.send_keys(self.phone)

    def sync_checkbox(self):
        print("Checking sync checkbox")
        sync_checkbox = self.wait_for_element(
            By.XPATH, CONFIG["selectors"]["sync_checkbox_xpath"]
        )
        if sync_checkbox.get_attribute("aria-checked") == "false":
            print("Clicking sync checkbox")
            sync_checkbox.click()

    def exist_checking(self):
        try:
            print("Checking if phone number already exists")
            WebDriverWait(self.driver, 1).until(
                EC.presence_of_element_located(
                    (By.XPATH, CONFIG["selectors"]["duplicate_message_xpath"])
                )
            )
            print(f"Phone number {self.phone} already exists")
            self.wait_for_element(
                By.XPATH, CONFIG["selectors"]["back_button_xpath"]
            ).click()
            self.wait_for_element(
                By.XPATH, CONFIG["selectors"]["back_button_xpath"]
            ).click()
            return 0
        except TimeoutException:
            print(
                f"Phone number {self.phone} not found in contacts, proceeding to save"
            )
            self.wait_for_element(
                By.XPATH, CONFIG["selectors"]["save_button_xpath"]
            ).click()

            self.wait_for_element_invincible(
                By.XPATH, CONFIG["selectors"]["save_button_xpath"]
            )

            print(f"Contact {self.name} with phone {self.phone} saved successfully")
            return 1

    def create_contact(self):
        print(f"Starting contact creation for name: {self.name}, phone: {self.phone}")
        try:
            self.new_chat()
            self.new_contact_button()
            self.input_name()
            self.input_phone()
            self.sync_checkbox()
            return self.exist_checking()
        except TimeoutException as e:
            print(f"Timeout during contact creation for {self.name}: {str(e)}")
            self.recover_from_error()
            return 0
        except WebDriverException as e:
            print(f"WebDriver error for {self.name}: {str(e)}")
            self.recover_from_error()
            return 0

    def recover_from_error(self):
        print("Recovering from error by reloading WhatsApp")
        self.driver.get("https://web.whatsapp.com")
        wait_load_screen(
            self.driver,
            by=By.CSS_SELECTOR,
            value=CONFIG["selectors"]["load_screen"],
        )


def validate_file_path(path: str) -> Path:
    while True:
        if not path:
            print("The file path cannot be empty.")
            path = input("Enter the path to the Excel file:\n").strip()
            continue
        file_path = Path(path)
        if file_path.exists() and file_path.is_file() and file_path.suffix == ".xlsx":
            return file_path
        print(
            "Invalid file path! Ensure the file exists and has a .xlsx extension."
        )
        path = input("Enter the path to the Excel file:\n").strip()


def load_excel(file_path: str):
    df = pd.read_excel(file_path)
    columns = df.columns.tolist()
    print(f"Available columns: {columns}")

    def get_valid_column(prompt, optional=False):
        while True:
            value = input(prompt).strip() or None
            if optional and (value == "0" or value is None):
                return None
            if value in columns:
                return value
            print(
                f"Invalid column! Choose from {columns}"
                + (" or '0' to skip." if optional else ".")
            )

    student_name = get_valid_column("Enter the name of the column with the student's name\n")
    student_phone = get_valid_column("Enter the name of the column with the student's phone\n")
    parent_phone = get_valid_column(
        "Enter the name of the column with the parent's phone (0=skip):\n", optional=True
    )
    return df, student_name, student_phone, parent_phone


@contextmanager
def whatsapp_driver():
    driver = webdriver.Chrome()
    try:
        yield driver
    finally:
        print("Closing WebDriver")
        driver.quit()


def normalize_phone(phone):
    phone = str(phone).strip()
    if not phone:
        raise ValueError("The phone number cannot be empty")
    phone = phone.replace(" ", "").replace(".0", "")
    if phone.startswith("8"):
        phone = phone[1:]
    elif phone.startswith("+7"):
        phone = phone[2:]
    if not phone.isdigit() or len(phone) < 10:
        raise ValueError(f"Invalid phone number: {phone}")
    return phone


def wait_load_screen(driver, by, value, timeout=CONFIG["timeouts"]["QR_timeout"]):
    try:
        WebDriverWait(driver, timeout).until(
            EC.invisibility_of_element_located((by, value))
        )
        print("Pass the load screen")
    except TimeoutException:
        print("Timeout: loading screen")


def wait_qr(driver, by, value, timeout=CONFIG["timeouts"]["QR_timeout"]):
    try:
        print("wait qr code")
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        print("find qr code")
        WebDriverWait(driver, timeout).until(
            EC.invisibility_of_element_located((by, value))
        )
        print("Pass the qr code")
        wait_load_screen(driver, by, value=CONFIG["selectors"]["load_screen"])
    except TimeoutException:
        print("Timeout: QR code did not disappear")


def first_enter(driver, timeout=CONFIG["timeouts"]["wait"]):
    print("first enter")
    time.sleep(2)
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, CONFIG["selectors"]["new_chat_xpath"]))
    ).click()
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, CONFIG["selectors"]["back_button_xpath"]))
    ).click()
    time.sleep(2)


def main():
    path = input("Enter the path to the Excel file:\n").strip()
    df, student_name, student_phone, parent_phone = load_excel(
        file_path=validate_file_path(path)
    )

    with whatsapp_driver() as driver:
        driver.get("https://web.whatsapp.com")
        wait_qr(driver, by=By.CSS_SELECTOR, value=CONFIG["selectors"]["qr_code"])
        first_enter(driver)

        for index, row in df.iterrows():
            try:
                print(f"row: {index+1}, process: {row[student_name]}")
                if pd.isna(row[student_name]) or pd.isna(row[student_phone]):
                    print(f"Skipping row {index+1}: Missing student name or phone")
                    continue
                student_whatsapp_parser = WhatsappParser(
                    driver=driver,
                    name=row[student_name].strip(),
                    phone=normalize_phone(str(row[student_phone])),
                )
                student_whatsapp_parser.create_contact()
                if parent_phone:
                    if pd.isna(row[parent_phone]):
                        print(f"Skipping row {index+1}: Missing parent phone")
                        continue
                    parent_whatsapp_parser = WhatsappParser(
                        driver=driver,
                        name=f"Parent {row[student_name]}",
                        phone=normalize_phone(str(row[parent_phone])),
                    )
                    parent_whatsapp_parser.create_contact()
            except (TypeError, ValueError) as e:
                print(e)
                continue
        print("End parser")


if __name__ == "__main__":
    main()