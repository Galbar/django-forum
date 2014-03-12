django-forum
============

A forum app for django.

Currently in development, not recommended for production.

Features
========
* Multiple forum instances, completetly independant, in the same site.

How to use
==========
After adding the app to the project and to the list of installed apps and doing syncdb, do the following:
```
python manage.py forumapp_init
```
This command will initialize the forum app.
