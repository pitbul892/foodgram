## Проект Foodgram
Foodgram - сайт, на котором пользователи будут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.
## Технологии
Python, Django, Django Rest Framework, Djoser, PostgreSQL.
Развернуть проект на удаленном сервере:

- Клонировать репозиторий:
```
https://github.com/Pitbul892/foodgram
```
- Скопировать на сервер docker-compose.production.yml и .env
```
 Пример файла .env
POSTGRES_USER=django_user              #пользователь бд
POSTGRES_PASSWORD=mysecretpassword     #пароль бд
POSTGRES_DB=django                     #база данных
DB_HOST=db                             #хост бд
DB_PORT=5432                           #порт бд
DJANGO_DEBUG = False                   #включен ли Debug
DJANGO_SECRET_KEY = django-insecure-cg6*%6d51ef8f#4!r3*$vmxm4) abgjw8mo!4y-q*uq1!4$-89$               #секретный ключ Django
ALLOWED_HOSTS=10.10.10.10,127.0.0.1,localhost,ваш_адрес.org   #разрешенные хосты
```
- Запустить докер docker-compose.production.yml
```
sudo docker compose -f docker-compose.production.yml up -d
```
- Выполнить миграции:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```
- Собрать статику:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```
Создать суперпользователя:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```
