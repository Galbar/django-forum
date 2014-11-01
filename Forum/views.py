# -*- coding: utf-8 -*-
import json
from django.http import Http404, HttpResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as lgout, authenticate, login as lgin
from django.shortcuts import render, redirect
from datetime import datetime
from Forum.models import *
from Forum.settings import *
from Forum.forms import *
from Forum.lib import *
from Forum.getInstanceLib import *
from Forum.modelsLib import *
import Forum.signals as signals
from math import ceil

# Create your views here.
def login(request, forum_id, template="Forum/forms/login.html", template_ajax="Forum/forms/ajax/login.html"):
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
	c = {
			'forum_id':forum_id,
			'form': form,
		}
	if request.is_ajax():
		return render(request, template_ajax, c)
	else:
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
	if forum:
		subforum_slug = forum.main_forum.slug()
		return subforum(request, forum_id, 0, subforum_slug, page, template=template)
	raise Http404

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
			if subforum.canView(request.user):
				is_mod = subforum.canModerate(request.user)
				can_create_thread = subforum.canCreateThread(request.user)
				subforum_list = []
				for sf in subforum.child_set.order_by('local_id'):
					if sf.canView(request.user):
						sf.is_visited = sf.isVisited(request.user)
						subforum_list.append(sf)
				sf_th_set = subforum.thread_set.order_by('-pinned', '-last_publication_datetime', 'name')
				if not subforum.canModerate(request.user):
					sf_th_set = sf_th_set.exclude(hidden=True)
				thread_list = []
				for th in sf_th_set:
					th.is_visited = th.isVisited(request.user)
					thread_list.append(th)
				page = int(page) -1
				subforum_num_pages = int(ceil(float(len(thread_list))/float(forum.threads_per_page)))
				if (subforum_num_pages > page and 0 <= page) or subforum_num_pages == 0:
					c = {
							'forum_id':forum_id,
							'forum': subforum,
							'subforum_list':subforum_list,
							'thread_list':thread_list[(page*forum.threads_per_page):(page*forum.threads_per_page)+forum.threads_per_page],
							'subforum_current_page':page+1,
							'subforum_pages':range(max(page, 1), min(page+3, subforum_num_pages+1)),
							'is_admin':user_has_permission(forum.admin_permission, request.user),
							'is_moderator': is_mod,
							'can_create_thread':can_create_thread and request.user.is_authenticated(),
						}
					return render(request, template, c)
			else:
				c = {
						'forum_id':forum_id,
					}
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
			if forum.canAdministrate(request.user):
				if request.method == 'POST':
					new_subforum_form = Subforum(forum=forum)
					new_subforum_form = FormSubforum(request.POST, instance=new_subforum_form)
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
							forum = subforum.forum,
							view_permission = subforum.view_permission,
							mod_permission = subforum.mod_permission,
							create_thread_permission = subforum.create_thread_permission,
							reply_thread_permission = subforum.reply_thread_permission,
						)
					new_subforum_form = FormSubforum(instance=new_subforum)
				c = {
						'forum_id':forum_id,
						'form': new_subforum_form,
						'page_title': 'Create Subforum',
						'title': 'Create Subforum',
						'submit_btn_text': 'Create',
					}
				return render(request, template, c)
			else:
				c = {
						'forum_id':forum_id,
					}
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
			is_mod = subforum.canModerate(request.user)
			if subforum.canView(request.user) and (not thread.hidden or is_mod):
				can_post = subforum.canReplyThread(request.user)
				post_list = []
				unfiltered_post_list = thread.post_set.order_by('local_id')
				if not subforum.canModerate(request.user):
					unfiltered_post_list = unfiltered_post_list.exclude(hidden=True)
				for pt in unfiltered_post_list:
					if request.user.is_authenticated():
						pt.is_quoted = get_quote_instance(request.user, pt)
						pt.vote = get_vote_instance(request.user, pt)
					post_list.append(pt)
				if request.user.is_authenticated() and thread.poll_set.count() and thread.poll_set.first().userCanVote(request.user):
					poll = thread.poll_set.first()
				else:
					poll = None
				page = int(page) -1
				thread_num_pages = int(ceil(float(len(post_list))/float(forum.posts_per_page)))
				if thread_num_pages > page and 0 <= page:
					set_visit(thread, request.user)
					thread.visit_counter += 1
					thread.save()
					c = {
							'forum_id':forum_id,
							'thread': thread,
							'post_list':post_list[(page*forum.posts_per_page):(page*forum.posts_per_page)+forum.posts_per_page],
							'thread_current_page':page+1,
							'thread_pages':range(max(page, 1), min(page+3, thread_num_pages+1)),
							'is_moderator': is_mod,
							'is_admin':user_has_permission(forum.admin_permission, request.user),
							'can_post':can_post and request.user.is_authenticated() and (not thread.closed or is_mod),
							'poll': poll,
						}
					return render(request, template, c)
			else:
				c = {
						'forum_id':forum_id,
					}
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
				if (not pt.hidden) or subforum.canModerate(request.user):
					post_list.append(pt)
			thread_num_pages = int(ceil(float(len(post_list))/float(forum.posts_per_page)))
			page = thread_num_pages
			return redirect('Forum.views.thread', forum_id=forum_id, thread_id=thread.local_id, thread_slug=thread.slug(), page=page)
	raise Http404


@csrf_protect
def saveThreadSettings(request, forum_id, thread_id, thread_slug, template="Forum/forms/thread_settings.html"):
	forum = get_forum_instance(forum_id)
	if forum:
		thread = get_thread_instance(forum, thread_id)
		if thread:
			if not check_slug(thread, thread_slug):
				return redirect('Forum.views.saveThreadSettings', forum_id=forum_id, thread_id=thread_id, thread_slug=thread.slug())
			if thread.parent.canModerate(request.user):
				if (request.method == 'POST'):
					form = FormThreadSettings(request.POST, instance=thread)
					if form.is_valid():
						thread.save()
						return redirect('Forum.views.thread', forum_id=forum_id, thread_id=thread_id, thread_slug=thread.slug())
				else:
					form = FormThreadSettings(instance=thread)
					c = {
							'forum_id':forum_id,
							'form': form,
							'thread': thread,
						}
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
				last_post = Post.objects.order_by('publication_datetime').filter(thread=thread, publication_datetime__gt=last_visit.datetime).first()
				if last_post:
					return redirect('Forum.views.post', forum_id=forum_id, post_id=last_post.local_id)
			print("shiet")
			return redirect('Forum.views.post', forum_id=forum.local_id, post_id=thread.getLastPublishedPost().local_id)
	raise Http404

@login_required
@csrf_protect
def newThread(request, forum_id, subforum_id, subforum_slug, template="Forum/forms/thread.html"):
	check_user_is_spamming(request.user)
	forum = get_forum_instance(forum_id)
	if forum:
		subforum = get_subforum_instance(forum, subforum_id)
		if subforum:
			if not check_slug(subforum, subforum_slug):
				return redirect('Forum.views.newThread', forum_id=forum_id, subforum_id=subforum_id, subforum_slug=subforum.slug())
			if subforum.canCreateThread(request.user):
				if request.method == 'POST':
					new_post = Post(publisher=request.user)
					new_post_form = FormNewThread(request.POST, instance=new_post)
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
						if request.POST.get("add_poll", "False") == "True" and request.POST.get("question", "") != "":
							rang = range(0, int(request.POST.get("poll_option_count", "2")))
							question = request.POST.get("question")
							option_list = []
							for i in rang:
								opt = request.POST.get("poll-option["+str(i)+"]", "")
								if opt != "":
									option_list.append(opt)
							if len(option_list) >= 2:
								new_thread.setPoll(question, option_list)

						new_post.hidden=False
						new_post.forum=forum
						new_post.thread=new_thread
						new_post.save()
						# Send new thread signal
						signals.thread_published.send(sender=forum, thread=new_thread)
						return redirect('Forum.views.thread', forum_id=forum_id, thread_id=new_thread.local_id, thread_slug=new_thread.slug())
				else:
					new_post = Post()
					new_post_form = FormNewThread(instance=new_post)
				c = {
						'forum_id':forum_id,
						'form': new_post_form,
						'page_title': 'New Thread',
						'title': 'New Thread',
						'submit_btn_text': 'Create',
					}
				return render(request, template, c)
			else:
				c = {
						'forum_id':forum_id,
					}
				return render(request, CANT_VIEW_CONTENT, c)
	
	raise Http404

@login_required
@csrf_protect
def replyThread(request, forum_id, thread_id, thread_slug, template="Forum/forms/post.html", template_ajax="Forum/forms/ajax/post.html"):
	check_user_is_spamming(request.user)
	forum = get_forum_instance(forum_id)
	if forum:
		thread = get_thread_instance(forum, thread_id)
		if thread and (not thread.closed or thread.parent.canModerate(request.user)):
			if not check_slug(thread, thread_slug):
				return redirect('Forum.views.replythread', forum_id=forum_id, thread_id=thread_id, thread_slug=thread.slug())
			if thread.parent.canReplyThread(request.user) and request.user.is_authenticated():
				if request.method == 'POST':
					new_post = Post(publisher=request.user)
					if thread.parent.canModerate(request.user):
						new_post_form = FormPost_Mod(request.POST, instance=new_post)
					else:
						new_post_form = FormPost(request.POST, instance=new_post)
					if new_post_form.is_valid():
						new_post = new_post_form.save(commit=False)
						new_post.local_id = forum.post_set.count()
						new_post.forum=forum
						new_post.thread=thread
						new_post.save()
						# Send signal new post published
						signals.post_published.send(sender=forum, post=new_post)
						thread.last_publication_datetime=new_post.publication_datetime
						thread.save()
						quote_list = Quote.objects.filter(user=request.user, thread=thread)
						for quote in quote_list:
							quote.delete()
						return redirect('Forum.views.post', forum_id=forum_id, post_id=new_post.local_id)
				else:
					new_post = Post()
					quotes_text = ""
					quote_list = Quote.objects.filter(user=request.user, thread=thread)
					for quote in quote_list:
						quotes_text += "[quote="+quote.post.publisher.username+"]"+quote.post.content+"[/quote]\n\n"
					new_post.content = quotes_text
					if thread.parent.canModerate(request.user):
						new_post_form = FormPost_Mod(instance=new_post)
					else:
						new_post_form = FormPost(instance=new_post)
				if request.is_ajax():
					template = template_ajax
					c = {
							'forum_id':forum_id,
							'form': new_post_form,
							'thread':thread,
						}
				else:
					c = {
							'forum_id':forum_id,
							'form': new_post_form,
							'page_title': 'Reply Thread',
							'title': 'Reply Thread',
							'submit_btn_text': 'Send',
						}
				return render(request, template, c)

					
			else:
				c = {
						'forum_id':forum_id,
					}
				return render(request, CANT_VIEW_CONTENT, c)
	raise Http404

@login_required
@csrf_protect
def voteThreadPoll(request, forum_id, thread_id, thread_slug):
	forum = get_forum_instance(forum_id)
	if forum:
		thread = get_thread_instance(forum, thread_id)
		if thread:
			if not check_slug(thread, thread_slug):
				return redirect('Forum.views.voteThreadPoll', forum_id=forum_id, thread_id=thread_id, thread_slug=thread.slug())
			subforum = thread.parent
			is_mod = subforum.canModerate(request.user)
			if subforum.canView(request.user) and (not thread.hidden or is_mod):
				if thread.poll:
					if thread.poll.userCanVote(request.user) and request.method == 'POST':
						answer = request.POST.get("poll_answer", False)
						if answer:
							thread.poll.vote(request.user, answer)
	return redirect('Forum.views.thread', forum_id=forum_id, thread_id=thread_id, thread_slug=thread.slug())

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
def editPost(request, forum_id, post_id, template="Forum/forms/edit_post.html", template_ajax="Forum/forms/ajax/edit_post.html"):
	check_user_is_spamming(request.user)
	forum = get_forum_instance(forum_id)
	if forum:
		post = get_post_instance(forum, post_id)
		if post and post.thread.parent.canView(request.user):
			post_old_title = post.title
			post_old_content = post.content
			if request.method == 'POST':
				if post.thread.parent.canModerate(request.user):
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
						user_is_moderator = post.thread.parent.canModerate(request.user),
						user_is_administrator = forum.canAdministrate(request.user),
						)
					post = edit_post_form.save(commit=False)
					if post.thread.post_set.first() == post:
						if post.title == "":
							post.title = post_old_title
						post.thread.name = post.title
						post.thread.save()
					post_edited.save()
					post.save()
					return redirect('Forum.views.post', forum_id=forum_id, post_id=post.local_id)
			else:
				if post.thread.parent.canModerate(request.user):
					edit_post_form = FormPost_Mod(instance=post)
				elif post.publisher == request.user:
					edit_post_form = FormPost(instance=post)
				else:
					c = {
							'forum_id':forum_id,
						}
					return render(request, CANT_VIEW_CONTENT, c)
			c = {
					'forum_id':forum_id,
					'form': edit_post_form,
					'post':post,
					'user_is_mod':user_has_permission(post.thread.parent.mod_permission, request.user),
				}
			if request.is_ajax():
				return render(request, template_ajax, c)
			else:
				return render(request, template, c)
	raise Http404

@login_required
@csrf_protect
def reportPost(request, forum_id, post_id, template="Forum/forms/report_post.html", template_ajax="Forum/forms/ajax/report_post.html"):
	check_user_is_spamming(request.user)
	forum = get_forum_instance(forum_id)
	if forum:
		post = get_post_instance(forum, post_id)
		if post and post.thread.parent.canView(request.user):
			if request.method == 'POST':
				report_post_form = FormReportPost(request.POST)
				if report_post_form.is_valid():
					report_post = report_post_form.save(commit=False)
					report_post.user = request.user
					report_post.post = post
					report_post.save()
					return redirect('Forum.views.post', forum_id=forum_id, post_id=post.local_id)
			else:
				report_post_form = FormReportPost()
			c = {
					'forum_id':forum_id,
					'form': report_post_form,
					'post': post,
				}
			if request.is_ajax():
				return render(request, template_ajax, c)
			else:
				return render(request, template, c)
	raise Http404

@login_required
def quotePost(request, forum_id, post_id):
	forum = get_forum_instance(forum_id)
	if forum:
		post = get_post_instance(forum, post_id)
		if post and post.thread.parent.canView(request.user):
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
		if post and post.thread.parent.canView(request.user):
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
				# Send signal
				signals.upvote.send(sender=forum, user=request.user, post=post)
				if not post.score_event_sent and post.score() >= forum.positive_score_event:
					post.score_event_sent = True
					post.save()
					signals.positive_score_event.send(sender=forum, post=post)
			response_data['score'] = post.score()
			return HttpResponse(json.dumps(response_data), content_type="application/json")
	raise Http404

@login_required
def votePostDown(request, forum_id, post_id):
	forum = get_forum_instance(forum_id)
	if forum and forum.allow_down_votes:
		post = get_post_instance(forum, post_id)
		if post and post.thread.parent.canView(request.user):
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
				# Send signal
				signals.downvote.send(sender=forum, user=request.user, post=post)
				if not post.score_event_sent and post.score() <= forum.negative_score_event:
					post.score_event_sent = True
					post.save()
					signals.negative_score_event.send(sender=forum, post=post)
			response_data['score'] = post.score()
			return HttpResponse(json.dumps(response_data), content_type="application/json")
	raise Http404
