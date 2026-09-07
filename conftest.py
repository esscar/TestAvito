import pytest
import requests
import time

BASE_URL = "https://qa-internship.avito.com"


@pytest.fixture(scope="function")
def auth_session():
    """Динамически создает пользователя, получает токен и чистит стенд после теста."""
    #Генерация уникальных данных для независимости тестов
    username = f"qa_student_{int(time.time() * 1000)}"
    password = "AutoPassword123!"

    #Регистрация (POST /api/1/register)
    reg_resp = requests.post(f"{BASE_URL}/api/1/register", json={"username": username, "password": password})
    seller_id = reg_resp.json().get("id")

    #Авторизация (POST /api/1/autorize)
    auth_resp = requests.post(f"{BASE_URL}/api/1/autorize", json={"username": username, "password": password})
    token = auth_resp.json().get("accessToken")
    headers = {"Authorization": f"Bearer {token}"}

    #Контейнер для передачи данных в сам автотест
    session_data = {
        "headers": headers,
        "seller_id": seller_id,
        "items_to_delete": []
    }

    yield session_data

    #Удаляем все созданные за время теста объявления
    for item_id in session_data["items_to_delete"]:
        requests.delete(f"{BASE_URL}/api/2/item/{item_id}", headers=headers)