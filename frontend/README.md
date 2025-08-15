# FastAPI Frontend

A simple web frontend for the Translate API using FastAPI and Jinja2.

## Run locally

```sh
uvicorn frontend.main:app --reload
```

- The frontend will be available at http://127.0.0.1:8001
- By default, it expects the API to be at http://api:5001 (Docker) or http://localhost:5001 (local)
- You can override the API base URL with the `API_BASE` environment variable:

```sh
API_BASE=http://localhost:5001 uvicorn frontend.main:app --reload
```
