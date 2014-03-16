from django.core.exceptions import ObjectDoesNotExist
from django.template.defaultfilters import slugify
from django.db import models
from Forum.settings import User
# Create your models here.
class Forum(models.Model):
	def _get_main_forum(self):
		return self.subforum_set.get(local_id=0)

	local_id = models.IntegerField(unique=True)
	name = models.CharField(max_length=100) #name of the Forum instance (for listing and icons and stuff)
	main_forum = property(_get_main_forum)
	admin_permission = models.CharField(max_length=40, default="none")
	# Votes config
	allow_up_votes = models.BooleanField(default=True)
	allow_down_votes = models.BooleanField(default=True)
	# Display config
	posts_per_page = models.IntegerField(default=10)
	threads_per_page = models.IntegerField(default=20)
	forum_icon_normal = models.ImageField(upload_to="Forum/icons/", default="Forum/icons/default_normal.jpg")
	forum_icon_unread = models.ImageField(upload_to="Forum/icons/", default="Forum/icons/default_unread.jpg")
	forum_icon_pinned = models.ImageField(upload_to="Forum/icons/", default="Forum/icons/default_pinned.jpg")
	forum_icon_closed = models.ImageField(upload_to="Forum/icons/", default="Forum/icons/default_closed.jpg")

	def __unicode__(self):
		return str(self.local_id) + "-" + self.name

	def slug(self):
		return '-'+slugify(self.name)

class Subforum(models.Model):
	local_id = models.IntegerField()
	name = models.CharField(max_length=100)
	parent = models.ForeignKey('self', related_name="child_set", blank=True, null=True)
	forum = models.ForeignKey(Forum)
	view_permission = models.CharField(max_length=40, default="none")
	mod_permission = models.CharField(max_length=40, default="none") # or user has permission "Forum.global_moderator"
	create_thread_permission = models.CharField(max_length=40, default="none")
	reply_thread_permission = models.CharField(max_length=40, default="none")
	description = models.TextField()
	creator = models.ForeignKey(User, null=True)
	creation_datetime = models.DateTimeField(auto_now_add=True, null=True)

	class Meta:
		unique_together = ('local_id','forum')

	def __unicode__(self):
		return str(self.local_id) + "-" + self.name

	def slug(self):
		return '-'+slugify(self.name)

	def getPathAsList(self):
		l = []
		current_element = self
		while current_element != self.forum.main_forum:
			current_element = current_element.parent
			l.append(current_element)
		l.reverse()
		return l

	def getLastModifiedThread(self):
		return self.thread_set.all().order_by('-last_publication_datetime').first()

	def isVisited(self, user):
		if self.thread_set.count() == 0 or not user.is_authenticated():
			return True
		for thread in self.thread_set.all():
			if thread.isVisited(user):
				return True
		return False

class Thread(models.Model):
	local_id = models.IntegerField()
	name = models.CharField(max_length=100)
	parent = models.ForeignKey(Subforum)
	forum = models.ForeignKey(Forum)
	creator = models.ForeignKey(User)
	creation_datetime = models.DateTimeField(auto_now_add=True)
	last_publication_datetime = models.DateTimeField()
	hidden = models.BooleanField(default=False)
	closed = models.BooleanField(default=False)
	pinned = models.BooleanField(default=False)
	visit_counter = models.IntegerField(default=0)

	class Meta:
		unique_together = ('local_id','forum')

	def __unicode__(self):
		return str(self.local_id) + "-" + self.name

	def slug(self):
		return '-'+slugify(self.name)

	def getLastPublishedPost(self):
		return self.post_set.all().order_by('-publication_datetime').first()

	def isVisited(self, user):
		if not user.is_authenticated():
			return True
		try:
			dt = self.lastuservisit_set.get(user=user, thread=self).datetime
			if self.last_publication_datetime <= dt:
				return True
			else:
				return False
		except ObjectDoesNotExist:
			return False

class Poll(models.Model):
	question = models.CharField(max_length=200)
	thread = models.ForeignKey(Thread, unique=True)
	vote_count = models.IntegerField(default=0)

	def __unicode__(self):
		return self.thread.__unicode__()+"-"+self.question

class PollOption(models.Model):
	content = models.CharField(max_length=200)
	poll = models.ForeignKey(Poll, related_name="option_set")
	vote_count = models.IntegerField(default=0)

	def __unicode__(self):
		return self.content

class Post(models.Model):
	def _get_upvotes(self):
		return Vote.objects.filter(post=self, type="Up").count()
	def _get_downvotes(self):
		return Vote.objects.filter(post=self, type="Down").count()
	local_id = models.IntegerField()
	title = models.CharField(max_length=200, blank=True)
	forum = models.ForeignKey(Forum)
	thread = models.ForeignKey(Thread)
	content = models.TextField(max_length=1000)
	publisher = models.ForeignKey(User)
	publication_datetime = models.DateTimeField(auto_now_add=True)
	upvotes = property(_get_upvotes)
	downvotes = property(_get_downvotes)
	hidden = models.BooleanField(default=False)

	def __unicode__(self):
		return str(self.local_id) + "-" + self.title

	def slug(self):
		return '-'+slugify(self.title)

	def score(self):
		return self.upvotes-self.downvotes

	class Meta:
		unique_together = ('local_id','forum')

class PostReported(models.Model):
	post = models.ForeignKey(Post)
	user = models.ForeignKey(User, related_name="+")
	reason = models.CharField(max_length=500)
	datetime = models.DateTimeField(auto_now_add=True)
	class Meta:
		unique_together = ('post','user', 'datetime')
		verbose_name_plural = "Posts Reported"
	def __unicode__(self):
		return self.post.__unicode__()

class PostEdited(models.Model):
	post = models.ForeignKey(Post)
	user = models.ForeignKey(User, related_name="+")
	datetime = models.DateTimeField(auto_now_add=True)
	reason = models.CharField(max_length=500)
	old_title = models.CharField(max_length=200, blank=True)
	new_title = models.CharField(max_length=200, blank=True)
	old_content = models.TextField()
	new_content = models.TextField()
	user_is_moderator = models.BooleanField(default=False)
	user_is_administrator = models.BooleanField(default=False)
	class Meta:
		verbose_name_plural = "Posts Edited"

class LastUserVisit(models.Model):
	thread = models.ForeignKey(Thread)
	datetime = models.DateTimeField()
	user = models.ForeignKey(User)

class Quote(models.Model):
	user = models.ForeignKey(User)
	post = models.ForeignKey(Post)
	thread = models.ForeignKey(Thread)
	class Meta:
		unique_together = ('user','post')

Vote_types = (("Up","Up"),("Down","Down"))
class Vote(models.Model):
	user = models.ForeignKey(User)
	post = models.ForeignKey(Post)
	type = models.CharField(max_length=4, choices=Vote_types)
	class Meta:
		unique_together = ('user','post')