from django.contrib import admin, messages
from django.http.request import HttpRequest
from django.db.models import QuerySet
from django.contrib.auth.admin import UserAdmin

from users.models import User


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        'username',
        'is_active',
        'email',
        'first_name',
        'last_name',
        'is_verified',
        'is_staff',
    )
    list_filter = (
        'created_at',
        'is_active',
        'is_verified',
        'is_staff',
    )
    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name',
    )
    fieldsets = (
        (None, {'fields': ('email', 'username', 'avatar')}),
        ('Permissions', {
            'fields': ('is_verified', 'is_staff')
        }),
        ('Personal informations', {
            'fields': ('first_name', 'last_name', 'title')
        })
    )
    
    actions = ('activate', 'desactivate', 'verify', 'unverify')
    
    def activate(modeladmin, request: HttpRequest, queryset: QuerySet) -> None:
        queryset.update(is_active=True)
        messages.success(
            request, 'Selected User(s) are now activate!')

    def activate(modeladmin, request: HttpRequest, queryset: QuerySet) -> None:
        queryset.update(is_active=False)
        messages.success(
            request, 'Selected User(s) are now desactivate!')

    def verify(modeladmin, request: HttpRequest, queryset: QuerySet) -> None:
        queryset.update(is_verified=True)
        messages.success(
            request, 'Selected User(s) are now verified!')

    def unverify(modeladmin, request: HttpRequest, queryset: QuerySet) -> None:
        queryset.update(is_verified=False)
        messages.success(
            request, 'Selected User(s) are now unverified!')
