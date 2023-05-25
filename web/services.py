from django.conf import settings

import redis


def connect_to_redis():
    return redis.StrictRedis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        encoding='utf-8'
    )
