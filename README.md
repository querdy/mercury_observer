# mercury_observer
тг-бот для автоматизации приема заявок на сырое молоко в ФГИС "Меркурий"

# Стек:
* aiogram
* beautifulsoup4

# Настройка:
* файл settings_example.py переименовать в settings.py и заполнить:
* API_TOKEN_TG: указать API-Token телеграм-бота
* EXECUTE: True - принять заявку и оформить всд, False - только прислать сообщение в чате бота о появившейся заявке
* ENTERPRISE_PATTERNS: массив строк с названиями площадок (можно не полные), на которых необходимо проверять наличие заявок
* VERIFIED_PRODUCTS: массив строк с названиями продуктов (можно не полные), которые считать корректными подтверждения заявки
* VERIFIED_TRANSACTION_TYPE: тип транзакции, который считать корректным для подтверждения заявки
* SCHEDULE_EVERY_TIME: периодичность проверки в минутах
* 
# Запуск:
* main.py