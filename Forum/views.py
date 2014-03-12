# -*- coding: utf-8 -*-
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as lgout
from django.template.defaultfilters import slugify
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from Forum.models import *
from Forum.settings import *
from Forum.forms import *
from django.template import RequestContext
from math import ceil


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

def user_has_permission(perm, user):
    if perm == "public":
        return True
    if perm == "registered":
        return user.is_authenticated()
    if perm == "none":
        return user.has_perm("Forum.forum_admin")
    return user.has_perm(perm)

def set_visit(thread, user):
    if not user.is_authenticated():
        return
    try:
        l = LastUserVisit.objects.get(user=user, thread=thread)
        l.datetime = datetime.now()
        l.save()
    except ObjectDoesNotExist:
        l = LastUserVisit(user=user, thread=thread, datetime=datetime.now())
        l.save()


# Create your views here.
@login_required
def login(request, forum_id):
    forum = get_forum_instance(forum_id)
    if forum:
        return redirect('base_forum', forum_id=forum.local_id)
    raise Http404

@login_required
def logout(request, forum_id):
    lgout(request)
    forum = get_forum_instance(forum_id)
    if forum:
        return redirect('base_forum', forum_id=forum.local_id)
    raise Http404

def forum(request, forum_id, page=1, template=MAIN_FORUM_TEMPLATE):
    return subforum(request, forum_id, 0, page, template=template)

def subforum(request, forum_id, subforum_id, page=1, template=SUBFORUM_TEMPLATE):
    forum = get_forum_instance(forum_id)
    if forum:
        subforum = get_subforum_instance(forum, subforum_id)
        if subforum:
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
                subforum_num_pages = int(ceil(float(len(thread_list))/float(THREADS_PER_PAGE)))
                if (subforum_num_pages > page and 0 <= page) or subforum_num_pages == 0:
                    c = RequestContext(request, {
                                            'forum_id':forum_id,
                                            'forum': subforum,
                                            'subforum_list':subforum_list,
                                            'thread_list':thread_list[(page*THREADS_PER_PAGE):(page*THREADS_PER_PAGE)+THREADS_PER_PAGE],
                                            'subforum_current_page':page+1,
                                            'subforum_pages':range(max(page-1, 1), min(page+4, subforum_num_pages+1)),
                                            'is_admin':user_has_permission(forum.admin_permission, request.user),
                                            'is_moderator': is_mod,
                                            'can_create_thread':can_create_thread and request.user.is_authenticated(),
                                        })
                    return render(request, template, c)
            else:
                c = RequestContext(request, {})
                return render(request, CANT_VIEW_CONTENT, c)
    
    raise Http404

def newSubforum(request, forum_id, subforum_id, template=FORM_TEMPLATE):
    forum = get_forum_instance(forum_id)
    if forum:
        subforum = get_subforum_instance(forum, subforum_id)
        if subforum:
            if user_has_permission(forum.admin_permission, request.user):
                if request.method == 'POST':
                    new_subforum_form = FormSubforum(request.POST)
                    if new_subforum_form.is_valid():
                        new_subforum = new_subforum_form.save(commit=False)
                        new_subforum.local_id = forum.subforum_set.count()
                        new_subforum.parent = subforum
                        new_subforum.forum = forum
                        new_subforum.save()
                        return redirect('subforum', forum_id=forum_id, subforum_id=slugify(new_subforum.__unicode__()))
                else:
                    new_subforum = Subforum(
                            view_permission = subforum.view_permission,
                            mod_permission = subforum.mod_permission,
                            create_thread_permission = subforum.create_thread_permission,
                            reply_thread_permission = subforum.reply_thread_permission,
                        )
                    new_subforum_form = FormSubforum(instance=new_subforum)
                c = RequestContext(request, {
                                        'form': new_subforum_form,
                                        'page_title': 'Create Subforum',
                                        'title': 'Create Subforum',
                                        'submit_btn_text': 'Create',
                                    })
                return render(request, template, c)
            else:
                c = RequestContext(request, {})
                return render(request, CANT_VIEW_CONTENT, c)
    
    raise Http404

def thread(request, forum_id, thread_id, page=1, go_last_page=False, template=THREAD_TEMPLATE):
    forum = get_forum_instance(forum_id)
    if forum:
        thread = get_thread_instance(forum, thread_id)
        if thread:
            subforum = thread.parent
            if user_has_permission(subforum.view_permission, request.user):
                is_mod = user_has_permission(subforum.mod_permission, request.user)
                can_post = user_has_permission(subforum.reply_thread_permission, request.user)
                post_list = []
                unfiltered_post_list = thread.post_set.order_by('local_id')
                for pt in unfiltered_post_list:
                    if (not pt.hidden) or user_has_permission(subforum.mod_permission, request.user):
                        pt.user_is_mod = user_has_permission(subforum.mod_permission, pt.publisher)
                        pt.user_is_admin = user_has_permission(forum.admin_permission, pt.publisher)
                        post_list.append(pt)

                page = int(page) -1
                thread_num_pages = int(ceil(float(len(post_list))/float(POSTS_PER_PAGE)))
                if go_last_page:
                    page = thread_num_pages
                if thread_num_pages > page and 0 <= page:
                    set_visit(thread, request.user)
                    thread.visit_counter += 1
                    thread.save()
                    c = RequestContext(request, {
                                            'forum_id':forum_id,
                                            'thread': thread,
                                            'post_list':post_list[(page*POSTS_PER_PAGE):(page*POSTS_PER_PAGE)+POSTS_PER_PAGE],
                                            'thread_current_page':page+1,
                                            'thread_pages':range(max(page-1, 1), min(page+4, thread_num_pages+1)),
                                            'is_moderator': is_mod,
                                            'is_admin':user_has_permission(forum.admin_permission, request.user),
                                            'can_post':can_post and request.user.is_authenticated(),
                                        })
                    return render(request, template, c)
            else:
                c = RequestContext(request, {})
                return render(request, CANT_VIEW_CONTENT, c)
    
    raise Http404

def newThread(request, forum_id, subforum_id, template=FORM_TEMPLATE):
    forum = get_forum_instance(forum_id)
    if forum:
        subforum = get_subforum_instance(forum, subforum_id)
        if subforum:
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
                        return redirect('thread', forum_id=forum_id, thread_id=slugify(new_thread.__unicode__()))
                else:
                    new_post = Post()
                    if user_has_permission(subforum.mod_permission, request.user):
                        new_post_form = FormPost_Mod(instance=new_post)
                    else:
                        new_post_form = FormPost(instance=new_post)
                c = RequestContext(request, {
                                        'form': new_post_form,
                                        'page_title': 'New Thread',
                                        'title': 'New Thread',
                                        'submit_btn_text': 'Create',
                                    })
                return render(request, template, c)
            else:
                c = RequestContext(request, {})
                return render(request, CANT_VIEW_CONTENT, c)
    
    raise Http404

def replyThread(request, forum_id, thread_id, template=FORM_TEMPLATE):
    forum = get_forum_instance(forum_id)
    if forum:
        thread = get_thread_instance(forum, thread_id)
        if thread:
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
                        return redirect('thread_last_page', forum_id=forum_id, thread_id=slugify(thread.__unicode__()))
                else:
                    new_post = Post()
                    if user_has_permission(thread.parent.mod_permission, request.user):
                        new_post_form = FormPost_Mod(instance=new_post)
                    else:
                        new_post_form = FormPost(instance=new_post)
                c = RequestContext(request, {
                                        'form': new_post_form,
                                        'page_title': 'Reply Thread',
                                        'title': 'Reply Thread',
                                        'submit_btn_text': 'Reply',
                                    })
                return render(request, template, c)
            else:
                c = RequestContext(request, {})
                return render(request, CANT_VIEW_CONTENT, c)

    raise Http404

@login_required
def editPost(request, forum_id, post_id, template=FORM_TEMPLATE):
    forum = get_forum_instance(forum_id)
    if forum:
        post = get_post_instance(forum, post_id)
        if post:
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
                    return redirect('thread', forum_id=forum_id, thread_id=slugify(post.thread.__unicode__()))
            else:
                if user_has_permission(post.thread.parent.mod_permission, request.user):
                    edit_post_form = FormPost_Mod(instance=post)
                elif post.publisher == request.user:
                    edit_post_form = FormPost(instance=post)
                else:
                    c = RequestContext(request, {})
                    return render(request, CANT_VIEW_CONTENT, c)

            c = RequestContext(request, {
                                    'form': edit_post_form,
                                    'page_title': 'Edit Post',
                                    'title': 'Edit Post',
                                    'submit_btn_text': 'Save',
                                })
            return render(request, template, c)
    raise Http404

@login_required
def reportPost(request, forum_id, post_id, template=FORM_TEMPLATE):
    forum = get_forum_instance(forum_id)
    if forum:
        post = get_post_instance(forum, post_id)
        if post:
            if request.method == 'POST':
                report_post_form = FormReportPost(request.POST)
                if report_post_form.is_valid():
                    report_post = report_post_form.save(commit=False)
                    report_post.user = request.user
                    report_post.post = post
                    report_post.save()
                    return redirect('thread', forum_id=forum_id, thread_id=slugify(post.thread.__unicode__()))
            else:
                report_post_form = FormReportPost()

            c = RequestContext(request, {
                                    'form': report_post_form,
                                    'page_title': 'Report Post',
                                    'title': 'Report Post',
                                    'submit_btn_text': 'Report',
                                })
            return render(request, template, c)
    raise Http404