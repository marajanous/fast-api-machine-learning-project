FROM python:3.12-slim

WORKDIR /code

RUN pip install poetry

RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock* /code/

RUN poetry install --no-root --no-interaction --no-ansi

COPY ./app /code/app

CMD ["sh", "-c", "python -m app.init_db && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]