from asgiref.sync import async_to_sync
from django.core.signals import request_finished
from django.core.cache import caches


async def _close_async_caches():
    for cache in caches.all():
        await cache.close_async()


def close_async_caches(**kwargs):
    async_to_sync(_close_async_caches)


request_finished.connect(close_async_caches)
