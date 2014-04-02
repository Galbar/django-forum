# -*- coding: UTF-8 -*-
import re
from django.templatetags.static import static

class GeneralSmilie(object):
	"""docstring for GeneralSmilie"""
	def __init__(self, pattern, icon_path, use_staticfiles=False):
		self.pattern = re.compile(pattern)
		if use_staticfiles:
			self.icon_path = static(icon_path)
		else:
			self.icon_path = icon_path
		
	def parse(self, text):
		pos = 0
		ret_text = ""
		for m in self.pattern.finditer(text):
			ret_text += text[pos:m.start()] + "<img class='emoticon' src='"+self.icon_path+"' />"
			pos = m.end()
		ret_text += text[pos:]
		return ret_text

class ColonSurroundedSmilie(GeneralSmilie):
	"""docstring for ColonSurroundedSmilie"""
	def __init__(self, name, icon_path, use_staticfiles=False):
		pattern = re.compile(r':'+name+':')
		super(ColonSurroundedSmilie, self).__init__(pattern, icon_path, use_staticfiles)


_em_list = [
	ColonSurroundedSmilie("alien", "Forum/emoticons/alien.png", use_staticfiles=True),
	ColonSurroundedSmilie("angel", "Forum/emoticons/angel.png", use_staticfiles=True),
	ColonSurroundedSmilie("angry", "Forum/emoticons/angry.png", use_staticfiles=True),
	ColonSurroundedSmilie("blink", "Forum/emoticons/blink.png", use_staticfiles=True),
	ColonSurroundedSmilie("blush", "Forum/emoticons/blush.png", use_staticfiles=True),
	ColonSurroundedSmilie("cheerful", "Forum/emoticons/cheerful.png", use_staticfiles=True),
	ColonSurroundedSmilie("cool", "Forum/emoticons/cool.png", use_staticfiles=True),
	ColonSurroundedSmilie("crying", "Forum/emoticons/crying.png", use_staticfiles=True),
	ColonSurroundedSmilie("devil", "Forum/emoticons/devil.png", use_staticfiles=True),
	ColonSurroundedSmilie("dizzy", "Forum/emoticons/dizzy.png", use_staticfiles=True),
	ColonSurroundedSmilie("ermm", "Forum/emoticons/ermm.png", use_staticfiles=True),
	ColonSurroundedSmilie("face", "Forum/emoticons/face.png", use_staticfiles=True),
	ColonSurroundedSmilie("getlost", "Forum/emoticons/getlost.png", use_staticfiles=True),
	ColonSurroundedSmilie("grin", "Forum/emoticons/grin.png", use_staticfiles=True),
	ColonSurroundedSmilie("happy", "Forum/emoticons/happy.png", use_staticfiles=True),
	ColonSurroundedSmilie("heart", "Forum/emoticons/heart.png", use_staticfiles=True),
	ColonSurroundedSmilie("kissing", "Forum/emoticons/kissing.png", use_staticfiles=True),
	ColonSurroundedSmilie("laughing", "Forum/emoticons/laughing.png", use_staticfiles=True),
	ColonSurroundedSmilie("ninja", "Forum/emoticons/ninja.png", use_staticfiles=True),
	ColonSurroundedSmilie("pinch", "Forum/emoticons/pinch.png", use_staticfiles=True),
	ColonSurroundedSmilie("pouty", "Forum/emoticons/pouty.png", use_staticfiles=True),
	ColonSurroundedSmilie("sad", "Forum/emoticons/sad.png", use_staticfiles=True),
	ColonSurroundedSmilie("shocked", "Forum/emoticons/shocked.png", use_staticfiles=True),
	ColonSurroundedSmilie("sick", "Forum/emoticons/sick.png", use_staticfiles=True),
	ColonSurroundedSmilie("sideways", "Forum/emoticons/sideways.png", use_staticfiles=True),
	ColonSurroundedSmilie("silly", "Forum/emoticons/silly.png", use_staticfiles=True),
	ColonSurroundedSmilie("sleeping", "Forum/emoticons/sleeping.png", use_staticfiles=True),
	ColonSurroundedSmilie("smile", "Forum/emoticons/smile.png", use_staticfiles=True),
	ColonSurroundedSmilie("tongue", "Forum/emoticons/tongue.png", use_staticfiles=True),
	ColonSurroundedSmilie("unsure", "Forum/emoticons/unsure.png", use_staticfiles=True),
	ColonSurroundedSmilie("wassat", "Forum/emoticons/wassat.png", use_staticfiles=True),
	ColonSurroundedSmilie("whistling", "Forum/emoticons/whistling.png", use_staticfiles=True),
	ColonSurroundedSmilie("wink", "Forum/emoticons/wink.png", use_staticfiles=True),
	ColonSurroundedSmilie("woot", "Forum/emoticons/woot.png", use_staticfiles=True),
	ColonSurroundedSmilie("wub", "Forum/emoticons/wub.png", use_staticfiles=True),
	GeneralSmilie(r':(-)?\)', "Forum/emoticons/smile.png", use_staticfiles=True),
	GeneralSmilie(r':(-)?\|', "Forum/emoticons/pouty.png", use_staticfiles=True),
	GeneralSmilie(r'(x|X)D', "Forum/emoticons/laughing.png", use_staticfiles=True),
	GeneralSmilie(r'B\)', "Forum/emoticons/cool.png", use_staticfiles=True),
	GeneralSmilie(r':\(', "Forum/emoticons/sad.png", use_staticfiles=True),
	GeneralSmilie(r':(\'|\&#39;)\(', "Forum/emoticons/crying.png", use_staticfiles=True),
	GeneralSmilie(r';\)', "Forum/emoticons/wink.png", use_staticfiles=True),
	GeneralSmilie(r'(\&lt;|\<)3', "Forum/emoticons/heart.png", use_staticfiles=True),
	GeneralSmilie(r'(\^|n)(\.|\_)?(\^|n)', "Forum/emoticons/happy.png", use_staticfiles=True),
	GeneralSmilie(r':(-)?(p|P)', "Forum/emoticons/tongue.png", use_staticfiles=True),
	GeneralSmilie(r':(o|O)', "Forum/emoticons/shocked.png", use_staticfiles=True),
	GeneralSmilie(r'(\&gt;|\>)(\.|\_)?(\&lt;|\<)', "Forum/emoticons/pinch.png", use_staticfiles=True),
	GeneralSmilie(r'(\&gt;|\>)(\.|\_)?(\&gt;|\>)', "Forum/emoticons/getlost.png", use_staticfiles=True),
	GeneralSmilie(r':(-)?\*', "Forum/emoticons/kissing.png", use_staticfiles=True),
	GeneralSmilie(r'(O.o|O.O|o.O)', "Forum/emoticons/woot.png", use_staticfiles=True),
	GeneralSmilie(r':(-)?D', "Forum/emoticons/grin.png", use_staticfiles=True),
]

def render_emoticons(text):
	for sm in _em_list:
		text = sm.parse(text)
	return text
