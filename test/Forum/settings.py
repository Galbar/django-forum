"""
General settings for Forum App
==============================

The Forum App suposes the User model is the django default one.
If you are using a custom User model, set your model in this file (and custom forum templates
if you wish to use that extra data on the forum display. p.e. avatar image, etc).
Your User model must use the django default permission system (at least for the forum permissions).
"""
# User model
from django.contrib.auth.models import User as def_User
User = def_User

# Templates
MAIN_FORUM_TEMPLATE = 'Forum/view_forum.html'
SUBFORUM_TEMPLATE = 'Forum/view_forum.html'
THREAD_TEMPLATE = 'Forum/view_thread.html'
CANT_VIEW_CONTENT = 'Forum/cant_view.html'

"""
Template context variables:
  form: An instance of the form to be prompted
  page_title: Title of the page
  title: Title of the form
  submit_btn_text: Text on the submit form button
"""
FORM_TEMPLATE = 'Forum/form.html'
