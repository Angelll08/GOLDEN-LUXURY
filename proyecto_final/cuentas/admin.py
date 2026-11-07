from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (('Extra', {'fields': ('telefono',)}),)


# Ocultar del admin los menús técnicos que no se usan (siguen funcionando por dentro)
for modelo in (Group, Site, EmailAddress, SocialApp, SocialAccount, SocialToken):
    try:
        admin.site.unregister(modelo)
    except admin.sites.NotRegistered:
        pass
