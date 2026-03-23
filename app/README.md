Первый запуск:
docker-compose build
docker-compose up -d db
docker-compose run --rm app alembic upgrade head
docker-compose up -d app
docker-compose exec app python -m app.test_data_faker --clear
