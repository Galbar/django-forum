# -*- coding: utf-8 -*-
from django import forms
from Forum.models import Post, Subforum, PostReported
from django.core.validators import MaxLengthValidator

class FormPost(forms.ModelForm):
    title = forms.CharField(min_length=1, max_length=Post._meta.get_field('title').max_length, required=False)
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
    class Meta:
        model = PostReported
        fields = ['reason']