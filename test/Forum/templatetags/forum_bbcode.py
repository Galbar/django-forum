import re
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.template.defaultfilters import stringfilter
from django import template
from Forum.postmarkup import render_bbcode

register = template.Library()

@register.filter
@stringfilter
def bbcode(t):
	t = render_bbcode(t, clean=True, paragraphs=False, render_unknown_tags=True)
	return mark_safe(t)
