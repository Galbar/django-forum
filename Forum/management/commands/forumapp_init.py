# -*- coding: utf-8 -*-
from Forum.models import *
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = u'Initializes the Forum app.'

    def handle(self, *args, **options):
        self.stdout.write("Check if \"Forum.forum_admin\" permission exists.")
        content_type = ContentType.objects.get_for_model(Forum)
        perm = Permission(codename='forum_admin',name='Is Forum administrator moderator',content_type=content_type)
        try:
            perm = Permission.objects.get(codename=perm.codename, name=perm.name, content_type=perm.content_type)
            self.stdout.write("Already exists. No need to create it.")
        except:
            self.stdout.write("Create \"Forum.forum_admin\" permission.")
            perm.save()


        self.stdout.write("Check if \"Forum Admins\" group exists.")
        group = Group(name="Forum Admins")
        try:
            Group.objects.get(name="Forum Admins")
            self.stdout.write("Already exists. No need to create it.")
        except:
            self.stdout.write("Create \"Forum Admins\" group.")
            group.save()
            group.permissions.add(perm)


        self.stdout.write("Check if Main Forum exists.")
        try:
            Forum.objects.get(id=0)
            self.stdout.write("Already exists. No need to create it.")
        except:
            f_name = raw_input("Main Forum name (if empty it'll be 'Main Forum'):")
            if f_name == "":
                f_name = "Main Forum"

            sf_desc = raw_input("Description for "+ f_name+ ":")
            self.stdout.write("Create Main Forum.")
            f = Forum(name=f_name)
            f.local_id = 0
            f.save()
            sf = Subforum(
                local_id=0,
                name=f_name,
                forum=f,
                description="Main forum"
                )
            sf.save()

        self.stdout.write("Done.")