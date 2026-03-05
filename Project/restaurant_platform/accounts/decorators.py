from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from functools import wraps


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):

            if request.user.role not in roles:
                return redirect("login")

            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator
