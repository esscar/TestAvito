import pytest
import requests
from test_data import VALID_ITEM_PAYLOAD, INVALID_PRICES

BASE_URL = "https://qa-internship.avito.com"


@pytest.mark.parametrize("invalid_price", INVALID_PRICES)
def test_create_item_invalid_price(auth_session, invalid_price):
    """8, 9: Валидация граничных значений цены"""

    payload = VALID_ITEM_PAYLOAD.copy()
    payload["sellerID"] = auth_session["seller_id"]
    payload["price"] = invalid_price

    resp = requests.post(f"{BASE_URL}/api/1/item", json=payload, headers=auth_session["headers"])
    assert resp.status_code == 400, f"Баг: Сервер принял невалидную цену {invalid_price}"


def test_create_item_missing_fields(auth_session):
    """12: Отсутствие обязательных полей"""
    payload = VALID_ITEM_PAYLOAD.copy()
    del payload["name"]
    payload["sellerID"] = auth_session["seller_id"]

    resp = requests.post(f"{BASE_URL}/api/1/item", json=payload, headers=auth_session["headers"])
    assert resp.status_code == 400, "Баг: Создано объявление без обязательного поля name"


def test_create_item_wrong_types(auth_session):
    """11: Нарушение типов данных"""
    payload = VALID_ITEM_PAYLOAD.copy()
    payload["sellerID"] = auth_session["seller_id"]
    payload["price"] = "пять тысяч"  # Передаем строку вместо числа

    resp = requests.post(f"{BASE_URL}/api/1/item", json=payload, headers=auth_session["headers"])
    assert resp.status_code == 400, "Баг: Сервер принял строку вместо числа в поле price"


def test_create_item_negative_statistics(auth_session):
    """10: Отрицательные счетчики статистики"""
    payload = VALID_ITEM_PAYLOAD.copy()
    payload["sellerID"] = auth_session["seller_id"]
    payload["statistics"] = {"contacts": -5, "likes": -1, "viewCount": -10}

    resp = requests.post(f"{BASE_URL}/api/1/item", json=payload, headers=auth_session["headers"])
    assert resp.status_code == 400, "Баг: Сервер принял отрицательную статистику"


def test_create_item_missing_statistics(auth_session):
    """14: Отсутствие опциональных блоков"""
    payload = VALID_ITEM_PAYLOAD.copy()
    payload["sellerID"] = auth_session["seller_id"]
    del payload["statistics"]

    resp = requests.post(f"{BASE_URL}/api/1/item", json=payload, headers=auth_session["headers"])
    assert resp.status_code in [200, 201]

    item_id = resp.json().get("status").split(" - ")[-1]
    auth_session["items_to_delete"].append(item_id)


def test_create_item_long_string_and_xss(auth_session):
    """13, 15: Сверхдлинная строка и XSS инъекция в поле name"""
    payload = VALID_ITEM_PAYLOAD.copy()
    payload["sellerID"] = auth_session["seller_id"]

    #13: Имя из 10 000 символов
    payload["name"] = "A" * 10000
    resp_long = requests.post(f"{BASE_URL}/api/1/item", json=payload, headers=auth_session["headers"])
    assert resp_long.status_code in [400, 200, 201], "Сервер упал с 500 ошибкой на длинной строке"

    #15: XSS тег
    payload["name"] = "<script>alert('xss')</script>"
    resp_xss = requests.post(f"{BASE_URL}/api/1/item", json=payload, headers=auth_session["headers"])
    if resp_xss.status_code in [200, 201]:
        item_id = resp_xss.json().get("status").split(" - ")[-1]
        auth_session["items_to_delete"].append(item_id)