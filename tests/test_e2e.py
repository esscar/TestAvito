import requests
from test_data import VALID_ITEM_PAYLOAD

BASE_URL = "https://qa-internship.avito.com"


def test_e2e_item_lifecycle(auth_session):
    """1: Полный жизненный цикл объявления"""

    payload = VALID_ITEM_PAYLOAD.copy()
    payload["sellerID"] = auth_session["seller_id"]

    create_resp = requests.post(f"{BASE_URL}/api/1/item", json=payload, headers=auth_session["headers"])
    assert create_resp.status_code == 200

    item_id = create_resp.json().get("status").split(" - ")[-1]
    auth_session["items_to_delete"].append(item_id)

    get_resp = requests.get(f"{BASE_URL}/api/1/item/{item_id}", headers=auth_session["headers"])
    assert get_resp.status_code == 200

    item_data = get_resp.json()[0]
    assert item_data["name"] == payload["name"]
    assert item_data["price"] == payload["price"]

    del_resp = requests.delete(f"{BASE_URL}/api/2/item/{item_id}", headers=auth_session["headers"])
    assert del_resp.status_code == 200
    auth_session["items_to_delete"].remove(item_id)

    get_deleted_resp = requests.get(f"{BASE_URL}/api/1/item/{item_id}", headers=auth_session["headers"])
    assert get_deleted_resp.status_code == 404


def test_get_all_seller_items(auth_session):
    """2: Получение всех объявлений продавца"""
    payload = VALID_ITEM_PAYLOAD.copy()
    payload["sellerID"] = auth_session["seller_id"]

    # Создаем два объявления
    resp1 = requests.post(f"{BASE_URL}/api/1/item", json=payload, headers=auth_session["headers"])
    resp2 = requests.post(f"{BASE_URL}/api/1/item", json=payload, headers=auth_session["headers"])

    id1 = resp1.json().get("status").split(" - ")[-1]
    id2 = resp2.json().get("status").split(" - ")[-1]
    auth_session["items_to_delete"].extend([id1, id2])

    get_resp = requests.get(f"{BASE_URL}/api/1/{auth_session['seller_id']}/item", headers=auth_session["headers"])
    assert get_resp.status_code == 200
    assert type(get_resp.json()) == list, "Ожидался массив объявлений"
    assert len(get_resp.json()) >= 2


def test_statistics_v1_vs_v2(auth_session):
    """3: Сравнение статистики v1 и v2"""
    payload = VALID_ITEM_PAYLOAD.copy()
    payload["sellerID"] = auth_session["seller_id"]
    create_resp = requests.post(f"{BASE_URL}/api/1/item", json=payload, headers=auth_session["headers"])
    item_id = create_resp.json().get("status").split(" - ")[-1]
    auth_session["items_to_delete"].append(item_id)

    stat_v1 = requests.get(f"{BASE_URL}/api/1/statistic/{item_id}", headers=auth_session["headers"])
    stat_v2 = requests.get(f"{BASE_URL}/api/2/statistic/{item_id}", headers=auth_session["headers"])

    assert stat_v1.status_code == 200
    assert stat_v2.status_code == 200