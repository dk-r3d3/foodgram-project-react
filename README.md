# Foodgram - продуктовый помощник

[![Django-app workflow](https://github.com/dk-r3d3/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)](https://github.com/dk-r3d3/yamdb_final/actions/workflows/yamdb_workflow.yml)

## Описание проекта
Приложение «Продуктовый помощник»: сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволит пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Подготовка и запуск проекта
##### Клонирование репозитория
Склонируйте репозиторий на локальную машину:
```bash
git@github.com:dk-r3d3/foodgram-project-react.git
```

## Установка на удаленном сервере (Ubuntu):

##### Шаг 1. На сервере установите Docker:
Команда:
```bash
sudo apt install docker.io 
```

##### Шаг 2. Установите docker-compose:
Команда:
```bash
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

##### Шаг 3. Локально отредактируйте файл nginx.conf
Локально отредактируйте файл `infra/nginx.conf` и в строке `server_name` впишите свой IP.

##### Шаг 4. Скопируйте подготовленные файлы из каталога infra:
Скопируйте подготовленные файлы `docker-compose.yaml` и `nginx/default.conf` из вашего проекта на сервер:
```bash
scp [файл, который хотите скопировать] [name@public_id:/путь к файлу на сервере/]
```

##### Шаг 5. Cоздайте .env файл:
На сервере создайте файл `nano .env` и заполните переменные окружения (или создайте этот файл локально и скопируйте файл по аналогии с предыдущим шагом):
```bash
SECRET_KEY=<SECRET_KEY>
DEBUG=<True/False>

DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

##### Шаг 6. Добавьте Secrets:
Для получения информации о деплое и тестировании flake8 в репозитории GitHub добавьте данные в `Actions secrets`:
```bash
TELEGRAM_TO=<ID своего телеграм-аккаунта>
TELEGRAM_TOKEN=<токен вашего бота>
```

##### Шаг 7. После успешного деплоя:
Зайдите на сервер и выполните команды:

###### Из директории backend:
```bash
sudo docker build -t dkr3d3/backend:v1.09.2022 .
```

###### Из директории infra:
```bash
sudo docker-compose up -d --build
```

Применяем миграции
```bash
sudo docker-compose exec backend python manage.py migrate --noinput
```

Подгружаем статику
```bash
sudo docker-compose exec backend python manage.py collectstatic --noinput 
```

Заполняем базу данных:
```bash
sudo docker-compose exec backend python manage.py load_data
```

###### Создаем суперпользователя Django:
```bash
sudo docker-compose exec backend python manage.py createsuperuser
```

##### Шаг 8. Проект запущен:
Проект будет доступен по вашему IP-адресу.

### Автор: 

Copyright © 2022 Dmitry Koroteev. All rights reserved.
