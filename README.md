# Django Async Redis Websocket Sessions

Created on 7 October 2020

Created by: Andrew Chen Wang

I honestly should be studying for my midterms
which are in... 5 hours. But I was too curious
as to how Django Async Redis can work with sessions.
This repository demonstrates how to use sessions view-wise
and websocket wise (using native Django 3.0 websockets).

TL;DR It can't for all standard apps like the admin.
The problem lies in the fact that Django has not
implemented the async methods for `django.contrib.auth`
and other areas, so the methods are simply not called.

In the session branch of django-async-redis, you'll see
a locally tested but not unit tested code for sessions.
If you try to login to the admin, you won't be given
the admin page. Instead, even though the session is set,
you aren't being authenticated and the session key is
not saved since the contrib apps are not designed for
async yet.

---
### Instructions

Create an admin user with createsuperuser. Login
with the admin. Then go to https://localhost:8000

You should see that the socket connected and in the
console you'll find the saved dict that was encoded
in to the cache.
