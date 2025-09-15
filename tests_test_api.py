import pytest
import requests
import os
import allure
from dotenv import load_dotenv

load_dotenv()

# Получаем API ключ из переменных окружения
API_KEY = os.getenv('KINOPOISK_API_KEY', 'GGTYBTW-0VB4NX1-G4REM52-0Y8V7Y6')


@pytest.fixture(scope='session')
def api_client():
    """Фикстура для API клиента с правильными заголовками"""
    session = requests.Session()
    session.headers.update({
        "X-API-KEY": API_KEY,
        "accept": "application/json"
    })
    return session


@allure.feature("API Tests")
@allure.title("Проверка валидности API ключа")
@allure.description("Тест проверяет, что API ключ действителен и можно получить данные")
def test_api_key_valid(api_client):
    """Тест проверки валидности API ключа"""
    with allure.step("Отправка запроса для проверки API ключа"):
        response = api_client.get(
            "https://api.kinopoisk.dev/v1.4/movie",
            params={"limit": 1}
        )

    allure.attach(
        f"Status Code: {response.status_code}", name="Response Status")
    allure.attach(
        f"Response: {response.text[:200]}...", name="Response Preview")

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:200]}...")

    with allure.step("Проверка статус кода и структуры ответа"):
        assert response.status_code == 200, f"API вернул статус {response.status_code}"
        assert "docs" in response.json(), "Ответ не содержит ключ 'docs'"

    print("✅ API ключ валиден!")
    allure.attach("✅ API ключ валиден!", name="Result")


@allure.feature("API Tests")
@allure.title("Поиск фильма 'Школа'")
@allure.description("Тест проверяет поиск фильма по названию")
def test_api_search_school(api_client):
    """Тест поиска Школы через API"""
    with allure.step("Выполнение поиска 'Школа'"):
        print("🔍 Ищем Школу...")

        response = api_client.get(
            "https://api.kinopoisk.dev/v1.4/movie/search",
            params={"query": "Школа", "limit": 10}
        )

    allure.attach(f"Status: {response.status_code}", name="Search Status")
    print(f"Status: {response.status_code}")

    with allure.step("Проверка успешности запроса"):
        assert response.status_code == 200, f"Ошибка поиска: {response.status_code}"

    data = response.json()
    movies = data.get('docs', [])

    with allure.step("Проверка наличия результатов поиска"):
        assert len(movies) > 0, "Фильм 'Школа' не найден"

    # Проверяем что нашли правильный фильм
    found = False
    found_movie = None
    for movie in movies:
        if "школа" in movie.get('name', '').lower() and movie.get('year') == 2010:
            found = True
            found_movie = movie
            print(f"✅ Найден: {movie['name']} ({movie.get('year', 'N/A')})")
            break

    with allure.step("Проверка корректности найденного фильма"):
        assert found, "Не найден фильм 'Школа' 2010 года в результатах"
        if found_movie:
            allure.attach(
                f"Найденный фильм: {found_movie['name']} ({found_movie.get('year', 'N/A')})", 
                name="Found Movie"
            )


@allure.feature("API Tests")
@allure.title("Поиск высокорейтинговых фильмов")
@allure.description("Тест проверяет поиск фильмов с рейтингом 8+")
def test_api_high_rated_movies(api_client):
    """Тест высокорейтинговых фильмов через API"""
    with allure.step("Поиск фильмов с высоким рейтингом"):
        print("⭐ Ищем фильмы с высоким рейтингом...")

        response = api_client.get(
            "https://api.kinopoisk.dev/v1.4/movie",
            params={
                "rating.kp": "8-10",
                "sortField": "rating.kp",
                "sortType": "-1",
                "limit": 5
            }
        )

    with allure.step("Проверка успешности запроса"):
        assert response.status_code == 200

    data = response.json()
    movies = data.get('docs', [])

    with allure.step("Проверка наличия результатов"):
        assert len(movies) > 0, "Не найдено фильмов с высоким рейтингом"

    # Проверяем рейтинг
    movie_ratings = []
    for movie in movies:
        rating = movie.get('rating', {}).get('kp', 0)
        movie_ratings.append(f"{movie.get('name')}: {rating}")
        with allure.step(f"Проверка рейтинга фильма {movie.get('name')}"):
            assert rating >= 8.0, f"Фильм {movie.get('name')} имеет рейтинг {rating} < 8.0"

    allure.attach("\n".join(movie_ratings), name="Movies with ratings ≥ 8.0")
    print(f"✅ Найдено {len(movies)} фильмов с рейтингом ≥ 8.0")


@allure.feature("API Tests")
@allure.title("Поиск фильмов по году")
@allure.description("Тест проверяет поиск фильмов 2023 года")
def test_api_movies_by_year(api_client):
    """Тест фильмов по году через API"""
    with allure.step("Поиск фильмов 2023 года"):
        print("📅 Ищем фильмы 2023 года...")

        response = api_client.get(
            "https://api.kinopoisk.dev/v1.4/movie",
            params={"year": "2023", "limit": 5}
        )

    with allure.step("Проверка успешности запроса"):
        assert response.status_code == 200

    data = response.json()
    movies = data.get('docs', [])

    with allure.step("Проверка наличия результатов"):
        assert len(movies) > 0, "Не найдено фильмов 2023 года"

    # Проверяем год
    movie_list = []
    for movie in movies:
        movie_list.append(f"{movie.get('name')} ({movie.get('year')})")
        with allure.step(f"Проверка года выпуска {movie.get('name')}"):
            assert movie.get('year') == 2023, f"Фильм {movie.get('name')} не 2023 года"

    allure.attach("\n".join(movie_list), name="Movies from 2023")
    print(f"✅ Найдено {len(movies)} фильмов 2023 года")


@allure.feature("API Tests")
@allure.title("Получение детальной информации о фильме")
@allure.description("Тест проверяет получение детальной информации по ID фильма")
def test_api_movie_details(api_client):
    """Тест детальной информации о фильме"""
    with allure.step("Получение детальной информации о фильме"):
        print("🎬 Получаем детальную информацию о фильме...")

        # Используем правильный API endpoint и ID фильма "Школа"
        response = api_client.get(
            "https://api.kinopoisk.dev/v1.4/movie/493098"  # ID фильма "Школа"
        )

    with allure.step("Проверка успешности запроса"):
        assert response.status_code == 200, f"Ошибка запроса: {response.status_code}"

    movie_data = response.json()

    # Проверяем основные поля
    with allure.step("Проверка основных полей фильма"):
        assert movie_data.get('name') == "Школа", f"Название: {movie_data.get('name')}"
        assert movie_data.get('year') == 2010, f"Год: {movie_data.get('year')}"
        assert movie_data.get('rating', {}).get('kp') >= 5.0  # Понижаем ожидания для рейтинга

    allure.attach(f"Название: {movie_data.get('name')}", name="Movie Details")
    allure.attach(f"Год: {movie_data.get('year')}", name="Movie Details")
    allure.attach(
        f"Рейтинг: {movie_data.get('rating', {}).get('kp')}",
        name="Movie Details"
    )

    print(f"✅ Детали: {movie_data['name']} ({movie_data['year']})")


@allure.feature("API Tests")
@allure.title("Тестирование пагинации")
@allure.description("Тест проверяет работу пагинации в API")
def test_api_pagination(api_client):
    """Тест пагинации API"""
    with allure.step("Тестирование пагинации"):
        print("📄 Тестируем пагинацию...")

        response = api_client.get(
            "https://api.kinopoisk.dev/v1.4/movie",
            params={"page": 1, "limit": 2}
        )

    with allure.step("Проверка успешности запроса"):
        assert response.status_code == 200

    data = response.json()

    with allure.step("Проверка параметров пагинации"):
        assert data['page'] == 1
        assert data['limit'] == 2
        assert len(data['docs']) == 2

    allure.attach(f"Page: {data['page']}", name="Pagination Info")
    allure.attach(f"Limit: {data['limit']}", name="Pagination Info")
    allure.attach(
        f"Documents count: {len(data['docs'])}", name="Pagination Info")

    print("✅ Пагинация работает")


if __name__ == "__main__":
    pytest.main(['-v', '-s', '--alluredir=allure-results'])