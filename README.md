# Foodgram

### Описание 
Foodgram - это интернет-сервис, который позволяет пользователям делиться рецептами.

### Функционал Foodgram
- Просмотр рецептов;
- Добавление, обновление и удаление рецептов;
- Добавление рецептов в список избранного;
- Добавление рецептов в корзину покупок, получение списка покупок.
- Подписка на авторов рецептов.
- Фильтрация рецептов по тегам.
- Регистрация для получения полного доступа к возможностям Foodgram.

### Технологии
#### Backend
- Python 3.9
- Django 3.2
- Django REST Framework 3.12.4
- Подробную информацию о зависимостях можно найти в файле `requirements.txt`
#### Frontend
- React

### Установка и запуск проекта:
- Установите `docker`
    ```
    sudo apt update
    sudo apt install curl
    curl -fSL https://get.docker.com -o get-docker.sh
    sudo sh ./get-docker.sh
    sudo apt-get install docker-compose-plugin
    ```
- Установите `sudo apt install nginx` и настройте веб-сервер, пример конфигурации:
    ```
    server {
        server_name foodgram.dev;
        location / {
        proxy_pass http://127.0.0.1:8000;
        }
    }
    ```
- В домашней директории пользователя создайте каталог `foodgram`
- Создайте в `~/foodgram` файл .env и запишите в него необходимые переменные окружения:
    - `POSTGRES_USER=foodgram_user`
    - `POSTGRES_PASSWORD=foodgram_password`
    - `POSTGRES_DB=foodgram`
    - `DB_HOST=db`
    - `DB_PORT=5432`
    - `SECRET_KEY=Super_secret_key`
- Скопируйте в `~/foodgram` файл `docker-compose.production.yml`
- Запустите приложение в контейнерах
    ```
    sudo docker compose -f docker-compose.production.yml up -d
    ```

### Авторы
Денис Третьяков

## Лицензия

[MIT License](https://opensource.org/licenses/MIT)