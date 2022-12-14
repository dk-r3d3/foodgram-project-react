from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    model = User
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
    )
    list_filter = ('username', 'email')
    search_fields = ('username', 'email')
