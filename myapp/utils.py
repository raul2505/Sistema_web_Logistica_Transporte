# app/utils.py
from django.core.exceptions import PermissionDenied

def role_required(role_name):
    """ Decorador para permitir acceso solo a usuarios con un rol específico """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated or not request.user.has_role(role_name):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
