# -*- coding: utf-8 -*-
from django import forms
from Forum.models import *

class FormPost(forms.ModelForm):
    title = forms.CharField(max_length=Post._meta.get_field('title').max_length, required=False)
    content = forms.CharField(min_length=1, max_length=Post._meta.get_field('content').max_length, widget=forms.Textarea)
    class Meta:
        model = Post
        fields = ['title', 'content']

class FormNewThread(forms.ModelForm):
    title = forms.CharField(max_length=Post._meta.get_field('title').max_length, required=True)
    content = forms.CharField(min_length=1, max_length=Post._meta.get_field('content').max_length, widget=forms.Textarea)
    class Meta:
        model = Post
        fields = ['title', 'content']

class FormPost_Mod(forms.ModelForm):
    title = forms.CharField(min_length=1, max_length=Post._meta.get_field('title').max_length, required=False)
    content = forms.CharField(min_length=1, max_length=Post._meta.get_field('content').max_length, widget=forms.Textarea)
    class Meta:
        model = Post
        fields = ['title', 'content', 'hidden']

class FormSubforum(forms.ModelForm):
    class Meta:
        model = Subforum
        fields = ['name', 'description', 'view_permission', 'mod_permission', 'create_thread_permission', 'reply_thread_permission']

class FormReportPost(forms.ModelForm):
    reason = forms.CharField(max_length=Post._meta.get_field('content').max_length, widget=forms.Textarea, required=False)
    class Meta:
        model = PostReported
        fields = ['reason']

class FormThreadSettings(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ['parent', 'hidden', 'closed', 'pinned']

class FormUserLogin(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)