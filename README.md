# Учет активов ООО Колибри

Приложение учета активов, отображения состояния, местанахождения, истории активов для ООО Колибри

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
UPLOAD_FORMAT=Наименование,Метоположение,Стоимость,Год закупки,Статус,Состояние
UPLOAD_FIELDS=name,location,price,year_of_purchase,status,state
LOGGING_FORMAT=%(asctime)s - %(levelname)-8s %(message)s
LOGGING_PATH=./logs/app.log
LOGGING_LEVEL=INFO
LOGGING_SERVER_PATH=/var/log/app.log
```

### Config db example (.env.db file)

```
DB_DATABASE=dbname
POSTGRES_USER=dbuser
POSTGRES_PASSWORD=dbpassword
```

## Used technologies

- Python3
- Django3
- Pandas
- Redis
- HTML5
- CSS3
- Bootstrap
