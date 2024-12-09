## Проект Foodgram
Foodgram - это сайт, на котором можно публиковать собственные рецепты, добавлять чужие рецепты в избранное, подписываться на других авторов и создавать список покупок для заданных блюд.
## Вот что было сделано в ходе работы над проектом:
1. создан собственный API-сервис на базе проекта Django;
2. подключено SPA к бэкенду на Django через API;
3. созданы образы и запущены контейнеры Docker;
4. создано, развёрнуто и запущено на сервере мультиконтейнерное приложение;
5. закреплены на практике основы DevOps, включая CI/CD.

Инструменты и стек: #python #JSON #YAML #Django #React #API #Docker #Nginx #PostgreSQL #Gunicorn #JWT #Postman

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
