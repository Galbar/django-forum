Info
====
3 default permission for Subforum access permissions:
    - public : everybody, logged in or not
    - registered : only logged in users
    - none : only users in "Forum Admins" group

Forum Admins group:
    Users in this group have the Forum.forum_admin permission,
    giving them access to moderation everywhere in the forums.

Installation
============
After doing syncdb, execute forumapp_init for letting the app initialize some base configuration.