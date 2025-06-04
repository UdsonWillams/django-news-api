.PHONY: runserver coverage test

localserver:
	export DB_DEBUG=True
	mkdir -p media
	python manage.py migrate
	python manage.py runserver localhost:8000

up:
	docker compose up

test:
	python manage.py test

coverage:
	PYTHONPATH=. pytest --cov=. --cov-report=term --cov-fail-under=85

coverage_detailed:
	PYTHONPATH=. pytest --cov=. --cov-report=term-missing --cov-fail-under=85

html_coverage:
	PYTHONPATH=. pytest --cov=. --cov-fail-under=85 --cov-report=html --disable-warnings
