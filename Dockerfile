# pull official base image
FROM python:3.10.4

WORKDIR /home/app/web

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update -y && apt-get -y install postgresql gcc python3-dev musl-dev redis-server

COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt && mkdir /home/app/web/static

COPY . .

RUN mkdir ./logs/

RUN python manage.py collectstatic --noinput
RUN chmod +x entrypoint.sh

ENTRYPOINT ["/home/app/web/entrypoint.sh"]