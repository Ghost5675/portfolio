### README (Русский)

#### Парсер для сайта krisha.kz

**Описание**  
Этот проект представляет собой парсер, разработанный для компании "SvoyDom" для сбора данных с сайта krisha.kz. Парсер предназначен для извлечения информации о продаже и аренде жилой и коммерческой недвижимости, включая такие характеристики, как площадь, этажность, цена, адрес, состояние объекта и другие параметры.

**Функциональность**  
- Поддержка парсинга данных о продаже и аренде квартир и коммерческой недвижимости.  
- Извлечение подробной информации об объектах, включая:  
  - Ссылку на объявление  
  - Количество комнат (для квартир)  
  - Площадь объекта  
  - Этаж и этажность здания  
  - Цена и цена за квадратный метр  
  - Район, адрес, жилой комплекс (для квартир)  
  - Год постройки и категория года  
  - Состояние объекта, высота потолков, санузел, продавец и другие характеристики (в зависимости от типа недвижимости).  
- Автоматическая обработка страниц с заданным количеством объявлений.  
- Два режима работы:  
  1. Парсинг по заранее заданной категории и количеству страниц.  
  2. Парсинг по конкретной ссылке, предоставленной пользователем.  
- Сохранение данных в CSV-файл с поддержкой кодировки UTF-16 и разделителем "[".  
- Логирование всех операций и ошибок в файл `scraper.log` и на консоль.  
- Использование headless-режима браузера для минимизации нагрузки на систему.

**Требования**  
- Python 3.8+  
- Библиотеки: `selenium`, `pandas`, `urllib`  
- Установленный Chrome WebDriver, совместимый с установленной версией браузера Chrome.  

**Установка**  
1. Установите необходимые библиотеки:  
   ```bash:disable-run
   pip install selenium pandas
   ```
2. Убедитесь, что Chrome WebDriver установлен и доступен в системной переменной PATH.  
3. Склонируйте репозиторий или скопируйте код в локальную директорию.  

**Использование**  
1. Запустите скрипт:  
   ```bash
   python krisha_parser.py
   ```
2. Выберите метод парсинга:  
   - **1**: Парсинг по категории (продажа/аренда, квартира/коммерческая недвижимость) с указанием количества страниц.  
   - **2**: Парсинг по конкретной ссылке, введенной пользователем.  
3. Укажите параметры (действие, категория, количество сохранений, количество страниц при необходимости).  
4. Результаты сохраняются в CSV-файл в зависимости от выбранной категории (`sell_apartments.csv`, `rent_apartments.csv`, `sell_commerce.csv`, `rent_commerce.csv`).  

**Структура кода**  
- **Parser (абстрактный класс)**: Базовый класс для всех парсеров, содержащий общие методы для извлечения данных, сохранения в CSV и обработки ошибок.  
- **AppartmentSellParser / AppartmentRentParser**: Парсеры для продажи и аренды квартир.  
- **CommerceSellParser / CommerceRentParser**: Парсеры для продажи и аренды коммерческой недвижимости.  
- **CONFIG**: Словарь с настройками, включая базовые URL, таймауты и параметры сохранения.  
- **XPATHS**: Словарь с XPath-выражениями для извлечения данных с веб-страниц.  

**Логирование**  
Все действия и ошибки логируются в файл `scraper.log` и выводятся в консоль для удобства отладки.  

**Ограничения**  
- Максимальное количество страниц для парсинга ограничено 1000 (настраивается в `CONFIG`).  
- Парсер работает только с сайтом krisha.kz и требует корректных ссылок.  
- Для корректной работы требуется стабильное интернет-соединение.  

**Контакты**  
Разработано для компании "SvoyDom".  
Для вопросов и предложений: [вставьте контактную информацию].  

---

### README (English)

#### Parser for krisha.kz Website

**Description**  
This project is a web scraper developed for the company "SvoyDom" to extract data from the krisha.kz website. The parser is designed to collect information about the sale and rental of residential and commercial properties, including details such as area, floor, price, address, condition, and other relevant attributes.

**Functionality**  
- Supports parsing of data for the sale and rental of apartments and commercial properties.  
- Extracts detailed information about listings, including:  
  - Listing URL  
  - Number of rooms (for apartments)  
  - Property area  
  - Floor and total building floors  
  - Price and price per square meter  
  - District, address, residential complex (for apartments)  
  - Construction year and year category  
  - Property condition, ceiling height, bathroom, seller, and other attributes (depending on property type).  
- Automatic processing of pages with a specified number of listings.  
- Two operating modes:  
  1. Parsing based on predefined categories and page counts.  
  2. Parsing based on a specific URL provided by the user.  
- Saves data to a CSV file with UTF-16 encoding and "[" as a separator.  
- Logs all operations and errors to a `scraper.log` file and the console.  
- Uses headless browser mode to minimize system load.  

**Requirements**  
- Python 3.8+  
- Libraries: `selenium`, `pandas`, `urllib`  
- Installed Chrome WebDriver compatible with the installed Chrome browser version.  

**Installation**  
1. Install the required libraries:  
   ```bash
   pip install selenium pandas
   ```
2. Ensure Chrome WebDriver is installed and available in the system PATH.  
3. Clone the repository or copy the code to a local directory.  

**Usage**  
1. Run the script:  
   ```bash
   python krisha_parser.py
   ```
2. Select the parsing method:  
   - **1**: Parse by category (sale/rent, apartment/commercial property) with a specified number of pages.  
   - **2**: Parse by a specific URL provided by the user.  
3. Specify parameters (action, category, number of saves, number of pages if applicable).  
4. Results are saved to a CSV file based on the selected category (`sell_apartments.csv`, `rent_apartments.csv`, `sell_commerce.csv`, `rent_commerce.csv`).  

**Code Structure**  
- **Parser (abstract class)**: Base class for all parsers, containing common methods for data extraction, CSV saving, and error handling.  
- **AppartmentSellParser / AppartmentRentParser**: Parsers for apartment sales and rentals.  
- **CommerceSellParser / CommerceRentParser**: Parsers for commercial property sales and rentals.  
- **CONFIG**: Dictionary with settings, including base URLs, timeouts, and saving parameters.  
- **XPATHS**: Dictionary with XPath expressions for extracting data from web pages.  

**Logging**  
All actions and errors are logged to the `scraper.log` file and printed to the console for debugging purposes.  

**Limitations**  
- The maximum number of pages for parsing is limited to 1000 (configurable in `CONFIG`).  
- The parser works only with the krisha.kz website and requires valid URLs.  
- A stable internet connection is required for proper operation.  

**Contacts**  
Developed for the company "SvoyDom".  
For questions and suggestions: [insert contact information].  
