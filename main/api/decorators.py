from functools import wraps

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group, Permission
from rest_framework.response import Response
from rest_framework import status


def api_permission_required(perm):
    '''
    Декоратор для метода Viewset, проверяющий наличие у пользователя прав.
    Для анонимного пользователя предполагается наличие группы Anonymous,
    в которой указаны все его права.
    У суперпользователя права изначально все есть.
    '''
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if isinstance(perm, str):
                perms = [perm]
            else:
                perms = perm

            request = args[1]
            user = request.user

            check_passed = False

            if user.is_authenticated:
                if user.has_perms(perm) or user.is_superuser:
                    check_passed = True
            else:
                group = Group.objects.filter(name='Anonymous').first()
                if group:
                    count = group.permissions.filter(codename__in=perms).count()
                    if count == len(perms):
                        check_passed = True

            if check_passed:
                return func(*args, **kwargs)
            else:
                return Response(_("You have no permission"), status=status.HTTP_403_FORBIDDEN)

        return wrapper

    return decorator
