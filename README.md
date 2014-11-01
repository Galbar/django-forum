django-forum
============

A forum app for django-1.7.

TODO: Administration pannel.

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

Test Project
============
The Test Project comes with everything set up and two users: admin and guest (being the password the same than the username). So you can try it.
