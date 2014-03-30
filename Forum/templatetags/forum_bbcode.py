import re
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.template.defaultfilters import stringfilter
from django import template
from Forum.postmarkup import render_bbcode
from Forum.emoticons import render_emoticons

register = template.Library()

@register.filter
@stringfilter
def bbcode(t):
	t = escape(t)
	t = render_emoticons(t)
	t = render_bbcode(t, clean=True, paragraphs=False, render_unknown_tags=True, encoding="utf-8")
	return mark_safe(t)
