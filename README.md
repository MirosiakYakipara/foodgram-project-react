# О проекте
Проект Foodgram, «Продуктовый помощник». На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин могут скачать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.
***
## Выполнено при помощи:
* [Django 2.2.19](https://www.djangoproject.com/)
* [Python 3.7.9](https://www.python.org/downloads/release/python-379/)
* [Rest Framefork](https://www.django-rest-framework.org/)
* [JWT](https://jwt.io/)
* [Docker](https://www.docker.com/)
* [nginx](https://nginx.org/ru/)
* ![workflow](https://github.com/MirosiakYakipara/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)
***
## Как запустить проект
Чтобы запустить проект вам нужно склонировать репозиторий и установить в нем все необходиое.
### Клонирование и установка
1. Склонируйте репозиторий и перейдите в папку с *docker-compose*:

    * Клонирование репозитория:
    ```sh
    git clone git@github.com:MirosiakYakipara/foodgram-project-react.git
    ```
    * Перейдите в папку с проектом:
    ```sh
    cd foodgram-project-react/
    ```
    * Перейдите в папку с *docker-compose.yaml*:
    ```sh
   cd infra/
    ```

2. Создайте файл "*.env*" с переменными окружения для работы с базой данных:

    * Создайте файл "*.env*":
    ```sh
    touch .env
    ```
    * Заполните его переменными окружения для работы с базой данных:
    ```sh
    nano .env
    ```
    Шаблон наполнения "*.env*":
    ***
    DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
    DB_NAME=postgres # имя базы данных
    POSTGRES_USER=postgres # логин для подключения к базе данных
    POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
    DB_HOST=db # название сервиса (контейнера)
    DB_PORT=5432 # порт для подключения к БД
    ***

3. Запустите *docker-compose*: 

    * Запуск *docker-compose*:
    ```sh
    docker-compose up
    ```
    
4. Выполните миграции:

    * Создайте миграции: 
    ```sh
    docker-compose exec backend python manage.py makemigrations
    ```

    * Выполните миграции: 
    ```sh
    docker-compose exec backend python manage.py migrate
    ```
    
5. Создайте суперпользователя:

    * Создайте суперпользвоателя:
    ```sh
    docker-compose exec backend python manage.py createsuperuser
    ```
    
6. Загрузите статику: 

    * Загрузите статику:
    ```sh
    docker-compose exec backend python manage.py collectstatic --no-input
    ```

7. Заполните базу данных:

    * Заполните базу данных: 
    ```sh
    docker-compose exec backend python manage.py loaddata fixtures.json
    ```
***
## Регистрация пользователей
Для того чтобы использовать все возможности сервиса вам нужно зарегестрироваться и получить токен, для работы с токеном у нас есть несколько ссылок:

1. Зарегистрировать пользователя можно по ссылке, сделав POST- запрос с вашими username, email, first_name, last_name, password. Использовать имя "me" в качестве username запрещено:

```
http://localhost/api/users/
```

* Пример POST-запроса:
```json
{
  "email": "vpupkin@yandex.ru",
  "username": "vasya.pupkin",
  "first_name": "Вася",
  "last_name": "Пупкин",
  "password": "Qwerty123"
}
```

* Пример ответа:
```json
{
  "email": "vpupkin@yandex.ru",
  "id": 0,
  "username": "vasya.pupkin",
  "first_name": "Вася",
  "last_name": "Пупкин"
}
```

2. Получить токен можно по ссылке, сделав POST- запрос с вашим email и password:

```
http://localhost/api/auth/token/login/
```

* Пример POST-запроса:
```json
{
  "password": "string",
  "email": "string"
}
```

* Пример ответа:
```json
{
  "auth_token": "string"
}
```

3. Удалить токен можно по ссылке, сделав POST- будучи авторизованным:

```
http://localhost/api/auth/token/logout/
```

* Пример POST-запроса:
```json
{}
```

* Пример ответа:
```json
{}
```
***
## Пользовательские роли
****Аноним**** — может cоздать аккаунт, просматривать рецепты на главной, просматривать отдельные страницы рецептов, просматривать страницы пользователей, фильтровать рецепты по тегам.

****Аутентифицированный пользователь (user)**** — может входить в систему под своим логином и паролем, выходить из системы (разлогиниваться), менять свой пароль, создавать/редактировать/удалять собственные рецепты, просматривать рецепты на главной, просматривать страницы пользователей, просматривать отдельные страницы рецептов, фильтровать рецепты по тегам, работать с персональным списком избранного: добавлять в него рецепты или удалять их, просматривать свою страницу избранных рецептов, работать с персональным списком покупок: добавлять/удалять любые рецепты, выгружать файл с количеством необходимых ингридиентов для рецептов из списка покупок, подписываться на публикации авторов рецептов и отменять подписку, просматривать свою страницу подписок.

****Администратор**** — бладает всеми правами авторизованного пользователя. Плюс к этому он может: изменять пароль любого пользователя, создавать/блокировать/удалять аккаунты пользователей, редактировать/удалять любые рецепты, добавлять/удалять/редактировать ингредиенты, добавлять/удалять/редактировать теги.
***
### Работа с рецептами

1. ***GET-запрос:*** Получить список всех рецептов, доступна фильтрация по избранному, автору, списку покупок и тегам:

```
http://localhost/api/recipes/
```

* Пример ответа:
```json
{
  "count": 123,
  "next": "http://foodgram.example.org/api/recipes/?page=4",
  "previous": "http://foodgram.example.org/api/recipes/?page=2",
  "results": [
    {
      "id": 0,
      "tags": [
        {
          "id": 0,
          "name": "Завтрак",
          "color": "#E26C2D",
          "slug": "breakfast"
        }
      ],
      "author": {
        "email": "user@example.com",
        "id": 0,
        "username": "string",
        "first_name": "Вася",
        "last_name": "Пупкин",
        "is_subscribed": false
      },
      "ingredients": [
        {
          "id": 0,
          "name": "Картофель отварной",
          "measurement_unit": "г",
          "amount": 1
        }
      ],
      "is_favorited": true,
      "is_in_shopping_cart": true,
      "name": "string",
      "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
      "text": "string",
      "cooking_time": 1
    }
  ]
}
```

2. ***POST-запрос:*** Создать рецепт. Минимум 1 Тег, время приготовления минимум 1:

```
http://localhost/api/v1/categories/
```
    
* Пример POST-запроса:
```json
{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```

* Пример ответа:
```json
{
  "id": 0,
  "tags": [
    {
      "id": 0,
      "name": "Завтрак",
      "color": "#E26C2D",
      "slug": "breakfast"
    }
  ],
  "author": {
    "email": "user@example.com",
    "id": 0,
    "username": "string",
    "first_name": "Вася",
    "last_name": "Пупкин",
    "is_subscribed": false
  },
  "ingredients": [
    {
      "id": 0,
      "name": "Картофель отварной",
      "measurement_unit": "г",
      "amount": 1
    }
  ],
  "is_favorited": true,
  "is_in_shopping_cart": true,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
  "text": "string",
  "cooking_time": 1
}
```

3. ***GET-запрос:*** Получение рецепта по id:

```
http://localhost/api/recipes/{id}/
```

* Пример ответа:
```json
{
  "id": 0,
  "tags": [
    {
      "id": 0,
      "name": "Завтрак",
      "color": "#E26C2D",
      "slug": "breakfast"
    }
  ],
  "author": {
    "email": "user@example.com",
    "id": 0,
    "username": "string",
    "first_name": "Вася",
    "last_name": "Пупкин",
    "is_subscribed": false
  },
  "ingredients": [
    {
      "id": 0,
      "name": "Картофель отварной",
      "measurement_unit": "г",
      "amount": 1
    }
  ],
  "is_favorited": true,
  "is_in_shopping_cart": true,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
  "text": "string",
  "cooking_time": 1
}
```
4. ***PATCH-запрос:*** Обновление рецепта по id. Минимум 1 Тег, время приготовления минимум 1:

```
http://localhost/api/recipes/{id}/
```

* Пример PATCH-запроса:
```json
{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```

* Пример ответа:
```
{
  "id": 0,
  "tags": [
    {
      "id": 0,
      "name": "Завтрак",
      "color": "#E26C2D",
      "slug": "breakfast"
    }
  ],
  "author": {
    "email": "user@example.com",
    "id": 0,
    "username": "string",
    "first_name": "Вася",
    "last_name": "Пупкин",
    "is_subscribed": false
  },
  "ingredients": [
    {
      "id": 0,
      "name": "Картофель отварной",
      "measurement_unit": "г",
      "amount": 1
    }
  ],
  "is_favorited": true,
  "is_in_shopping_cart": true,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
  "text": "string",
  "cooking_time": 1
}
```

5. ***DELETE-запрос:*** Удаление рецепта по id:

```
http://localhost/api/recipes/{id}/
```

* Пример ответа:
```json
{}
```
***
### Работа со списком покупок.

1. ***GET-запрос:*** Скачать список покупок:

```
http://localhost/api/recipes/download_shopping_cart/
```

* Пример ответа:
```json
{}
```

2. ***POST-запрос:*** Добавить рецепт в список покупок по id:

```
http://localhost/api/recipes/{id}/shopping_cart/
```
    
* Пример POST-запроса:
```json
{}
```

* Пример ответа:
```json
{
  "id": 0,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
  "cooking_time": 1
}
```

3. ***DELETE-запрос:*** Удалить рецепт из списка покупок по id:

```
http://localhost/api/recipes/{id}/shopping_cart/
```

* Пример ответа:
```json
{}
```
***
### Работа с избранным.

1. ***POST-запрос:*** Добавить рецепт в избранное по id:

```
http://localhost/api/v1/titles/
```

* Пример POST-запроса:
```json
{}
```

* Пример ответа:
```json
{
  "id": 0,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
  "cooking_time": 1
}
```

2. ***DELETE-запрос:*** Удалить рецепт из избранного по id:

```
http://localhost/api/recipes/{id}/favorite/
```

* Пример ответа:
```json
{}
```
***
### Работа с подписками.

1. ***GET-запрос:*** Возвращает пользователей, на которых подписан текущий пользователь. В выдачу добавляются рецепты:

```
http://localhost/api/users/subscriptions/
```

* Пример ответа:
```json
{
  "count": 123,
  "next": "http://foodgram.example.org/api/users/subscriptions/?page=4",
  "previous": "http://foodgram.example.org/api/users/subscriptions/?page=2",
  "results": [
    {
      "email": "user@example.com",
      "id": 0,
      "username": "string",
      "first_name": "Вася",
      "last_name": "Пупкин",
      "is_subscribed": true,
      "recipes": [
        {
          "id": 0,
          "name": "string",
          "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
          "cooking_time": 1
        }
      ],
      "recipes_count": 0
    }
  ]
}
```

2. ***POST-запрос:*** Подписаться на пользователя по id:

```
http://localhost/api/users/{id}/subscribe/
```

* Пример POST-запроса:
```json
{}
```

* Пример ответа:
```json
{
  "email": "user@example.com",
  "id": 0,
  "username": "string",
  "first_name": "Вася",
  "last_name": "Пупкин",
  "is_subscribed": true,
  "recipes": [
    {
      "id": 0,
      "name": "string",
      "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
      "cooking_time": 1
    }
  ],
  "recipes_count": 0
}
```

3. ***DELETE-запрос:*** УОтписаться от пользователя по id:

```
http://localhost/api/users/{id}/subscribe/
```

* Пример ответа:
```json
{}
```
***
### Работа с ингредиентами.

1. ***GET-запрос:*** Получить список ингредиентов с возможностью поиска по имени.:

```
http://localhost/api/ingredients/
```

* Пример ответа:
```json
[
  {
    "id": 0,
    "name": "Капуста",
    "measurement_unit": "кг"
  }
]
```

2. ***GET-запрос:*** Получение ингредиента по id:

```
http://localhost/api/ingredients/{id}/
```

* Пример ответа:
{
  "id": 0,
  "name": "Капуста",
  "measurement_unit": "кг"
}
```

### Работа с пользователями

1. ***GET-запрос:*** Получить список всех пользователей:

```
http://localhost/api/users/
```

* Пример ответа:
```json
{
  "count": 123,
  "next": "http://foodgram.example.org/api/users/?page=4",
  "previous": "http://foodgram.example.org/api/users/?page=2",
  "results": [
    {
      "email": "user@example.com",
      "id": 0,
      "username": "string",
      "first_name": "Вася",
      "last_name": "Пупкин",
      "is_subscribed": false
    }
  ]
}
```

2. ***GET-запрос:*** Получить пользователя по id:

```
http://localhost/api/users/{id}/
```

* Пример ответа:
```json
{
  "email": "user@example.com",
  "id": 0,
  "username": "string",
  "first_name": "Вася",
  "last_name": "Пупкин",
  "is_subscribed": false
}
```

3. ***POST-запрос:*** Изменить пароль пользователя, изменить можно только свой пароль:

```
http://localhost/api/users/set_password/
```

* Пример POST-запроса:
```json
{
  "new_password": "string",
  "current_password": "string"
}
```

* Пример ответа:
```json
{}
```

4. ***GET-запрос:*** Получить данные своей учетной записи:

```
http://localhost/api/users/me/
```

* Пример ответа:
```json
{
  "email": "user@example.com",
  "id": 0,
  "username": "string",
  "first_name": "Вася",
  "last_name": "Пупкин",
  "is_subscribed": false
}
```
***
## Контакты

Никита Зотов - nz030432@gmail.com

IP для подключения к API: 158.160.18.130

Ссылка на спецификацию API: [http://158.160.18.130/api/docs/redoc.html](http://158.160.18.130/api/docs/redoc.html)

Ссылка на проект: [http://158.160.18.130](http://158.160.18.130)
