from django.db.models.signals import post_save
from Forum.models import *

def forum(sender, instance, *args, **kwargs):
	if kwargs["created"]:
		p = instance.add_perm("Forum admin", "[Forum:"+str(instance.local_id)+"] Administration permission")
		g = instance.add_group("Administrators")
		g.permissions.add(p)
		g.save()
		instance.admin_permission = p.codename;
		Subforum(
		local_id = instance.subforum_set.count(),
		name = instance.name,
		forum = instance,
		).save()

		p = instance.add_perm("member", "[Forum:"+str(instance.local_id)+"] Membership token")
		p.save()
		instance.member_permission = p.codename
		sf = instance.main_forum
		g = instance.add_group("Moderators")
		g.permissions.add(
			p,
			instance.perms().get(codename=sf.view_permission),
			instance.perms().get(codename=sf.mod_permission),
			instance.perms().get(codename=sf.create_thread_permission),
			instance.perms().get(codename=sf.reply_thread_permission)
		)
		g.save()
		g = instance.add_group("Members")
		g.permissions.add(
			p,
			instance.perms().get(codename=sf.view_permission),
			instance.perms().get(codename=sf.create_thread_permission),
			instance.perms().get(codename=sf.reply_thread_permission)
		)
		g.save()
		g = instance.add_group("Visitors")
		g.permissions.add(
			instance.perms().get(codename=sf.view_permission)
		)
		g.save()
		g = instance.add_group("Banned Users")
		g.permissions.add(
			p,
			instance.perms().get(codename=sf.no_view_permission),
			instance.perms().get(codename=sf.no_mod_permission),
			instance.perms().get(codename=sf.no_create_thread_permission),
			instance.perms().get(codename=sf.no_reply_thread_permission)
		)
		g.save()

		instance.save()

def subforum(sender, instance, *args, **kwargs):
	if kwargs["created"]:
		instance.view_permission = instance.forum.add_perm("Subforum."+str(instance.local_id)+".view_permission", "[Forum:"+str(instance.forum.local_id)+" Subforum:"+str(instance.local_id)+"] Can view").codename
		instance.mod_permission = instance.forum.add_perm("Subforum."+str(instance.local_id)+".mod_permission", "[Forum:"+str(instance.forum.local_id)+" Subforum:"+str(instance.local_id)+"] Can moderate").codename
		instance.create_thread_permission = instance.forum.add_perm("Subforum."+str(instance.local_id)+".create_thread_permission", "[Forum:"+str(instance.forum.local_id)+" Subforum:"+str(instance.local_id)+"] Can create thread").codename
		instance.reply_thread_permission = instance.forum.add_perm("Subforum."+str(instance.local_id)+".reply_thread_permission", "[Forum:"+str(instance.forum.local_id)+" Subforum:"+str(instance.local_id)+"] Can reply thread").codename
		instance.no_view_permission = instance.forum.add_perm("Subforum."+str(instance.local_id)+".no_view_permission", "[Forum:"+str(instance.forum.local_id)+" Subforum:"+str(instance.local_id)+"] Can't view").codename
		instance.no_mod_permission = instance.forum.add_perm("Subforum."+str(instance.local_id)+".no_mod_permission", "[Forum:"+str(instance.forum.local_id)+" Subforum:"+str(instance.local_id)+"] Can't moderate").codename
		instance.no_create_thread_permission = instance.forum.add_perm("Subforum."+str(instance.local_id)+".no_create_thread_permission", "[Forum:"+str(instance.forum.local_id)+" Subforum:"+str(instance.local_id)+"] Can't create thread").codename
		instance.no_reply_thread_permission = instance.forum.add_perm("Subforum."+str(instance.local_id)+".no_reply_thread_permission", "[Forum:"+str(instance.forum.local_id)+" Subforum:"+str(instance.local_id)+"] Can't reply thread").codename

		instance.save()

post_save.connect(receiver=forum, sender=Forum)
post_save.connect(receiver=subforum, sender=Subforum)
