import django.dispatch

# Publication
thread_published  = django.dispatch.Signal(providing_args=["thread"])
post_published  = django.dispatch.Signal(providing_args=["post"])

# Votes
upvote = django.dispatch.Signal(providing_args=["user", "post"])
downvote = django.dispatch.Signal(providing_args=["user", "post"])
positive_score_event = django.dispatch.Signal(providing_args=["post"])
negative_score_event = django.dispatch.Signal(providing_args=["post"])