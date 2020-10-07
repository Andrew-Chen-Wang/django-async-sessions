# Django Async Redis Websocket Sessions

Created on 7 October 2020

Created by: Andrew Chen Wang

I honestly should be studying for my midterms
which are in... 5 hours. But I was too curious
as to how Django Async Redis can work with sessions.
This repository demonstrates how to use sessions view-wise
and websocket wise (using native Django 3.0 websockets).

TL;DR It can't. I'm currently working on
[ticket 32076](https://code.djangoproject.com/ticket/32076)
which will finally introduce the async cache methods.
That means you can finally use django.core.cache... almost.

The problem I immediately saw before I even created 
django-async-redis was that on each request, the cache
must close. But Django signals is still synchronous only.

Additionally, the cache session backend that django-redis
uses is the default because the cache backend for that is
set to use the synchronous methods of CacheHandler. Since
my ticket is the first to introduce async cache, there are
no methods for sessions to work properly.

I've implemented a class in `public/websockets/index.py`
that is basically ASGIRequest remade into Websocket stuff
so that I could easily access the headers and cookies.
Finally, I check the cache and voila you find the session
in the cache.

---
### Instructions

Create an admin user with createsuperuser. Login
with the admin. Then go to https://localhost:8000

You should see that the socket connected and in the
console you'll find the saved dict that was encoded
in to the cache.
