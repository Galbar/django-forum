# -*- coding: utf-8 -*-
import json
from django.http import Http404, HttpResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as lgout, authenticate, login as lgin
from django.template.defaultfilters import slugify
from django.shortcuts import render, redirect
from datetime import datetime
from Forum.models import *
from Forum.settings import *
from Forum.forms import *
from Forum.lib import *
from django.template import RequestContext
from math import ceil

# Create your views here.
def login(request, forum_id, template=FORM_TEMPLATE):
	form = None
	if request.method == 'POST':
		form = FormUserLogin(request.POST)
		if form.is_valid():
			user = authenticate(username=form.data['username'], password=form.data['password'])
			if user:
				lgin(request, user)
				forum = get_forum_instance(forum_id)
				if forum:
					return redirect('base_forum', forum_id=forum.local_id)
				else:
					raise Http404
	if not form:
		form = FormUserLogin()
	c = RequestContext(request, {
							'forum_id':forum_id,
							'form': form,
							'page_title': 'Login',
							'title': 'Login',
							'submit_btn_text': 'Login',
						})
	return render(request, template, c)


@login_required
def logout(request, forum_id):
	lgout(request)
	forum = get_forum_instance(forum_id)
	if forum:
		return redirect('base_forum', forum_id=forum.local_id)
	raise Http404

def forum(request, forum_id, page=1, template=MAIN_FORUM_TEMPLATE):
	forum = get_forum_instance(forum_id)
	subforum_slug = get_subforum_instance(forum, 0).slug()
	return subforum(request, forum_id, 0, subforum_slug, page, template=template)

def subforum(request, forum_id, subforum_id, subforum_slug, page=1, template=SUBFORUM_TEMPLATE):
	forum = get_forum_instance(forum_id)
	if forum:
		subforum = get_subforum_instance(forum, subforum_id)
		if subforum:
			if not check_slug(subforum, subforum_slug):
				if page == 1:
					return redirect('Forum.views.subforum', forum_id=forum_id, subforum_id=subforum_id, subforum_slug=subforum.slug())
				else:
					return redirect('Forum.views.subforum', forum_id=forum_id, subforum_id=subforum_id, subforum_slug=subforum.slug(), page=page)
			if user_has_permission(subforum.view_permission, request.user):
				is_mod = user_has_permission(subforum.mod_permission, request.user)
				can_create_thread = user_has_permission(subforum.create_thread_permission, request.user)
				subforum_list = []
				for sf in subforum.child_set.order_by('local_id'):
					if user_has_permission(sf.view_permission, request.user):
						sf.is_visited = sf.isVisited(request.user)
						subforum_list.append(sf)
				thread_list = []
				for th in subforum.thread_set.order_by('-pinned', '-last_publication_datetime', 'name'):
					if (not th.hidden) or user_has_permission(subforum.mod_permission, request.user):
						th.is_visited = th.isVisited(request.user)
						thread_list.append(th)
				page = int(page) -1
				subforum_num_pages = int(ceil(float(len(thread_list))/float(forum.threads_per_page)))
				if (subforum_num_pages > page and 0 <= page) or subforum_num_pages == 0:
					c = RequestContext(request, {
											'forum_id':forum_id,
											'forum': subforum,
											'subforum_list':subforum_list,
											'thread_list':thread_list[(page*forum.threads_per_page):(page*forum.threads_per_page)+forum.threads_per_page],
											'subforum_current_page':page+1,
											'subforum_pages':range(max(page-1, 1), min(page+4, subforum_num_pages+1)),
											'is_admin':user_has_permission(forum.admin_permission, request.user),
											'is_moderator': is_mod,
											'can_create_thread':can_create_thread and request.user.is_authenticated(),
										})
					return render(request, template, c)
			else:
				c = RequestContext(request, {
											'forum_id':forum_id,
					})
				return render(request, CANT_VIEW_CONTENT, c)
	
	raise Http404

@login_required
@csrf_protect
def newSubforum(request, forum_id, subforum_id, subforum_slug, template=FORM_TEMPLATE):
	check_user_is_spamming(request.user)
	forum = get_forum_instance(forum_id)
	if forum:
		subforum = get_subforum_instance(forum, subforum_id)
		if subforum:
			if not check_slug(subforum, subforum_slug):
				return redirect('Forum.views.newSubforum', forum_id=forum_id, subforum_id=subforum_id, subforum_slug=subforum.slug())
			if user_has_permission(forum.admin_permission, request.user):
				if request.method == 'POST':
					new_subforum_form = FormSubforum(request.POST)
					if new_subforum_form.is_valid():
						new_subforum = new_subforum_form.save(commit=False)
						new_subforum.local_id = forum.subforum_set.count()
						new_subforum.parent = subforum
						new_subforum.forum = forum
						new_subforum.creator = request.user
						new_subforum.save()
						return redirect('subforum', forum_id=forum_id, subforum_id=new_subforum.local_id, subforum_slug=new_subforum.slug())
				else:
					new_subforum = Subforum(
							view_permission = subforum.view_permission,
							mod_permission = subforum.mod_permission,
							create_thread_permission = subforum.create_thread_permission,
							reply_thread_permission = subforum.reply_thread_permission,
						)
					new_subforum_form = FormSubforum(instance=new_subforum)
				c = RequestContext(request, {
										'forum_id':forum_id,
										'form': new_subforum_form,
										'page_title': 'Create Subforum',
										'title': 'Create Subforum',
										'submit_btn_text': 'Create',
									})
				return render(request, template, c)
			else:
				c = RequestContext(request, {
											'forum_id':forum_id,
					})
				return render(request, CANT_VIEW_CONTENT, c)
	
	raise Http404

def thread(request, forum_id, thread_id, thread_slug, page=1, template=THREAD_TEMPLATE):
	forum = get_forum_instance(forum_id)
	if forum:
		thread = get_thread_instance(forum, thread_id)
		if thread:
			if not check_slug(thread, thread_slug):
				if page == 1:
					return redirect('Forum.views.thread', forum_id=forum_id, thread_id=thread_id, thread_slug=thread.slug())
				else:
					return redirect('Forum.views.thread', forum_id=forum_id, thread_id=thread_id, thread_slug=thread.slug(), page=page)
			subforum = thread.parent
			is_mod = user_has_permission(subforum.mod_permission, request.user)
			if user_has_permission(subforum.view_permission, request.user) and (not thread.hidden or is_mod):
				can_post = user_has_permission(subforum.reply_thread_permission, request.user)
				post_list = []
				unfiltered_post_list = thread.post_set.order_by('local_id')
				for pt in unfiltered_post_list:
					if (not pt.hidden) or user_has_permission(subforum.mod_permission, request.user):
						pt.user_is_mod = user_has_permission(subforum.mod_permission, pt.publisher)
						pt.user_is_admin = user_has_permission(forum.admin_permission, pt.publisher)
						if request.user.is_authenticated():
							pt.is_quoted = get_quote_instance(request.user, pt)
							pt.vote = get_vote_instance(request.user, pt)
						post_list.append(pt)
				page = int(page) -1
				thread_num_pages = int(ceil(float(len(post_list))/float(forum.posts_per_page)))
				if thread_num_pages > page and 0 <= page:
					set_visit(thread, request.user)
					thread.visit_counter += 1
					thread.save()
					c = RequestContext(request, {
											'forum_id':forum_id,
											'thread': thread,
											'post_list':post_list[(page*forum.posts_per_page):(page*forum.posts_per_page)+forum.posts_per_page],
											'thread_current_page':page+1,
											'thread_pages':range(max(page-1, 1), min(page+4, thread_num_pages+1)),
											'is_moderator': is_mod,
											'is_admin':user_has_permission(forum.admin_permission, request.user),
											'can_post':can_post and request.user.is_authenticated() and (not thread.closed or is_mod),
										})
					return render(request, template, c)
			else:
				c = RequestContext(request, {
											'forum_id':forum_id,
					})
				return render(request, CANT_VIEW_CONTENT, c)
	raise Http404

def threadLastPage(request, forum_id, thread_id, thread_slug):
	forum = get_forum_instance(forum_id)
	if forum:
		thread = get_thread_instance(forum, thread_id)
		if thread:
			if not check_slug(thread, thread_slug):
				return redirect('Forum.views.threadLastPage', forum_id=forum_id, thread_id=thread_id, thread_slug=thread.slug())
			subforum = thread.parent
			post_list = []
			unfiltered_post_list = thread.post_set.order_by('local_id')
			for pt in unfiltered_post_list:
				if (not pt.hidden) or user_has_permission(subforum.mod_permission, request.user):
					post_list.append(pt)
			thread_num_pages = int(ceil(float(len(post_list))/float(forum.posts_per_page)))
			page = thread_num_pages
			return redirect('Forum.views.thread', forum_id=forum_id, thread_id=thread.local_id, thread_slug=thread.slug(), page=page)
	raise Http404


@login_required
@csrf_protect
def saveThreadSettings(request, forum_id, thread_id, thread_slug, template=FORM_TEMPLATE):
	forum = get_forum_instance(forum_id)
	if forum:
		thread = get_thread_instance(forum, thread_id)
		if thread:
			if not check_slug(thread, thread_slug):
				return redirect('Forum.views.saveThreadSettings', forum_id=forum_id, thread_id=thread_id, thread_slug=thread.slug())
			if user_has_permission(thread.parent.mod_permission, request.user):
				if (request.method == 'POST'):
					form = FormThreadSettings(request.POST, instance=thread)
					if form.is_valid():
						thread.save()
						return redirect('Forum.views.thread', forum_id=forum_id, thread_id=thread_id, thread_slug=thread.slug())
				else:
					form = FormThreadSettings(instance=thread)
					c = RequestContext(request, {
										'forum_id':forum_id,
										'form': form,
										'page_title': 'Thread Settings',
										'title': 'Thread Settings',
										'submit_btn_text': 'Save',
									})
					return render(request, template, c)
	raise Http404

@login_required
def firstPostUnreadThread(request, forum_id, thread_id, thread_slug):
	forum = get_forum_instance(forum_id)
	if forum:
		thread = get_thread_instance(forum, thread_id)
		if thread:
			if not check_slug(thread, thread_slug):
				return redirect('Forum.views.firstPostUnreadThread', forum_id=forum_id, thread_id=thread_id, thread_slug=thread.slug())
			last_visit = get_last_visit_instance(request.user, thread)
			if last_visit:
				last_post = Post.objects.order_by('publication_datetime').filter(publication_datetime__gt=last_visit.datetime).first()
				if last_post:
					return redirect('Forum.views.post', forum_id=forum_id, post_id=last_post.local_id)
			print("shiet")
			return redirect('Forum.views.post', forum_id=forum.local_id, post_id=thread.getLastPublishedPost().local_id)
	raise Http404

@login_required
@csrf_protect
def newThread(request, forum_id, subforum_id, subforum_slug, template=FORM_TEMPLATE):
	check_user_is_spamming(request.user)
	forum = get_forum_instance(forum_id)
	if forum:
		subforum = get_subforum_instance(forum, subforum_id)
		if subforum:
			if not check_slug(subforum, subforum_slug):
				return redirect('Forum.views.newThread', forum_id=forum_id, subforum_id=subforum_id, subforum_slug=subforum.slug())
			if user_has_permission(subforum.create_thread_permission, request.user):
				if request.method == 'POST':
					new_post = Post(publisher=request.user)
					new_post_form = FormPost(request.POST, instance=new_post)
					if new_post_form.is_valid():
						new_post = new_post_form.save(commit=False)
						new_post.local_id = forum.post_set.count()
						new_thread = Thread(
							local_id=forum.thread_set.count(),
							name=new_post.title,
							parent=subforum,
							forum=forum,
							creator=request.user,
							last_publication_datetime=datetime.now(),
							hidden=new_post.hidden,
							)
						new_thread.save()
						new_post.hidden=False
						new_post.forum=forum
						new_post.thread=new_thread
						new_post.save()
						return redirect('Forum.views.thread', forum_id=forum_id, thread_id=new_thread.local_id, thread_slug=new_thread.slug())
				else:
					new_post = Post()
					if user_has_permission(subforum.mod_permission, request.user):
						new_post_form = FormPost_Mod(instance=new_post)
					else:
						new_post_form = FormPost(instance=new_post)
				c = RequestContext(request, {
										'forum_id':forum_id,
										'form': new_post_form,
										'page_title': 'New Thread',
										'title': 'New Thread',
										'submit_btn_text': 'Create',
									})
				return render(request, template, c)
			else:
				c = RequestContext(request, {
											'forum_id':forum_id,
					})
				return render(request, CANT_VIEW_CONTENT, c)
	
	raise Http404

@login_required
@csrf_protect
def replyThread(request, forum_id, thread_id, thread_slug, template=FORM_TEMPLATE):
	check_user_is_spamming(request.user)
	forum = get_forum_instance(forum_id)
	if forum:
		thread = get_thread_instance(forum, thread_id)
		if thread and (not thread.closed or user_has_permission(thread.parent.mod_permission, request.user)):
			if not check_slug(thread, thread_slug):
				return redirect('Forum.views.replythread', forum_id=forum_id, thread_id=thread_id, thread_slug=thread.slug())
			if user_has_permission(thread.parent.reply_thread_permission, request.user):
				if request.method == 'POST':
					new_post = Post(publisher=request.user)
					if user_has_permission(thread.parent.mod_permission, request.user):
						new_post_form = FormPost_Mod(request.POST, instance=new_post)
					else:
						new_post_form = FormPost(request.POST, instance=new_post)
					if new_post_form.is_valid():
						new_post = new_post_form.save(commit=False)
						new_post.local_id = forum.post_set.count()
						new_post.forum=forum
						new_post.thread=thread
						new_post.save()
						thread.last_publication_datetime=new_post.publication_datetime
						thread.save()
						return redirect('Forum.views.post', forum_id=forum_id, post_id=new_post.local_id)
				else:
					new_post = Post()
					quotes_text = ""
					quote_list = Quote.objects.filter(user=request.user, thread=thread)
					for quote in quote_list:
						quotes_text += "[quote="+quote.post.publisher.username+"]"+quote.post.content+"[/quote]\n\n"
						quote.delete()
					new_post.content = quotes_text
					if user_has_permission(thread.parent.mod_permission, request.user):
						new_post_form = FormPost_Mod(instance=new_post)
					else:
						new_post_form = FormPost(instance=new_post)
				c = RequestContext(request, {
										'forum_id':forum_id,
										'form': new_post_form,
										'page_title': 'Reply Thread',
										'title': 'Reply Thread',
										'submit_btn_text': 'Reply',
									})
				return render(request, template, c)
			else:
				c = RequestContext(request, {
											'forum_id':forum_id,
					})
				return render(request, CANT_VIEW_CONTENT, c)
	raise Http404

def post(request, forum_id, post_id):
	forum = get_forum_instance(forum_id)
	if forum:
		post = get_post_instance(forum, post_id)
		if post:
			thread = post.thread
			post_list = thread.post_set.order_by('local_id')
			num = 0
			found = False
			for pt in post_list:
				if pt == post:
					found = True
					break
				num += 1
			if found:
				page = (num/forum.posts_per_page)+1
				return redirect('Forum.views.thread', forum_id=forum_id, thread_id=post.thread.local_id, thread_slug=post.thread.slug(), page=page, post_id=post_id)
	raise Http404

@login_required
@csrf_protect
def editPost(request, forum_id, post_id, template=FORM_TEMPLATE):
	check_user_is_spamming(request.user)
	forum = get_forum_instance(forum_id)
	if forum:
		post = get_post_instance(forum, post_id)
		if post and user_has_permission(post.thread.parent.view_permission, request.user):
			post_old_title = post.title
			post_old_content = post.content
			if request.method == 'POST':
				if user_has_permission(post.thread.parent.mod_permission, request.user):
					edit_post_form = FormPost_Mod(request.POST, instance=post)
				else:
					edit_post_form = FormPost(request.POST, instance=post)
				if edit_post_form.is_valid():
					post_edited = PostEdited(
						post=post,
						user=request.user,
						datetime=datetime.now(),
						reason='',
						old_title=post_old_title,
						new_title=post.title,
						old_content=post_old_content,
						new_content=post.content,
						user_is_moderator = user_has_permission(post.thread.parent.mod_permission, request.user),
						user_is_administrator = user_has_permission(forum.admin_permission, request.user),
						)
					post = edit_post_form.save()
					if post.thread.post_set.first() == post:
						post.thread.name = post.title
						post.thread.save()
					post_edited.save()
					return redirect('Forum.views.post', forum_id=forum_id, post_id=post.local_id)
			else:
				if user_has_permission(post.thread.parent.mod_permission, request.user):
					edit_post_form = FormPost_Mod(instance=post)
				elif post.publisher == request.user:
					edit_post_form = FormPost(instance=post)
				else:
					c = RequestContext(request, {
											'forum_id':forum_id,
						})
					return render(request, CANT_VIEW_CONTENT, c)
			c = RequestContext(request, {
									'forum_id':forum_id,
									'form': edit_post_form,
									'page_title': 'Edit Post',
									'title': 'Edit Post',
									'submit_btn_text': 'Save',
								})
			return render(request, template, c)
	raise Http404

@login_required
@csrf_protect
def reportPost(request, forum_id, post_id, template=FORM_TEMPLATE):
	check_user_is_spamming(request.user)
	forum = get_forum_instance(forum_id)
	if forum:
		post = get_post_instance(forum, post_id)
		if post and user_has_permission(post.thread.parent.view_permission, request.user):
			if request.method == 'POST':
				report_post_form = FormReportPost(request.POST)
				if report_post_form.is_valid():
					report_post = report_post_form.save(commit=False)
					report_post.user = request.user
					report_post.post = post
					report_post.save()
					return redirect('Forum.views.thread', forum_id=forum_id, thread_id=post.thread.local_id, thread_slug=post.thread.slug())
			else:
				report_post_form = FormReportPost()
			c = RequestContext(request, {
									'forum_id':forum_id,
									'form': report_post_form,
									'page_title': 'Report Post',
									'title': 'Report Post',
									'submit_btn_text': 'Report',
								})
			return render(request, template, c)
	raise Http404

@login_required
def quotePost(request, forum_id, post_id):
	forum = get_forum_instance(forum_id)
	if forum:
		post = get_post_instance(forum, post_id)
		if post and user_has_permission(post.thread.parent.view_permission, request.user):
			quote = get_quote_instance(request.user, post)
			response_data = {}
			if quote:
				quote.delete()
				response_data['action'] = 'removed'
			else:
				Quote(user=request.user, post=post, thread=post.thread).save()
				response_data['action'] = 'added'
			return HttpResponse(json.dumps(response_data), content_type="application/json")
	raise Http404

@login_required
def votePostUp(request, forum_id, post_id):
	forum = get_forum_instance(forum_id)
	if forum and forum.allow_up_votes:
		post = get_post_instance(forum, post_id)
		if post and user_has_permission(post.thread.parent.view_permission, request.user):
			vote = get_vote_instance(request.user, post)
			response_data = {}
			if vote:
				if vote.type == "Up":
					vote.delete()
					response_data['action'] = 'removed'
				else:
					vote.type = "Up"
					vote.save()
					response_data['action'] = 'added'
			else:
				Vote(user=request.user, post=post, type="Up").save()
				response_data['action'] = 'added'
			response_data['score'] = post.score()
			return HttpResponse(json.dumps(response_data), content_type="application/json")
	raise Http404

@login_required
def votePostDown(request, forum_id, post_id):
	forum = get_forum_instance(forum_id)
	if forum and forum.allow_down_votes:
		post = get_post_instance(forum, post_id)
		if post and user_has_permission(post.thread.parent.view_permission, request.user):
			vote = get_vote_instance(request.user, post)
			response_data = {}
			if vote:
				if vote.type == "Down":
					vote.delete()
					response_data['action'] = 'removed'
				elif vote.type == "Up":
					vote.type = "Down"
					vote.save()
					response_data['action'] = 'added'
			else:
				Vote(user=request.user, post=post, type="Down").save()
				response_data['action'] = 'added'
			response_data['score'] = post.score()
			return HttpResponse(json.dumps(response_data), content_type="application/json")
	raise Http404
