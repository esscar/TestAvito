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