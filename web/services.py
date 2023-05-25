from django.conf import settings

import logging
import redis


logger = logging.getLogger('main')


def connect_to_redis():
    logger.info("Try to connect redis")
    return redis.StrictRedis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        encoding='utf-8'
    )
