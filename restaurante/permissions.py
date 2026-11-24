from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.shortcuts import render
from rest_framework.permissions import BasePermission


def obter_perfil(user):
    if not user or not user.is_authenticated:
        return None
    try:
        return user.perfil
    except ObjectDoesNotExist:
        return None


def org_atual(request):
    perfil = obter_perfil(request.user)
    if perfil is None:
        return None
    return perfil.organizacao


def perfil_obrigatorio(view_func):
    @login_required
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        perfil = obter_perfil(request.user)
        if perfil is None:
            return render(
                request,
                'restaurante/sem_perfil.html',
                status=403,
            )
        request.perfil = perfil
        request.org = perfil.organizacao
        return view_func(request, *args, **kwargs)

    return _wrapped


def papel_requerido(*papeis_permitidos):
    def decorator(view_func):
        @perfil_obrigatorio
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if request.perfil.papel not in papeis_permitidos:
                raise PermissionDenied('Você não tem permissão para acessar esta funcionalidade.')
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator


class TemPerfilOrganizacao(BasePermission):
    message = 'Usuário autenticado não possui perfil vinculado a uma organização.'

    def has_permission(self, request, view):
        return obter_perfil(request.user) is not None


class IsAdminOrganizacao(BasePermission):
    message = 'Apenas administradores da organização podem executar esta ação.'

    def has_permission(self, request, view):
        perfil = obter_perfil(request.user)
        if perfil is None:
            return False
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return perfil.eh_admin
