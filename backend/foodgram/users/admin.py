from django.contrib import admin
from users.models import User
from recipes.models import Follow


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'role', 'password'
    )
    search_fields = ('username',)
    list_filter = ('username',)
    empty_value_display = '-пусто-'


class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'author'
    )
    search_fields = ('user',)
    list_filter = ('user',)
    empty_value_display = '-пусто-'


admin.site.register(Follow, FollowAdmin)
admin.site.register(User, UserAdmin)
