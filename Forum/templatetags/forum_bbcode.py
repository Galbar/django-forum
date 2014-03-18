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
	#t = escape(t)

	# Remove newlines from tables
	pattern = re.compile(r"(?P<bbtag>\[\/?(table|th|tr|td)\])\r?\n+")
	pos = 0
	ret_text = ""
	for m in pattern.finditer(t):
		ret_text += t[pos:m.start()] + m.groupdict()["bbtag"]
		pos = m.end()
	ret_text += t[pos:]
	t = ret_text

	t = render_bbcode(t, clean=True, paragraphs=False, render_unknown_tags=True)
	return mark_safe(t)
