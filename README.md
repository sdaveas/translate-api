# Translate API

A simple translation API using Flask and Google Translate.

## Requirements
- Python 3.13+
- pipenv or pip

## Installation

```sh
pipenv install
# or
pip install -r requirements.txt
```

## Running the API

```sh
pipenv run python -m app.api
# or
python -m app.api
```

## Production (with Gunicorn)

API:
```sh
gunicorn -w 4 -b 0.0.0.0:5001 app.api:app
```
