import requests

BASE_URL = "https://qa-internship.avito.com"


def test_e2e_item_lifecycle(auth_session):
    """1: Полный жизненный цикл объявления"""

    #Создаем объявление
    payload = {
        "sellerID": auth_session["seller_id"],
        "name": "Автотест Телефон",
        "price": 50000,
        "statistics": {
            "contacts": 5,
            "likes": 10,
            "viewCount": 15
        }
    }

    create_resp = requests.post(f"{BASE_URL}/api/1/item", json=payload, headers=auth_session["headers"])
    assert create_resp.status_code == 200, f"Ожидался 200, получено: {create_resp.status_code}. Ответ: {create_resp.text}"

    #Парсим ID из строки вида "Сохранили объявление - 734a9bfe-..."
    item_id = create_resp.json().get("status").split(" - ")[-1]

    #Добавляем в фикстуру для очистки
    auth_session["items_to_delete"].append(item_id)

    #Получаем объявление и проверяем данные
    get_resp = requests.get(f"{BASE_URL}/api/1/item/{item_id}", headers=auth_session["headers"])
    assert get_resp.status_code == 200

    #Учитываем баг API: ручка возвращает массив, берем первый элемент
    item_data = get_resp.json()[0]
    assert item_data["name"] == payload["name"], "Имя не совпадает"
    assert item_data["price"] == payload["price"], "Цена не совпадает"
    assert item_data["sellerId"] == payload["sellerID"], "SellerID не совпадает"

    #Удаляем объявление
    del_resp = requests.delete(f"{BASE_URL}/api/2/item/{item_id}", headers=auth_session["headers"])
    assert del_resp.status_code == 200

    #Убираем ID из очереди на очистку, так как мы его уже удалили
    auth_session["items_to_delete"].remove(item_id)

    #Проверяем, что объявление удалено
    get_deleted_resp = requests.get(f"{BASE_URL}/api/1/item/{item_id}", headers=auth_session["headers"])
    assert get_deleted_resp.status_code == 404, "Ожидалась ошибка 404, но объявление все еще существует"