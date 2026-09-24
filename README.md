# Movie Review Platform

A Django learning project for discovering movies and series through OMDb, keeping watch lists, rating titles and writing reviews. It shows a complete web workflow with authentication and local data persistence.

## Features

- Search and paginate movies and series from the OMDb API
- Movie details, genres, actors, posters, and external ratings
- Registration, login, profiles, and profile pictures
- Watched and watch-later collections
- Ratings, reviews, comments, likes, and dislikes
- Django admin and SQLite persistence for local development

## Stack

Python, Django 5, SQLite, Requests, Pillow, Materialize CSS

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cd django/django_projesi/film_dizi_puanlama_website
copy .env.example .env
python manage.py migrate
python manage.py runserver
```

On macOS/Linux, activate with `source .venv/bin/activate` and use `cp` instead of `copy`.

Create an OMDb key at the provider's website and set `OMDB_API_KEY` in the local `.env`. Never commit that file. Set a unique `DJANGO_SECRET_KEY` as well.

Open `http://127.0.0.1:8000/movie/`.

## Tests

```bash
cd django/django_projesi/film_dizi_puanlama_website
python manage.py check
python manage.py test
```

The test suite covers model slug creation and the credential-safe OMDb client, including missing configuration and mocked API requests.

## Screenshots

![RateFlix home](docs/screenshots/01-home.png)

![Login screen](docs/screenshots/02-login.png)

## Repository hygiene

The original coursework archive contained a Windows virtual environment, local database, poster cache, and test profile pictures. These are excluded from version control. A clean clone recreates its database with Django migrations.

## Security notes

- Secrets are read from environment variables.
- Network requests use a timeout and present a safe error when OMDb is unavailable.
- Runtime databases and uploaded user media must never contain real personal data in a public portfolio repository.

## License

MIT
