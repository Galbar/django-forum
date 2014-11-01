import re
from Forum.settings import *

def user_has_permission(perm, user):
	if perm == "none":
		return user.has_perm("Forum.forum_admin")
	if re.compile(r'^\d+\.public$').search(perm):
		return True
	return user.has_perm("Forum."+perm)

def check_slug(instace, slug):
	if (instace.slug() == slug):
		return True
	return False