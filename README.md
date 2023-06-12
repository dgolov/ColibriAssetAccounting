# Учет активов ООО Колибри

Приложение учета активов, отображения состояние, местанахождения, истории активов для ООО Колибри

Opensource code

Переиспользование кода возможно без согласия автора

## Start application

```shell
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Create user

```shell
python manage.py createsuperuser
```

## Start application via docker

```shell
docker-compose up --build -d
```

### Create user via docker

```shell
docker exec -it colibriassetaccounting_web_1 bash
python manage.py createsuperuser
```

### Config example (Add to .env file)

```
SECRET_KEY=django-SECRET_KEY
DEBUG=0
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=some_password
ALLOWED_HOSTS=0.0.0.0,127.0.0.1
```

## Used technologies

- Python3
- Django3
- Pandas
- Redis
- HTML5
- CSS3
- Bootstrap
