FROM python:3.12-slim

WORKDIR /code

RUN pip install poetry

# Zakážeme Poetry vytvářet virtuální prostředí uvnitř kontejneru
RUN poetry config virtualenvs.create false

# Zkopírujeme konfigurační soubory Poetry
COPY pyproject.toml poetry.lock* /code/

# Nainstalujeme závislosti 
RUN poetry install --no-root --no-interaction --no-ansi

COPY ./app /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]