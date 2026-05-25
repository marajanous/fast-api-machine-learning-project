set shell := ["powershell", "-Command"]

up:
	docker compose up --build -d

down:
	docker compose down

# Spustí pouze testy pro autentizaci
test-auth:
	docker compose run --rm web sh -c "PYTHONPATH=. python tests/test_auth.py"

# Spustí úplně všechny testy v projektu
test-all:
	docker compose run --rm web sh -c "PYTHONPATH=. python -m unittest discover tests"

logs:
	docker compose logs -f web