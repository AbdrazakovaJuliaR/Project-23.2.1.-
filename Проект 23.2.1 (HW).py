import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def get_movie_details(film_url):
    response = requests.get(film_url)
    soup = BeautifulSoup(response.text, 'lxml')

    # Получаем жанры
    genres = [genre.text for genre in soup.select('.text-sluglist a')]

    # Получаем режиссера
    director_tag = soup.select_one('.text-sluglist a[href*="/director/"]')
    director = director_tag.text.strip() if director_tag else 'Неизвестно'

    # Получаем актеров
    actors = [actor.text.strip() for actor in soup.select('.cast-list .text-slug')]
    
    return genres, director, actors

def collect_user_rates(user_login):
    page_num = 1
    data = []

    while True:
        url = f'https://letterboxd.com/{user_login}/films/diary/page/{page_num}/'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')

        entries = soup.find_all('tr', class_='diary-entry-row')
        if not entries:
            break  # Если нет записей, rjytw

        for entry in entries:
            film_tag = entry.find('td', class_='td-film-details').find('a')
            film_name = film_tag.text.strip()
            film_url = 'https://letterboxd.com' + film_tag['href']

            release_year = entry.find('td', class_='td-released').text.strip()[-4:]
            rating_tag = entry.find('td', class_='td-rating')
            rating = rating_tag.text.strip() if rating_tag else 'Нет рейтинга'

            # Получаем жанры, режиссера и актеров
            genres, director, actors = get_movie_details(film_url)

            data.append({
                'film_name': film_name,
                'release_year': release_year,
                'rating': rating,
                'genres': genres,
                'director': director,
                'actors': actors
            })

            time.sleep(1)  # Чтобы не получить бан за количество запромов

        page_num += 1  # Переход на след стр

    return data

# Использование функции
user_rates = collect_user_rates(user_login='rfeldman9')
df = pd.DataFrame(user_rates)

# Сохранение в Excel
df.to_excel('user_rates.xlsx', index=False)

print("Данные сохранены в user_rates.xlsx!")
