from django.contrib import admin

from .models import User, Follow


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'is_active'
    )
    list_filter = (
        'is_active',
    )
    search_fields = (
        'email__istartswith',
        'username__istartswith'
    )
    fieldsets = (
        (None, {
            'fields': (
                'username', 'first_name', 'last_name', 'email', 'is_active'
            )
        }),
    )


admin.site.register(Follow)
