1. Скопировать переменные окружения из .env.example файла в .env

2. Запустить приложение можно командой
```shell
docker-compose up
```

Запустить периодическую задачу вне расписания можно зайдя в контейнер с приложением:
```shell
docker-compose exec app sh
```
и выполнив команду:
```shell
celery -A config call goods.tasks.calculate_delivery_cost
```
