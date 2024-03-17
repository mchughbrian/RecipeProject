from django.contrib import admin
from .models import Recipe, Profile


class RecipeAdmin(admin.ModelAdmin):
    ordering = ('user__id',)  # This orders the recipes in the admin list view by user ID.
    list_display = ('name', 'user_id_display',)  # This specifies which columns to display.

    def user_id_display(self, obj):
        return obj.user.id
    user_id_display.short_description = 'User ID'  # This sets a custom column name.

    # If you want to make the User ID column sortable, you can add:
    user_id_display.admin_order_field = 'user__id'


# register model and the custom admin class
admin.site.register(Recipe, RecipeAdmin, Profile)