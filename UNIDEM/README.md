# WhatsApp Contact Parser

## Overview

This Python script automates the process of adding student and parent contacts to WhatsApp using data from an Excel file. It was developed for the Unidem Center, which specializes in preparation for the Unified National Testing (ENT) in Kazakhstan. The parser handles the routine task of checking for existing contacts and adding new ones via WhatsApp Web, saving time for administrative staff.

Key features:
- Reads student names, phone numbers, and optional parent phone numbers from an Excel spreadsheet.
- Normalizes phone numbers (supports Russian/Kazakh formats like starting with 8 or +7).
- Checks if the contact already exists in WhatsApp to avoid duplicates.
- Adds new contacts with optional syncing to phone.
- Error handling for timeouts, invalid inputs, and WebDriver issues.
- Bilingual support: The script includes prompts and messages in English (translated from original Russian).

This project is part of my portfolio to demonstrate automation skills using Selenium, Pandas, and web scraping.

## Requirements

- Python 3.x
- Libraries: `selenium`, `pandas`, `webdriver-manager` (for ChromeDriver, though not explicitly used in code; install via `pip install webdriver-manager` if needed)
- Chrome browser and compatible ChromeDriver
- An Excel file (.xlsx) with columns for student names, student phones, and optional parent phones.

Install dependencies:
```
pip install selenium pandas
```

## Usage

1. Run the script:
   ```
   python whatsapp_parser.py
   ```

2. When prompted, enter the path to your Excel file (e.g., `students.xlsx`).

3. Enter the column names for:
   - Student's name
   - Student's phone
   - Parent's phone (optional; enter 0 to skip)

4. Scan the QR code on WhatsApp Web to log in.

5. The script will process each row, adding contacts to WhatsApp.

Note: Ensure WhatsApp Web is accessible and your account is linked. The script uses selectors that may change with WhatsApp updates—update `CONFIG` if needed.

## Example Excel Structure

| Student Name | Student Phone | Parent Phone |
|--------------|---------------|--------------|
| John Doe    | +71234567890 | +71234567891 |
| Jane Smith  | 81234567890  |              |

## Limitations

- Relies on specific CSS/XPath selectors from WhatsApp Web; may break if the UI changes.
- No batch processing for very large files (processes row by row).
- Phone numbers must be in a valid format (10+ digits after normalization).
- Requires manual QR code scanning for authentication.

## License

MIT License. Feel free to use and modify.

---

# Парсер контактов для WhatsApp

## Обзор

Этот скрипт на Python автоматизирует процесс добавления контактов студентов и их родителей в WhatsApp на основе данных из файла Excel. Он был разработан для центра Unidem, специализирующегося на подготовке к ЕНТ (Единое Национальное Тестирование) в Казахстане. Парсер решает рутинную задачу по проверке существующих контактов и добавлению новых через WhatsApp Web, экономя время административному персоналу.

Ключевые особенности:
- Читает имена студентов, номера телефонов и опциональные номера родителей из таблицы Excel.
- Нормализует номера телефонов (поддерживает российские/казахстанские форматы, начинающиеся с 8 или +7).
- Проверяет, существует ли контакт в WhatsApp, чтобы избежать дубликатов.
- Добавляет новые контакты с опциональной синхронизацией на телефон.
- Обработка ошибок для таймаутов, неверных вводов и проблем с WebDriver.
- Двуязычная поддержка: Скрипт включает подсказки и сообщения на английском (переведено из оригинального русского).

Этот проект является частью моего портфолио для демонстрации навыков автоматизации с использованием Selenium, Pandas и веб-скрейпинга.

## Требования

- Python 3.x
- Библиотеки: `selenium`, `pandas`, `webdriver-manager` (для ChromeDriver, если нужно; установите через `pip install webdriver-manager`)
- Браузер Chrome и совместимый ChromeDriver
- Файл Excel (.xlsx) с колонками для имен студентов, телефонов студентов и опциональных телефонов родителей.

Установка зависимостей:
```
pip install selenium pandas
```

## Использование

1. Запустите скрипт:
   ```
   python whatsapp_parser.py
   ```

2. При запросе введите путь к файлу Excel (например, `students.xlsx`).

3. Введите названия колонок для:
   - Имени студента
   - Телефона студента
   - Телефона родителя (опционально; введите 0 для пропуска)

4. Отсканируйте QR-код в WhatsApp Web для входа.

5. Скрипт обработает каждую строку, добавляя контакты в WhatsApp.

Примечание: Убедитесь, что WhatsApp Web доступен и аккаунт связан. Скрипт использует селекторы, которые могут измениться при обновлениях WhatsApp — обновите `CONFIG` при необходимости.

## Пример структуры Excel

| Имя студента | Телефон студента | Телефон родителя |
|--------------|------------------|------------------|
| Джон Доу    | +71234567890     | +71234567891     |
| Джейн Смит  | 81234567890      |                  |

## Ограничения

- Зависит от конкретных CSS/XPath-селекторов WhatsApp Web; может сломаться при изменениях UI.
- Нет пакетной обработки для очень больших файлов (обрабатывает строку за строкой).
- Номера телефонов должны быть в валидном формате (10+ цифр после нормализации).
- Требует ручного сканирования QR-кода для аутентификации.

## Лицензия

Лицензия MIT. Свободно используйте и модифицируйте.