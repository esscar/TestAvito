# test_data.py

# Базовый payload для успешного создания объявления
VALID_ITEM_PAYLOAD = {
    "name": "Автотест Телефон",
    "price": 50000,
    "statistics": {
        "contacts": 5,
        "likes": 10,
        "viewCount": 15
    }
}

# Массив для параметризации (негативные проверки цены)
INVALID_PRICES = [-1, 0, 9999999999999999999]