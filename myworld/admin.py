from django.contrib import admin
from .models import UserProfile, SavedItem, Like, Comment

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'bio']
    search_fields = ['user__username', 'bio']

@admin.register(SavedItem)
class SavedItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'platform', 'category', 'is_public', 'created_at']
    list_filter = ['platform', 'category', 'is_public', 'created_at']
    search_fields = ['title', 'description', 'url', 'user__username']
    date_hierarchy = 'created_at'

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'item', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'item__title']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'item', 'content_summary', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'item__title', 'content']

    def content_summary(self, obj):
        return obj.content[:50]
    content_summary.short_description = 'Content'
