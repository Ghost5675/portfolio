from enum import Enum
from typing import Dict, List, Optional, Tuple
import time
import re
import logging
import random
import pandas as pd
from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from contextlib import contextmanager
import os

import urllib


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("scraper.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

CONFIG = {
    "BASE_URLS": {
        ("sell", "1"): "https://krisha.kz/prodazha/kvartiry/?",
        ("sell", "59"): "https://krisha.kz/prodazha/kommercheskaya-nedvizhimost/?",
        ("rent", "1"): "https://krisha.kz/arenda/kvartiry/?rent-period-switch=%2Farenda%2Fkvartiry&",
        ("rent", "59"): "https://krisha.kz/arenda/kommercheskaya-nedvizhimost/?das[rent.square]=2&",
    },
    "OUTPUT_ENCODING": "utf-16",
    "OUTPUT_SEPARATOR": "[",
    "MAX_PAGES": 1000,
    "SITE_URL": "https://krisha.kz/",
    "TIMEOUT": 0.5,
    "AVG_NUM_OF_ADS": 20
}

XPATHS = {
    "OFFER_TITLE": "//div[@class='offer__advert-title']/h1",
    "LIVE_SQUARE": "//div[@data-name='live.square']",
    "COM_SQUARE": "//div[@data-name='com.square']",
    "FLAT_FLOOR": "//div[@data-name='flat.floor']/div[@class='offer__advert-short-info']",
    "HOUSE_FLOOR_NUM": "//div[@data-name='house.floor_num']/div[@class='offer__advert-short-info']",
    "LOCATION": "//div[contains(@class, 'offer__location') and contains(@class, 'offer__advert-short-info')]/span",
    "ADDRESS": "//div[@data-name='map.street']/div[@class='offer__advert-short-info']",
    "RESIDENTIAL_COMPLEX": "//div[@data-name='map.complex']/div[@class='offer__advert-short-info']",
    "BUILDING_TYPE": "//div[@data-name='flat.building']/div[@class='offer__advert-short-info']",
    "HOUSE_YEAR": "//div[@data-name='house.year']/div[@class='offer__advert-short-info']",
    "RENOVATION": "//div[@data-name='flat.renovation']/div[@class='offer__advert-short-info']",
    "RENT_RENOVATION": "//div[@data-name='flat.rent_renovation']/div[@class='offer__advert-short-info']",
    "CEILING": [
        "//dt[@data-name='ceiling']/following-sibling::dd",
        "//div[@data-name='ceiling']/div[@class='offer__advert-short-info']",
    ],
    "TOILET": [
        "//dt[@data-name='separated_toilet']/following-sibling::dd",
        "//dt[@data-name='flat.toilet']/following-sibling::dd",
        "//div[@data-name='separated_toilet']/div[@class='offer__advert-short-info']",
        "//div[@data-name='flat.toilet']/div[@class='offer__advert-short-info']"
    ],
    "SELLER": [
        "//div[contains(@class, 'label') and contains(@class, 'label--default') and contains(@class, 'label-user-agent')]",
        "//div[contains(@class, 'label') and contains(@class, 'label--transparent') and contains(@class, 'label-user-identified-specialist')]",
        "//div[contains(@class, 'owners__name') and contains(@class, 'owners__name--large')]",
        "//div[@class='owners__labels-list']",
    ],
    "PRICE": [
        "//div[@class='offer__price']",
        "//p[contains(@class, 'offer__price') and contains(@class, 'offer__price--full')]",
        "//p[@class='offer__price  ']"
    ],
    "COM_PRICE": [
        "//div[@class='offer__price']/span[@class='offer__price-part'][1]",
        "//p[contains(@class, 'offer__price') and contains(@class, 'offer__price--full')]",
    ],
    "COM_LOCATION": "//div[@data-name='com.location']/div[@class='offer__advert-short-info']",
    "COMPLEX_NAME": "//div[@data-name='office.complex_name']/div[@class='offer__advert-short-info']",
    "COM_RENOVATION": [
        "//dt[@data-name='com.renovation']/following-sibling::dd",
        "//div[@data-name='com.renovation']/div[@class='offer__advert-short-info']",
    ],
    "OPERATING_BUSINESS": [
        "//dt[@data-name='estate.is_buss']/following-sibling::dd",
        "//div[@data-name='religious.is_buss']/div[@class='offer__advert-short-info']",
    ],
    "COMMUNICATIONS": [
        "//dt[@data-name='com.communications']/following-sibling::dd",
        "//div[@data-name='com.communications']/div[@class='offer__advert-short-info']",
    ],
    "LOCATION_LINE": [
        "//dt[@data-name='com.location_line']/following-sibling::dd",
        "//div[@data-name='com.location_line']/div[@class='offer__advert-short-info']",
    ],
    "SECURITY": [
        "//dt[@data-name='com.security']/following-sibling::dd",
        "//div[@data-name='com.security']/div[@class='offer__advert-short-info']",
    ],
    "CUSTOM_LAYOUT": "//dt[@data-name='com.custom_layout']/following-sibling::dd",
    "ENTRANCE": "//dt[@data-name='com.entrance_opts']/following-sibling::dd",
    "PARKING": [
        "//dt[@data-name='com.parking_opts']/following-sibling::dd",
        "//div[@data-name='com.parking_opts']//div[@class='offer__advert-short-info']",
    ],
    "ALLOCATED_POWER": [
        "//dt[@data-name='indust.max_electr']/following-sibling::dd",
        "//div[@data-name='indust.max_electr']/div[@class='offer__advert-short-info']",
    ],
    "SEARCH_BUTTON": "//button[contains(text(), 'Найти')]",
    "CATEGORY_SELECT": "//div[@class='search-element-wrap categories-for-sell']/div[@class='element-select']/select",
}

class Action(Enum):
    SELL = "sell"
    RENT = "rent"

class Category(Enum):
    APARTMENT = "1"
    COMMERCE = "59"

class Parser(ABC):
    def __init__(self, driver: webdriver.Chrome):

        self.driver = driver
        self.data: Dict[str, List] = {}

    def safe_extract(self, locators: List[Tuple[By, str]], timeout: float) -> Optional[str]:

        if not isinstance(locators, list):
            locators = [locators]

        for by, xpath in locators:
            try:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((by, xpath))
                )
                text = element.text.strip()
                return text if text else pd.NA
            except (TimeoutException, NoSuchElementException):
                logger.debug(f"Element not found with locator: {(by, xpath)}")
                continue
        logger.error(f"No elements found for locators: {locators}")
        return pd.NA

    def year_category(self, year: Optional[str]) -> Optional[str]:
        if pd.isna(year):
            return pd.NA
        try:
            year = int(year)
            if year < 1980:
                return "<1980"
            elif 1980 <= year <= 1990:
                return "1980-1990"
            elif 1990 < year <= 2000:
                return "1990-2000"
            elif 2000 < year <= 2010:
                return "2000-2010"
            elif 2010 < year <= 2020:
                return "2010-2020"
            return ">2020"
        except (ValueError, TypeError):
            return pd.NA

    def floor_category(self, floor: Optional[str], max_floor: Optional[str]) -> Optional[str]:
        if pd.isna(floor) or pd.isna(max_floor):
            return pd.NA
        try:
            floor, max_floor = int(floor), int(max_floor)
            if floor == 1:
                return "Первый этаж"
            elif floor == 2:
                return "Второй этаж"
            elif floor > 2 and floor < max_floor - 1:
                return "Средние этажи"
            elif max_floor - floor == 1:
                return "Предпоследний этаж"
            elif floor == max_floor:
                return "Последний этаж"
            return pd.NA
        except (ValueError, TypeError):
            return pd.NA

    def resize(self) -> None:
        max_len = max(len(lst) for lst in self.data.values())
        for key in self.data:
            current_len = len(self.data[key])
            if current_len < max_len:
                self.data[key].extend([pd.NA] * (max_len - current_len))

    def save_to_csv(self, filename: str, encoding: str = CONFIG["OUTPUT_ENCODING"], separator: str = CONFIG["OUTPUT_SEPARATOR"]) -> Optional[pd.DataFrame]:
        try:
            df = pd.DataFrame(self.data)
            df.to_csv(filename, encoding=encoding, sep=separator, mode='a', index=False, header=not os.path.exists(filename))
            logger.info(f"Data saved to {filename}")
            return df
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")
            return None
    
    def clear_data(self):
        for key in self.data:
            self.data[key] = []
    
    @abstractmethod
    def parse_page(self, link: str) -> None:
        pass

    def print_data(self) -> Dict[str, List]:
        return self.data

class AppartmentSellParser(Parser):

    def __init__(self, driver: webdriver.Chrome):
        super().__init__(driver)
        self.data = {
            "Ссылка": [],
            "Комнатность": [],
            "Площадь": [],
            "Этаж": [],
            "Этажность дома": [],
            "Этажность категория": [],
            "Ценна за квм": [],
            "Стоимость": [],
            "Район": [],
            "Адрес": [],
            "ЖК": [],
            "Тип построения": [],
            "Год постройки": [],
            "Год постройки - категория": [],
            "состояние": [],
            "потолки": [],
            "санузел": [],
            "продавец": [],
        }

    def parse_rooms(self) -> None:
        room_size = self.safe_extract([(By.XPATH, XPATHS["OFFER_TITLE"])], CONFIG["TIMEOUT"])
        self.data["Комнатность"].append(
            room_size[0] if pd.notna(room_size) and room_size and room_size[0].isdigit() else pd.NA
        )

    def parse_area(self) -> Optional[float]:
        square = self.safe_extract([(By.XPATH, XPATHS["LIVE_SQUARE"])], CONFIG["TIMEOUT"])
        square_clean = float(re.search(r"\d+\.?\d*", square).group()) if pd.notna(square) else pd.NA
        self.data["Площадь"].append(square_clean)
        return square_clean

    def parse_floor(self) -> None:
        floor = self.safe_extract([(By.XPATH, XPATHS["FLAT_FLOOR"])], CONFIG["TIMEOUT"])
        if pd.notna(floor) and "из" in floor:
            floor_parts = [int(i.strip()) for i in floor.split("из")]
            self.data["Этаж"].append(floor_parts[0])
            self.data["Этажность дома"].append(floor_parts[1])
            self.data["Этажность категория"].append(self.floor_category(floor_parts[0], floor_parts[1]))
        elif pd.notna(floor) and floor.strip().isdigit():
            self.data["Этаж"].append(int(floor))
            self.data["Этажность дома"].append(int(floor))
            self.data["Этажность категория"].append(self.floor_category(floor, floor))
        else:
            self.data["Этаж"].append(pd.NA)
            self.data["Этажность дома"].append(pd.NA)
            self.data["Этажность категория"].append(pd.NA)

    def parse_district(self) -> None:
        district = self.safe_extract([(By.XPATH, XPATHS["LOCATION"])], CONFIG["TIMEOUT"])
        self.data["Район"].append(
            district.split(",")[1].strip() if pd.notna(district) and len(district.split(",")) > 1 else pd.NA
        )

    def parse_address(self) -> None:
        address = self.safe_extract([(By.XPATH, XPATHS["OFFER_TITLE"])], CONFIG["TIMEOUT"])
        self.data["Адрес"].append(
            address.split(",")[-1].strip() if pd.notna(address) and "," in address else pd.NA
        )

    def parse_residential_complex(self) -> None:
        residential_complex = self.safe_extract([(By.XPATH, XPATHS["RESIDENTIAL_COMPLEX"])], CONFIG["TIMEOUT"])
        self.data["ЖК"].append(residential_complex)

    def parse_building_type(self) -> None:
        building_type = self.safe_extract([(By.XPATH, XPATHS["BUILDING_TYPE"])], CONFIG["TIMEOUT"])
        self.data["Тип построения"].append(building_type)

    def parse_construction_year(self) -> None:
        year = self.safe_extract([(By.XPATH, XPATHS["HOUSE_YEAR"])], CONFIG["TIMEOUT"])
        self.data["Год постройки"].append(year)
        self.data["Год постройки - категория"].append(self.year_category(year))

    def parse_condition(self) -> None:
        condition = self.safe_extract([(By.XPATH, XPATHS["RENOVATION"])], CONFIG["TIMEOUT"])
        self.data["состояние"].append(condition)

    def parse_ceiling_height(self) -> None:
        ceiling_height = self.safe_extract([(By.XPATH, x) for x in XPATHS["CEILING"]], CONFIG["TIMEOUT"])
        self.data["потолки"].append(ceiling_height)

    def parse_bathroom(self) -> None:
        bathroom = self.safe_extract([(By.XPATH, x) for x in XPATHS["TOILET"]], CONFIG["TIMEOUT"])
        self.data["санузел"].append(bathroom)

    def parse_seller(self) -> None:
        seller = self.safe_extract([(By.XPATH, x) for x in XPATHS["SELLER"]], CONFIG["TIMEOUT"])
        self.data["продавец"].append(seller)

    def parse_price(self, area: Optional[float]) -> None:
        try:
            price = self.safe_extract([(By.XPATH, x) for x in XPATHS["PRICE"]], CONFIG["TIMEOUT"])
            price_clean = re.sub(r"[^\d\s]", "", price).strip().replace(" ", "") if pd.notna(price) else pd.NA
            self.data["Стоимость"].append(price_clean)
            self.data["Ценна за квм"].append(
                round(float(price_clean) / float(area), 2) if pd.notna(price_clean) and pd.notna(area) else pd.NA
            )
        except ValueError:
            print(f"couldn't convert the price type: {type(price_clean)} to float")
            logger.error(f"couldn't convert the price type: {type(price_clean)} to float")
    def parse_page(self, link: str) -> None:
        try:
            self.driver.get(link)
            self.driver.implicitly_wait(1)
            self.data["Ссылка"].append(link)
            area = self.parse_area()
            self.parse_rooms()
            self.parse_floor()
            self.parse_district()
            self.parse_address()
            self.parse_residential_complex()
            self.parse_building_type()
            self.parse_construction_year()
            self.parse_condition()
            self.parse_ceiling_height()
            self.parse_bathroom()
            self.parse_seller()
            self.parse_price(area)
        except Exception as e:
            logger.error(f"Error parsing page {link}: {e}")

class AppartmentRentParser(Parser):

    def __init__(self, driver: webdriver.Chrome):
        super().__init__(driver)
        self.data = {
            "Ссылка": [],
            "Комнатность": [],
            "Площадь": [],
            "Этаж": [],
            "Этажность дома": [],
            "Этажность категория": [],
            "Ценна за квм": [],
            "Ценна": [],
            "Район": [],
            "Адрес": [],
            "ЖК": [],
            "Тип построения": [],
            "Год постройки": [],
            "Год постройки - категория": [],
            "состояние": [],
            "потолки": [],
            "санузел": [],
            "продавец": [],
        }

    def parse_rooms(self) -> None:
        room_size = self.safe_extract([(By.XPATH, XPATHS["OFFER_TITLE"])], CONFIG["TIMEOUT"])
        self.data["Комнатность"].append(
            room_size[0] if pd.notna(room_size) and room_size and room_size[0].isdigit() else pd.NA
        )

    def parse_area(self) -> Optional[float]:
        square = self.safe_extract([(By.XPATH, XPATHS["LIVE_SQUARE"])], CONFIG["TIMEOUT"])
        square_clean = float(re.search(r"\d+\.?\d*", square).group()) if pd.notna(square) else pd.NA
        self.data["Площадь"].append(square_clean)
        return square_clean

    def parse_floor(self) -> None:
        floor = self.safe_extract([(By.XPATH, XPATHS["FLAT_FLOOR"])], CONFIG["TIMEOUT"])
        if pd.notna(floor) and "из" in floor:
            floor_parts = [int(i.strip()) for i in floor.split("из")]
            self.data["Этаж"].append(floor_parts[0])
            self.data["Этажность дома"].append(floor_parts[1])
            self.data["Этажность категория"].append(self.floor_category(floor_parts[0], floor_parts[1]))
        else:
            self.data["Этаж"].append(pd.NA)
            self.data["Этажность дома"].append(pd.NA)
            self.data["Этажность категория"].append(pd.NA)

    def parse_district(self) -> None:
        district = self.safe_extract([(By.XPATH, XPATHS["LOCATION"])], CONFIG["TIMEOUT"])
        self.data["Район"].append(
            district.split(",")[1].strip() if pd.notna(district) and len(district.split(",")) > 1 else pd.NA
        )

    def parse_address(self) -> None:
        address = self.safe_extract([(By.XPATH, XPATHS["OFFER_TITLE"])], CONFIG["TIMEOUT"])
        self.data["Адрес"].append(
            address.split(",")[-1].strip() if pd.notna(address) and "," in address else pd.NA
        )

    def parse_residential_complex(self) -> None:
        residential_complex = self.safe_extract([(By.XPATH, XPATHS["RESIDENTIAL_COMPLEX"])], CONFIG["TIMEOUT"])
        self.data["ЖК"].append(residential_complex)

    def parse_building_type(self) -> None:
        building_type = self.safe_extract([(By.XPATH, XPATHS["BUILDING_TYPE"])], CONFIG["TIMEOUT"])
        self.data["Тип построения"].append(building_type)

    def parse_construction_year(self) -> None:
        year = self.safe_extract([(By.XPATH, XPATHS["HOUSE_YEAR"])], CONFIG["TIMEOUT"])
        self.data["Год постройки"].append(year)
        self.data["Год постройки - категория"].append(self.year_category(year))

    def parse_condition(self) -> None:
        condition = self.safe_extract([(By.XPATH, XPATHS["RENT_RENOVATION"])], CONFIG["TIMEOUT"])
        self.data["состояние"].append(condition)

    def parse_ceiling_height(self) -> None:
        ceiling_height = self.safe_extract([(By.XPATH, XPATHS["CEILING"][0])], CONFIG["TIMEOUT"])
        self.data["потолки"].append(ceiling_height)

    def parse_bathroom(self) -> None:
        bathroom = self.safe_extract([(By.XPATH, x) for x in XPATHS["TOILET"]], CONFIG["TIMEOUT"])
        self.data["санузел"].append(bathroom)

    def parse_seller(self) -> None:
        seller = self.safe_extract([(By.XPATH, x) for x in XPATHS["SELLER"]], CONFIG["TIMEOUT"])
        self.data["продавец"].append(seller)

    def parse_price(self, area: Optional[float]) -> None:
        try:
            price = self.safe_extract([(By.XPATH, x) for x in XPATHS["PRICE"]], CONFIG["TIMEOUT"])
            price_clean = re.sub(r"[^\d\s]", "", price).strip().replace(" ", "") if pd.notna(price) else pd.NA
            self.data["Ценна"].append(price_clean)
            self.data["Ценна за квм"].append(
                round(float(price_clean) / float(area), 2) if pd.notna(price_clean) and pd.notna(area) else pd.NA
            )
        except ValueError:
            print(f"couldn't convert the price type: {type(price_clean)} to float")
            logger.error(f"couldn't convert the price type: {type(price_clean)} to float")  

    def parse_page(self, link: str) -> None:
        try:
            self.driver.get(link)
            self.driver.implicitly_wait(1)
            self.data["Ссылка"].append(link)
            area = self.parse_area()
            self.parse_rooms()
            self.parse_floor()
            self.parse_district()
            self.parse_address()
            self.parse_residential_complex()
            self.parse_building_type()
            self.parse_construction_year()
            self.parse_condition()
            self.parse_ceiling_height()
            self.parse_bathroom()
            self.parse_seller()
            self.parse_price(area)
        except Exception as e:
            logger.error(f"Error parsing page {link}: {e}")

class CommerceSellParser(Parser):

    def __init__(self, driver: webdriver.Chrome):
        super().__init__(driver)
        self.data = {
            "Ссылка": [],
            "Площадь": [],
            "Этажность": [],
            "Ценна за квм": [],
            "Стоимость": [],
            "Район": [],
            "Адрес": [],
            "Размещение объекта": [],
            "Название объекта": [],
            "Год постройки": [],
            "Год постройки - категория": [],
            "состояние": [],
            "потолки": [],
            "Действующий бизнес": [],
            "коммуникации": [],
            "Линия домов": [],
            "Безопасность": [],
            "Свободная планировка": [],
            "Вход": [],
            "Парковка": [],
            "Выделенная мощность": [],
            "продавец": [],
        }

    def parse_area(self) -> Optional[float]:
        square = self.safe_extract([(By.XPATH, x) for x in [XPATHS["LIVE_SQUARE"], XPATHS["COM_SQUARE"]]], CONFIG["TIMEOUT"])
        square_clean = float(re.search(r"\d+\.?\d*", square).group()) if pd.notna(square) else pd.NA
        self.data["Площадь"].append(square_clean)
        return square_clean

    def parse_floor(self) -> None:
        floor = self.safe_extract([(By.XPATH, x) for x in [XPATHS["HOUSE_FLOOR_NUM"], XPATHS["FLAT_FLOOR"]]], CONFIG["TIMEOUT"])
        self.data["Этажность"].append(floor)

    def parse_district(self) -> None:
        district = self.safe_extract([(By.XPATH, XPATHS["LOCATION"])], CONFIG["TIMEOUT"])
        self.data["Район"].append(
            district.split(",")[1].strip() if pd.notna(district) and len(district.split(",")) > 1 else pd.NA
        )

    def parse_address(self) -> None:
        address = self.safe_extract([(By.XPATH, XPATHS["ADDRESS"])], CONFIG["TIMEOUT"])
        self.data["Адрес"].append(
            address.split(",")[-1].strip() if pd.notna(address) and "," in address else pd.NA
        )

    def parse_object_placement(self) -> None:
        object_placement = self.safe_extract([(By.XPATH, XPATHS["COM_LOCATION"])], CONFIG["TIMEOUT"])
        self.data["Размещение объекта"].append(object_placement)

    def parse_object_name(self) -> None:
        object_name = self.safe_extract([(By.XPATH, XPATHS["COMPLEX_NAME"])], CONFIG["TIMEOUT"])
        self.data["Название объекта"].append(object_name)

    def parse_construction_year(self) -> None:
        year = self.safe_extract([(By.XPATH, XPATHS["HOUSE_YEAR"])], CONFIG["TIMEOUT"])
        self.data["Год постройки"].append(year)
        self.data["Год постройки - категория"].append(self.year_category(year))

    def parse_condition(self) -> None:
        condition = self.safe_extract([(By.XPATH, x) for x in XPATHS["COM_RENOVATION"]], CONFIG["TIMEOUT"])
        self.data["состояние"].append(condition)

    def parse_ceiling_height(self) -> None:
        ceiling_height = self.safe_extract([(By.XPATH, x) for x in XPATHS["CEILING"]], CONFIG["TIMEOUT"])
        self.data["потолки"].append(ceiling_height)

    def parse_operating_business(self) -> None:
        operating_business = self.safe_extract([(By.XPATH, x) for x in XPATHS["OPERATING_BUSINESS"]], CONFIG["TIMEOUT"])
        self.data["Действующий бизнес"].append(operating_business)

    def parse_communications(self) -> None:
        communications = self.safe_extract([(By.XPATH, x) for x in XPATHS["COMMUNICATIONS"]], CONFIG["TIMEOUT"])
        self.data["коммуникации"].append(communications)

    def parse_location_line(self) -> None:
        location_line = self.safe_extract([(By.XPATH, x) for x in XPATHS["LOCATION_LINE"]], CONFIG["TIMEOUT"])
        self.data["Линия домов"].append(location_line)

    def parse_security(self) -> None:
        security = self.safe_extract([(By.XPATH, x) for x in XPATHS["SECURITY"]], CONFIG["TIMEOUT"])
        self.data["Безопасность"].append(security)

    def parse_free_layout(self) -> None:
        free_layout = self.safe_extract([(By.XPATH, XPATHS["CUSTOM_LAYOUT"])], CONFIG["TIMEOUT"])
        self.data["Свободная планировка"].append(free_layout)

    def parse_entrance(self) -> None:
        entrance = self.safe_extract([(By.XPATH, XPATHS["ENTRANCE"])], CONFIG["TIMEOUT"])
        self.data["Вход"].append(entrance)

    def parse_parking(self) -> None:
        parking = self.safe_extract([(By.XPATH, x) for x in XPATHS["PARKING"]], CONFIG["TIMEOUT"])
        self.data["Парковка"].append(parking)

    def parse_allocated_power(self) -> None:
        allocated_power = self.safe_extract([(By.XPATH, x) for x in XPATHS["ALLOCATED_POWER"]], CONFIG["TIMEOUT"])
        self.data["Выделенная мощность"].append(allocated_power)

    def parse_seller(self) -> None:
        seller = self.safe_extract([(By.XPATH, x) for x in XPATHS["SELLER"]], CONFIG["TIMEOUT"])
        self.data["продавец"].append(seller)

    def parse_price(self, area: Optional[float]) -> None:
        try:
            price = self.safe_extract([(By.XPATH, x) for x in XPATHS["COM_PRICE"]], CONFIG["TIMEOUT"])
            price_clean = re.sub(r"[^\d\s]", "", price).strip().replace(" ", "") if pd.notna(price) else pd.NA
            self.data["Стоимость"].append(price_clean)
            self.data["Ценна за квм"].append(
                round(float(price_clean) / float(area), 2) if pd.notna(price_clean) and pd.notna(area) else pd.NA
            )
        except ValueError:
            print(f"couldn't convert the price type: {type(price_clean)} to float")
            logger.error(f"couldn't convert the price type: {type(price_clean)} to float")
            
    def parse_page(self, link: str) -> None:
        """Parse a single commercial sale listing page."""
        try:
            self.driver.get(link)
            self.driver.implicitly_wait(1)
            self.data["Ссылка"].append(link)
            area = self.parse_area()
            self.parse_floor()
            self.parse_district()
            self.parse_address()
            self.parse_object_placement()
            self.parse_object_name()
            self.parse_construction_year()
            self.parse_condition()
            self.parse_ceiling_height()
            self.parse_operating_business()
            self.parse_communications()
            self.parse_location_line()
            self.parse_security()
            self.parse_free_layout()
            self.parse_entrance()
            self.parse_parking()
            self.parse_allocated_power()
            self.parse_seller()
            self.parse_price(area)
        except Exception as e:
            logger.error(f"Error parsing page {link}: {e}")

class CommerceRentParser(Parser):

    def __init__(self, driver: webdriver.Chrome):
        super().__init__(driver)
        self.data = {
            "Ссылка": [],
            "Площадь": [],
            "Этажность": [],
            "Ценна за квм": [],
            "Стоимость": [],
            "Район": [],
            "Адрес": [],
            "Размещение объекта": [],
            "Название объекта": [],
            "Год постройки": [],
            "Год постройки - категория": [],
            "состояние": [],
            "потолки": [],
            "Действующий бизнес": [],
            "коммуникации": [],
            "Линия домов": [],
            "Безопасность": [],
            "Свободная планировка": [],
            "Вход": [],
            "Парковка": [],
            "Выделенная мощность": [],
            "продавец": [],
        }

    def parse_area(self) -> Optional[float]:
        square = self.safe_extract([(By.XPATH, XPATHS["COM_SQUARE"])], CONFIG["TIMEOUT"])
        square_clean = float(re.search(r"\d+\.?\d*", square).group()) if pd.notna(square) else pd.NA
        self.data["Площадь"].append(square_clean)
        return square_clean

    def parse_floor(self) -> None:
        floor = self.safe_extract([(By.XPATH, x) for x in [XPATHS["HOUSE_FLOOR_NUM"], XPATHS["FLAT_FLOOR"]]], CONFIG["TIMEOUT"])
        self.data["Этажность"].append(floor)

    def parse_district(self) -> None:
        district = self.safe_extract([(By.XPATH, XPATHS["LOCATION"])], CONFIG["TIMEOUT"])
        self.data["Район"].append(
            district.split(",")[-1].strip() if pd.notna(district) and "," in district else pd.NA
        )

    def parse_address(self) -> None:
        address = self.safe_extract([(By.XPATH, XPATHS["ADDRESS"])], CONFIG["TIMEOUT"])
        self.data["Адрес"].append(
            address.split(",")[-1].strip() if pd.notna(address) and "," in address else address if pd.notna(address) else pd.NA
        )

    def parse_object_placement(self) -> None:
        object_placement = self.safe_extract([(By.XPATH, XPATHS["COM_LOCATION"])], CONFIG["TIMEOUT"])
        self.data["Размещение объекта"].append(object_placement)

    def parse_object_name(self) -> None:
        object_name = self.safe_extract([(By.XPATH, XPATHS["COMPLEX_NAME"])], CONFIG["TIMEOUT"])
        self.data["Название объекта"].append(object_name)

    def parse_construction_year(self) -> None:
        year = self.safe_extract([(By.XPATH, XPATHS["HOUSE_YEAR"])], CONFIG["TIMEOUT"])
        self.data["Год постройки"].append(year)
        self.data["Год постройки - категория"].append(self.year_category(year))

    def parse_condition(self) -> None:
        condition = self.safe_extract([(By.XPATH, x) for x in XPATHS["COM_RENOVATION"]], CONFIG["TIMEOUT"])
        self.data["состояние"].append(condition)

    def parse_ceiling_height(self) -> None:
        ceiling_height = self.safe_extract([(By.XPATH, x) for x in XPATHS["CEILING"]], CONFIG["TIMEOUT"])
        self.data["потолки"].append(ceiling_height)

    def parse_operating_business(self) -> None:
        operating_business = self.safe_extract([(By.XPATH, x) for x in XPATHS["OPERATING_BUSINESS"]], CONFIG["TIMEOUT"])
        self.data["Действующий бизнес"].append(operating_business)

    def parse_communications(self) -> None:
        communications = self.safe_extract([(By.XPATH, x) for x in XPATHS["COMMUNICATIONS"]], CONFIG["TIMEOUT"])
        self.data["коммуникации"].append(communications)

    def parse_location_line(self) -> None:
        location_line = self.safe_extract([(By.XPATH, x) for x in XPATHS["LOCATION_LINE"]], CONFIG["TIMEOUT"])
        self.data["Линия домов"].append(location_line)

    def parse_security(self) -> None:
        security = self.safe_extract([(By.XPATH, x) for x in XPATHS["SECURITY"]], CONFIG["TIMEOUT"])
        self.data["Безопасность"].append(security)

    def parse_free_layout(self) -> None:
        free_layout = self.safe_extract([(By.XPATH, XPATHS["CUSTOM_LAYOUT"])], CONFIG["TIMEOUT"])
        self.data["Свободная планировка"].append(free_layout)

    def parse_entrance(self) -> None:
        entrance = self.safe_extract([(By.XPATH, XPATHS["ENTRANCE"])], CONFIG["TIMEOUT"])
        self.data["Вход"].append(entrance)

    def parse_parking(self) -> None:
        parking = self.safe_extract([(By.XPATH, x) for x in XPATHS["PARKING"]], CONFIG["TIMEOUT"])
        self.data["Парковка"].append(parking)

    def parse_allocated_power(self) -> None:
        allocated_power = self.safe_extract([(By.XPATH, x) for x in XPATHS["ALLOCATED_POWER"]], CONFIG["TIMEOUT"])
        self.data["Выделенная мощность"].append(allocated_power)

    def parse_seller(self) -> None:
        seller = self.safe_extract([(By.XPATH, x) for x in XPATHS["SELLER"]], CONFIG["TIMEOUT"])
        self.data["продавец"].append(seller)

    def parse_price(self, area: Optional[float]) -> None:
        try:
            price = self.safe_extract([(By.XPATH, x) for x in XPATHS["COM_PRICE"]], CONFIG["TIMEOUT"])
            price_clean = re.sub(r"[^\d\s]", "", price).strip().replace(" ", "") if pd.notna(price) else pd.NA
            self.data["Стоимость"].append(price_clean)
            self.data["Ценна за квм"].append(
                round(float(price_clean) / float(area), 2) if pd.notna(price_clean) and pd.notna(area) else pd.NA
            )
        except ValueError:
            print(f"couldn't convert the price type: {type(price_clean)} to float")
            logger.error(f"couldn't convert the price type: {type(price_clean)} to float")

    def parse_page(self, link: str) -> None:
        try:
            self.driver.get(link)
            self.driver.implicitly_wait(1)
            self.data["Ссылка"].append(link)
            area = self.parse_area()
            self.parse_floor()
            self.parse_district()
            self.parse_address()
            self.parse_object_placement()
            self.parse_object_name()
            self.parse_construction_year()
            self.parse_condition()
            self.parse_ceiling_height()
            self.parse_operating_business()
            self.parse_communications()
            self.parse_location_line()
            self.parse_security()
            self.parse_free_layout()
            self.parse_entrance()
            self.parse_parking()
            self.parse_allocated_power()
            self.parse_seller()
            self.parse_price(area)
        except Exception as e:
            logger.error(f"Error parsing page {link}: {e}")

@contextmanager
def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = None
    try:
        driver = webdriver.Chrome()
        yield driver
    except Exception as e:
        logger.error(f"Driver initialization failed: {e}")
        raise
    finally:
        if driver:
            driver.quit()
            logger.info("Driver closed")

def select_category(driver: webdriver.Chrome, action: str, category: str) -> Optional[str]:
    driver.get(CONFIG["SITE_URL"])
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "category-type"))
        )
        Select(driver.find_element(By.XPATH, XPATHS["CATEGORY_SELECT"])).select_by_value(category)
        Select(driver.find_element(By.CLASS_NAME, "category-type")).select_by_value(action)
        driver.find_element(By.XPATH, XPATHS["SEARCH_BUTTON"]).click()
        return driver.current_url
    except Exception as e:
        logger.error(f"Error selecting category ({action}, {category}): {e}")
        return None

def get_links(driver: webdriver.Chrome) -> List[str]:
    try:
        divs = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "a-card__header-left"))
        )
        return [div.find_element(By.TAG_NAME, "a").get_attribute("href") for div in divs]
    except Exception as e:
        logger.error(f"Error extracting links: {e}")
        return []

def get_user_input(method: int) -> Tuple[str, str, int, Optional[int]]:
    action_map = {"1": Action.SELL.value, "2": Action.RENT.value}
    category_map = {"1": Category.APARTMENT.value, "2": Category.COMMERCE.value}

    action = input("Выберите действие:\n1. Продать (sell)\n2. Арендовать (rent)\nВведите (1/2/sell/rent): ").strip().lower()
    action = action_map.get(action, action)
    if action not in [a.value for a in Action]:
        raise ValueError(f"Invalid action: {action}")

    category = input("Выберите категорию:\n1. Квартира\n2. Коммерческая недвижимость (59)\nВведите (1/2): ").strip()
    category = category_map.get(category, category)
    if category not in [c.value for c in Category]:
        raise ValueError(f"Invalid category: {category}")

    try:
        save_count = int(input("Введите количество сохранений: ").strip())
        if save_count < 1:
            raise ValueError("Save count must be greater than 0")
    except ValueError as e:
        logger.error(f"Invalid save count: {e}")
        raise ValueError("Please enter a valid integer for save count")

    page_count = None
    if method == 1:
        try:
            page_count = int(input("Введите количество страниц для парсинга: ").strip())
            if page_count < 1:
                raise ValueError("Page count must be greater than 0")
        except ValueError as e:
            logger.error(f"Invalid page count: {e}")
            raise ValueError("Please enter a valid integer for page count")

    return action, category, save_count, page_count

def get_parsing_method():
    try:
        method = int(input("\n1. Ссылка уже задана\n2. Ссылка с консоли\nВведите (1/2): ").strip())
        if method == 1 or method == 2:
            return method
        else:
            raise ValueError("method must be 1 or 2")
    except ValueError as e:
        logger.error(f"Invalid method: {e}")
        raise ValueError("Please enter a valid integer for method")

def main():
    try:
        method = get_parsing_method()
        action, category, save_count, page_count = get_user_input(method)

        parser_map = {
            (Action.SELL.value, Category.APARTMENT.value): AppartmentSellParser,
            (Action.SELL.value, Category.COMMERCE.value): CommerceSellParser,
            (Action.RENT.value, Category.APARTMENT.value): AppartmentRentParser,
            (Action.RENT.value, Category.COMMERCE.value): CommerceRentParser,
        }

        parser_class = parser_map.get((action, category))
        if not parser_class:
            logger.error(f"Invalid action or category: {action}, {category}")
            print(f"Invalid action or category: {action}, {category}")
            return

        output_file = f"{action}_{'apartments' if category == Category.APARTMENT.value else 'commerce'}.csv"

        with init_driver() as driver:
            parser = None

            if method == 1:
                save_count = min(save_count, CONFIG["AVG_NUM_OF_ADS"] * page_count)
                main_url = select_category(driver, action, category)
                if not main_url:
                    logger.error("Failed to select category")
                    print("Failed to select category")
                    return

                base_url = CONFIG["BASE_URLS"].get((action, category))
                if not base_url:
                    logger.error(f"No base URL for action: {action}, category: {category}")
                    print(f"No base URL for action: {action}, category: {category}")
                    return

                parser = parser_class(driver)
                page_count = min(page_count, CONFIG["MAX_PAGES"])
                logger.info(f"Processing {page_count} pages (max: {CONFIG['MAX_PAGES']})")

                for page in range(1, page_count + 1):
                    page_url = f"{base_url}page={page}"
                    logger.info(f"Processing page {page}: {page_url}")
                    driver.get(page_url)

                    try:
                        WebDriverWait(driver, 2).until(
                            EC.presence_of_all_elements_located((By.CLASS_NAME, "a-card__header-left"))
                        )
                        links = get_links(driver)
                        if not links:
                            logger.warning(f"No listings found on page {page}")
                            print(f"No listings found on page {page}")
                            continue

                        logger.info(f"Found {len(links)} listings on page {page}")
                        print(f"Found {len(links)} listings on page {page}")

                        i = 0
                        for link in links:
                            logger.info(f"Parsing listing: {link}")
                            parser.parse_page(link)
                            i += 1
                            time.sleep(random.uniform(0.5, 1.5))

                            if i >= save_count:
                                parser.resize()
                                parser.save_to_csv(output_file)
                                parser.clear_data()
                                i = 0

                    except Exception as e:
                        logger.error(f"Error processing page {page}: {e}")
                        print(f"Error processing page {page}: {e}")

            elif method == 2:
                save_count = min(save_count, CONFIG["AVG_NUM_OF_ADS"])
                parser = parser_class(driver)

                while True:
                    page_link = input("Введите ссылку или 1 для закрытия программы: ").strip()
                    if page_link == "1":
                        break

                    if not page_link:
                        logger.error("Empty URL provided")
                        print("Ошибка: Ссылка не может быть пустой")
                        continue

                    try:
                        parsed_url = urllib.parse.urlparse(page_link)
                        if parsed_url.scheme != "https" or parsed_url.netloc != "krisha.kz":
                            logger.error(f"Invalid URL: {page_link}")
                            print("Ошибка: Введите корректную ссылку на https://krisha.kz/")
                            continue
                    except ValueError:
                        logger.error(f"Invalid URL format: {page_link}")
                        print("Ошибка: Неверный формат ссылки")
                        continue

                    driver.get(page_link)
                    driver.implicitly_wait(2)

                    links = get_links(driver)
                    if not links:
                        logger.warning(f"No listings found on page {page_link}")
                        print(f"No listings found on page {page_link}")
                        continue

                    logger.info(f"Found {len(links)} listings on page {page_link}")
                    print(f"Found {len(links)} listings on page {page_link}")

                    i = 0
                    for link in links:
                        logger.info(f"Parsing listing: {link}")
                        parser.parse_page(link)
                        i += 1
                        time.sleep(random.uniform(0.5, 1.5))

                        if i >= save_count:
                            parser.resize()
                            parser.save_to_csv(output_file)
                            parser.clear_data()
                            i = 0

            if parser and any(parser.data.values()):
                parser.resize()
                parser.save_to_csv(output_file)
                logger.info(f"Final data saved to {output_file}")
                print(f"Final data saved to {output_file}")

    except KeyboardInterrupt:
        logger.info("Program interrupted by user")
        print("Program interrupted by user")
        if parser and any(parser.data.values()):
            parser.resize()
            parser.save_to_csv(output_file)
            logger.info(f"Data saved to {output_file}")
            print(f"Data saved to {output_file}")
    except Exception as e:
        logger.error(f"Program error: {e}")
        print(f"Program error: {e}")

if __name__ == "__main__":
    main()