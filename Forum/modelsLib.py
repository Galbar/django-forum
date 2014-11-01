from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from Forum.models import *
from datetime import timedelta
from django.http import Http404

def set_visit(thread, user):
	if not user.is_authenticated():
		return
	try:
		l = LastUserVisit.objects.get(user=user, thread=thread)
		l.datetime = timezone.now()
		l.save()
	except ObjectDoesNotExist:
		l = LastUserVisit(user=user, thread=thread, datetime=timezone.now())
		l.save()

def check_user_is_spamming(user):
	delta_time = timezone.now()-timedelta(seconds=3)
	try:
		last_post_datetime = Post.objects.filter(publisher=user).order_by("-publication_datetime").first()
		if last_post_datetime and (last_post_datetime.publication_datetime >= delta_time):
			raise Http404
	except ObjectDoesNotExist:
		pass
	try:
		last_edition_datetime = PostEdited.objects.filter(user=user).order_by("-datetime").first()
		if last_edition_datetime and (last_edition_datetime.datetime >= delta_time):
			raise Http404
	except ObjectDoesNotExist:
		pass
	try:
		last_report_datetime = PostReported.objects.filter(user=user).order_by("-datetime").first()
		if last_report_datetime and (last_report_datetime.datetime >= delta_time):
			raise Http404
	except ObjectDoesNotExist:
		pass
	try:
		last_subforum_datetime = Subforum.objects.filter(creator=user).order_by("-creation_datetime").first()
		if last_subforum_datetime and (last_subforum_datetime.creation_datetime >= delta_time):
			raise Http404
	except ObjectDoesNotExist:
		pass
	return