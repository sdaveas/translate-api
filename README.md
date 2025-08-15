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


## Running the FastAPI Frontend

```sh
pip install -r requirements.frontend.txt
uvicorn fastapi_frontend.main:app --reload
# or for production:
gunicorn -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 fastapi_frontend.main:app
```

The frontend will be available at http://127.0.0.1:8000

## Production (with Gunicorn)

API:
```sh
gunicorn -w 4 -b 0.0.0.0:5001 app.api:app
```
