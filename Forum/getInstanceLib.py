from django.core.exceptions import ObjectDoesNotExist
from Forum.models import *

def get_forum_instance(id):
	try:
		return Forum.objects.get(local_id=id)
	except ObjectDoesNotExist:
		return None

def get_subforum_instance(forum, id):
	try:
		return Subforum.objects.get(forum=forum, local_id=id)
	except ObjectDoesNotExist:
		return None

def get_thread_instance(forum, id):
	try:
		return Thread.objects.get(forum=forum, local_id=id)
	except ObjectDoesNotExist:
		return None

def get_post_instance(forum, id):
	try:
		return Post.objects.get(forum=forum, local_id=id)
	except ObjectDoesNotExist:
		return None

def get_last_visit_instance(user, thread):
	try:
		return LastUserVisit.objects.get(user=user, thread=thread)
	except ObjectDoesNotExist:
		return None

def get_quote_instance(user, post):
	try:
		return Quote.objects.get(user=user, post=post)
	except ObjectDoesNotExist:
		return None

def get_vote_instance(user, post):
	try:
		return Vote.objects.get(user=user, post=post)
	except ObjectDoesNotExist:
		return None