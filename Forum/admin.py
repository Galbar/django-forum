from django.contrib import admin
from django.core.urlresolvers import reverse
from Forum.models import Subforum, Post, PostReported, PostEdited, Thread, Poll, PollOption, Forum
from django.utils.safestring import mark_safe
from django.contrib.auth.models import Permission
from Forum.forms import FormForum, FormSubforum

# Register your models here.
class ForumAdmin(admin.ModelAdmin):
	form = FormForum

	def unique_id(self, instance):
		return mark_safe(str(instance.id))

	def admin_main_forum(self, instance):
		url = reverse('admin:%s_%s_change' % (
			instance.main_forum._meta.app_label,
			instance.main_forum._meta.module_name), args=[instance.main_forum.id]
		)
		return mark_safe(u'<a href="{u}">'.format(u=url)+instance.main_forum.__unicode__()+'</a>')

"""
	fieldsets = [
	('General',         {'fields':[('name','unique_id'),('admin_main_forum')]}),
	('Permissions',     {'fields':['admin_permission']}),
	('Icons',           {'fields':['forum_icon_normal', 'forum_icon_unread', 'forum_icon_pinned', 'forum_icon_closed']}),
	]

	readonly_fields = ('admin_main_forum','unique_id',)
"""

class PostEditedInline(admin.StackedInline):
	model = PostEdited
	ordering = ("datetime",)
	extra = 0
	can_delete = False
	
	readonly_fields = ('user','datetime','reason','old_content','new_content')


class PostAdmin(admin.ModelAdmin):
	list_display = ('__unicode__', 'local_id', 'admin_thread', 'publication_datetime')
	def unique_id(self, instance):
		return mark_safe(str(instance.id))

	def publisher_profile_link(self, instance):
		url = reverse('admin:%s_%s_change' % (
			instance.publisher._meta.app_label,
			instance.publisher._meta.module_name), args=[instance.publisher.id]
		)
		return mark_safe(u'<a href="{u}">'.format(u=url)+instance.publisher.__unicode__()+'</a>')

	def admin_thread(self, instance):
		url = reverse('admin:%s_%s_change' % (
			instance.thread._meta.app_label,
			instance.thread._meta.module_name), args=[instance.thread.id]
		)
		return mark_safe(u'<a href="{u}">'.format(u=url)+instance.thread.__unicode__()+'</a>')

	fieldsets = [
	('General',         {'fields':[('title','local_id'),('thread','admin_thread', 'forum'),('publisher','publisher_profile_link','publication_datetime'),'content',('upvotes','downvotes'),'hidden']}),
	#('Icons',           {'fields':['forum_icon_normal', 'forum_icon_unread', 'forum_icon_pinned', 'forum_icon_closed']}),
	]
	inlines = [PostEditedInline]
	def get_readonly_fields(self, request, obj=None):
		readonly_fields = list(self.readonly_fields)
		if obj:
			readonly_fields.extend(['thread','publisher','content'])
		return readonly_fields
	readonly_fields = ('admin_thread','local_id','forum','publication_datetime','publisher_profile_link','upvotes','downvotes')

class PollOptionInline(admin.TabularInline):
	model = PollOption
	extra = 2

class PollAdmin(admin.ModelAdmin):
	fieldsets = [
		(None,    {'fields': ['thread', 'question']}),
		('Votes', {'fields': ['vote_count'], 'classes': ['collapse']}),
	]
	inlines = [PollOptionInline]
	list_display = ('question', 'thread')

class SubforumInline(admin.TabularInline):
	model = Subforum
	fk_name = "parent"
	extra = 0
	def admin_link(self, instance):
		url = reverse('admin:%s_%s_change' % (
			instance._meta.app_label,
			instance._meta.module_name), args=[instance.id]
		)
		return mark_safe(u'<a href="{u}">'.format(u=url)+instance.__unicode__()+'</a>')
	fields =('admin_link',)
	readonly_fields = ('admin_link',)
	can_delete = False

	def has_add_permission(self, request):
		return False

class ThreadInline(admin.TabularInline):
	model = Thread
	extra = 0
	def admin_link(self, instance):
		url = reverse('admin:%s_%s_change' % (
			instance._meta.app_label,
			instance._meta.module_name), args=[instance.id]
		)
		return mark_safe(u'<a href="{u}">'.format(u=url)+instance.__unicode__()+'</a>')
	fields =('admin_link',)
	readonly_fields = ('admin_link',)
	can_delete = False
	
	def has_add_permission(self, request):
		return False

class SubforumAdmin(admin.ModelAdmin):
	form = FormSubforum
	list_display = ('__unicode__', 'forum' , 'local_id', 'parent_name', 'description')
	inlines = [SubforumInline, ThreadInline]
	def parent_name(self, instance):
		if instance.parent == None:
			return "------"
		else:
			return instance.parent.name

	def unique_id(self, instance):
		return mark_safe(str(instance.id))

	def parent_admin_link(self, instance):
		url = reverse('admin:%s_%s_change' % (
			instance.parent._meta.app_label,
			instance.parent._meta.module_name), args=[instance.parent.id]
		)
		return mark_safe(u'<a href="{u}">'.format(u=url)+instance.parent.__unicode__()+'</a>')
	fieldsets = [
	('General',         {'fields':[('name','forum','local_id'),'description']}),
	('Parent',          {'fields':[('parent','parent_admin_link')]}),
	('Permissions',     {'fields':['view_permission','mod_permission','create_thread_permission','reply_thread_permission'], 'classes': ['collapse']}),
	]
	readonly_fields = ('parent_admin_link', )

class PostInline(admin.TabularInline):
	model = Post
	ordering = ("publication_datetime",)
	extra = 0
	def admin_link(self, instance):
		url = reverse('admin:%s_%s_change' % (
			instance._meta.app_label,
			instance._meta.module_name), args=[instance.id]
		)
		return mark_safe(u'<a href="{u}">'.format(u=url)+instance.__unicode__()+'</a>')
	fields =('admin_link','publisher','publication_datetime','hidden')
	readonly_fields = ('admin_link','publisher','publication_datetime')
	can_delete = False
	
	def has_add_permission(self, request):
		return False

class ThreadAdmin(admin.ModelAdmin):
	list_display = ('__unicode__', 'parent_name', 'local_id')
	inlines = []
	def parent_name(self, instance):
		if instance.parent == None:
			return "------"
		else:
			return instance.parent.name

	def unique_id(self, instance):
		return mark_safe(str(instance.id))

	def parent_admin_link(self, instance):
		url = reverse('admin:%s_%s_change' % (
			instance.parent._meta.app_label,
			instance.parent._meta.module_name), args=[instance.parent.id]
		)
		return mark_safe(u'<a href="{u}">'.format(u=url)+instance.parent.__unicode__()+'</a>')

	def creator_user(self, instance):
		url = reverse('admin:%s_%s_change' % (
			instance.creator._meta.app_label,
			instance.creator._meta.module_name), args=[instance.creator.id]
		)
		return mark_safe(u'<a href="{u}">'.format(u=url)+instance.creator.__unicode__()+'</a>')

	fieldsets = [
	('General',         {'fields':[('name','local_id'),('creator','creator_user','creation_datetime'),'visit_counter']}),
	('Parent',          {'fields':[('parent','parent_admin_link', 'forum')]}),
	('Settings',     {'fields':[('hidden', 'closed', 'pinned')], 'classes': ['collapse']}),
	]
	readonly_fields = ('parent_admin_link', 'creator_user', 'creation_datetime','visit_counter')
	inlines = [PostInline]

class PostReportedAdmin(admin.ModelAdmin):
	def post_link(self, instance):
		url = reverse('admin:%s_%s_change' % (
			instance.post._meta.app_label,
			instance.post._meta.module_name), args=[instance.post.id]
		)
		return mark_safe(u'<a href="{u}">'.format(u=url)+instance.post.__unicode__()+'</a>')

	def user_profile(self, instance):
		url = reverse('admin:%s_%s_change' % (
			instance.user._meta.app_label,
			instance.user._meta.module_name), args=[instance.user.id]
		)
		return mark_safe(u'<a href="{u}">'.format(u=url)+instance.user.__unicode__()+'</a>')
	fields = ('post_link','user_profile','reason')
	readonly_fields = ('post_link','user_profile','reason')

class PermAdmin(admin.ModelAdmin):
	pass

admin.site.register(Subforum, SubforumAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(PostReported, PostReportedAdmin)
admin.site.register(Thread, ThreadAdmin)
admin.site.register(Poll, PollAdmin)
admin.site.register(Forum, ForumAdmin)
admin.site.register(Permission, PermAdmin)