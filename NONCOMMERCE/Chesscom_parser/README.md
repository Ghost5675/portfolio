# Chess.com Profile Bio Updater

This Python script automates updating a Telegram profile bio with a user's chess.com profile information, specifically their rank and rating in the Kazakhstan (KZ) rapid leaderboard. It uses the `telethon` library to interact with the Telegram API and `selenium` to scrape data from the chess.com leaderboard. The script navigates the leaderboard pages, finds the user's profile, extracts their rank and rating, and updates the Telegram bio with this information.

### Features
- Scrapes rank and rating from the chess.com Kazakhstan rapid leaderboard.
- Automatically updates the Telegram profile bio with the chess.com profile link, rank, and rating.
- Configurable settings for API credentials, profile details, and leaderboard URL.
- Handles pagination and modal popups on the chess.com website.

### Requirements
- Python 3.x
- Libraries: `telethon`, `selenium`
- Chrome WebDriver for Selenium
- Telegram API credentials (`API_ID`, `API_HASH`, `PHONE`)
- chess.com profile name and leaderboard URL

### Usage
1. Install required libraries: `pip install -r requirements.txt`
2. Set up Chrome WebDriver.
3. Update the `CONFIG` dictionary with your Telegram API credentials, chess.com profile name, and leaderboard URL.
4. Run the script: `python chess_parser.py`
5. The script will scrape your rank and rating from chess.com and update your Telegram bio.

### Notes
- Ensure the Chrome WebDriver version matches your installed Chrome browser.
- The script assumes the leaderboard structure and class names remain consistent with chess.com's website.
- Handle Telegram API rate limits and authentication prompts as needed.

Этот Python-скрипт автоматизирует обновление биографии профиля в Telegram, добавляя информацию о профиле пользователя на chess.com, в частности, его ранг и рейтинг в таблице лидеров по рапиду в Казахстане (KZ). Скрипт использует библиотеку `telethon` для взаимодействия с API Telegram и `selenium` для парсинга данных с сайта chess.com. Он переходит по страницам таблицы лидеров, находит профиль пользователя, извлекает его ранг и рейтинг, а затем обновляет биографию в Telegram.

### Особенности
- Извлекает ранг и рейтинг из таблицы лидеров по рапиду на chess.com для Казахстана.
- Автоматически обновляет биографию в Telegram, добавляя ссылку на профиль chess.com, ранг и рейтинг.
- Настраиваемые параметры для учетных данных API, информации о профиле и URL таблицы лидеров.
- Обрабатывает пагинацию и всплывающие окна на сайте chess.com.

### Требования
- Python 3.x
- Библиотеки: `telethon`, `selenium`
- Chrome WebDriver для Selenium
- Учетные данные Telegram API (`API_ID`, `API_HASH`, `PHONE`)
- Имя профиля на chess.com и URL таблицы лидеров

### Использование
1. Установите необходимые библиотеки: `pip install -r requirements.txt`
2. Настройте Chrome WebDriver.
3. Обновите словарь `CONFIG` с вашими учетными данными Telegram API, именем профиля на chess.com и URL таблицы лидеров.
4. Запустите скрипт: `python chess_parser.py`
5. Скрипт извлечет ваш ранг и рейтинг с chess.com и обновит биографию в Telegram.

### Примечания
- Убедитесь, что версия Chrome WebDriver соответствует версии установленного браузера Chrome.
- Скрипт предполагает, что структура таблицы лидеров и имена классов на сайте chess.com остаются неизменными.
- Учитывайте ограничения на частоту запросов Telegram API и запросы на аутентификацию.