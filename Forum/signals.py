import django.dispatch

# pizza_done = django.dispatch.Signal(providing_args=["toppings", "size"])

# New Post
new_post = django.dispatch.Signal(providing_args=[""])

# Votes recieved
upvote_recieved = django.dispatch.Signal(providing_args=[""])
downvote_recieved = django.dispatch.Signal(providing_args=[""])

# Votes given
upvote_given = django.dispatch.Signal(providing_args=[""])
downvote_given = django.dispatch.Signal(providing_args=[""])