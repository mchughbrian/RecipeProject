from django.contrib import admin
from .models import Recipe, Profile

# Register your models here.

admin.site.register(Recipe)
admin.site.register(Profile)

class RecipeAdmin(admin.ModelAdmin):
    ordering = ('user__id',)
    list_display = ('name', 'user_id_display',)

    def user_id_display(self, obj):
        return obj.user.id
    user_id_display.short_description = 'User ID'
