![workflow](https://github.com/Sharumario/foodgram-project-react/actions/workflows/
foodgram_workflows.yml/badge.svg)

## Проект доступен по [адресу]

Описание проекта:

Проект Foodgram позволяет публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Установка:
- Скачать репрозиторий:
	- > git clone [git@github.com:Sharumario/foodgram-project-react.git](https://github.com/Sharumario/foodgram-project-react.git)
- Перейти в директорию infra.
	- > cd foodgram-project-react/infra
- Создать .env файл внутри и заполнить данные:
	- > DB_ENGINE=django.db.backends.postgresql 
	- > DB_NAME=postgres 
	- > POSTGRES_USER=postgres 
	- > POSTGRES_PASSWORD=12345678 
	- > DB_HOST=db 
	- > DB_PORT=5432 
	- > SECRET_KEY = '************' # Здесь нужен ваш ключь
- Создать образы докера:
	- > docker-compose up -d --build
- Сделать миграции, загрузить ингридиенты в БД и загрузить статику: 
	- > docker-compose exec backend python manage.py migrate 
	- > docker-compose exec backend python manage.py update
	- > docker-compose exec backend python manage.py collectstatic --no-input

	Создать суперпользователя:
	- - > docker-compose exec backend python manage.py createsuperuser 

## Рабочие эндпоинты
 - > http://localhost/admin/ - страница админа
 - > http://localhost/signin/ - страница приложения