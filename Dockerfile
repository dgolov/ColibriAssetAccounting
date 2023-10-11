# Stage 1: build app and dependencies
FROM python:3.10.4 AS builder

WORKDIR /home/app/web

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update -y && apt-get -y install postgresql gcc python3-dev musl-dev redis-server

COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip &&
    pip install -r requirements.txt &&
    mkdir /home/app/web/static

COPY . .

RUN mkdir ./logs/

# Stage 2: create final image
FROM python:3.10.4 AS builder

WORKDIR /home/app/web

COPY --from=builder /root/.local /root/.local

ENV PATH=/root/.local/bin:$PATH

COPY --from=builder /home/app/web .

RUN python manage.py collectstatic --noinput
RUN chmod +x entrypoint.sh

ENTRYPOINT ["/home/app/web/entrypoint.sh"]