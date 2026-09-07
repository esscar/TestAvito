import requests
from test_data import VALID_ITEM_PAYLOAD

BASE_URL = "https://qa-internship.avito.com"


def test_no_token_access(auth_session):
    """4: Доступ без токена авторизации"""
    payload = VALID_ITEM_PAYLOAD.copy()
    payload["sellerID"] = auth_session["seller_id"]

    #Запрос БЕЗ headers
    resp = requests.post(f"{BASE_URL}/api/1/item", json=payload)
    assert resp.status_code == 401, f"Ожидалась 401, получено: {resp.status_code}"


def test_wrong_seller_id(auth_session):
    """5: Подмена sellerID при создании"""
    payload = VALID_ITEM_PAYLOAD.copy()
    payload["sellerID"] = 999999999  # Чужой ID

    resp = requests.post(f"{BASE_URL}/api/1/item", json=payload, headers=auth_session["headers"])

    #Если баг позволит создать объявление, мы добавим его в очистку
    if resp.status_code == 200:
        item_id = resp.json().get("status").split(" - ")[-1]
        auth_session["items_to_delete"].append(item_id)

    assert resp.status_code in [400,
                                403], f"Баг: Сервер разрешил создать объявление с чужим sellerID. Код {resp.status_code}"


def test_get_nonexistent_item(auth_session):
    """7: Запрос несуществующего ресурса"""
    fake_uuid = "11111111-2222-3333-4444-555555555555"
    resp = requests.get(f"{BASE_URL}/api/1/item/{fake_uuid}", headers=auth_session["headers"])
    assert resp.status_code == 404

def test_delete_other_user_item(auth_session):
    """6: Попытка удалить чужое объявление"""
    #Создаем объявление первым пользователем (из фикстуры)
    payload = VALID_ITEM_PAYLOAD.copy()
    payload["sellerID"] = auth_session["seller_id"]
    create_resp = requests.post(f"{BASE_URL}/api/1/item", json=payload, headers=auth_session["headers"])
    item_id = create_resp.json().get("status").split(" - ")[-1]
    auth_session["items_to_delete"].append(item_id)

    #Регистрируем ВТОРОГО пользователя на лету для теста безопасности
    import time
    other_user = f"hacker_{int(time.time() * 1000)}"
    requests.post(f"{BASE_URL}/api/1/register", json={"username": other_user, "password": "Password123!"})
    auth_resp = requests.post(f"{BASE_URL}/api/1/autorize", json={"username": other_user, "password": "Password123!"})
    other_headers = {"Authorization": f"Bearer {auth_resp.json().get('accessToken')}"}

    #Пытаемся удалить чужое объявление от лица второго пользователя
    del_resp = requests.delete(f"{BASE_URL}/api/2/item/{item_id}", headers=other_headers)
    assert del_resp.status_code in [403, 401], f"Критический баг безопасности: Пользователь смог удалить чужой товар! Код: {del_resp.status_code}"