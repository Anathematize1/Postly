from django.contrib import admin

from .models import Category, Location, Post, Comment


admin.site.empty_value_display = 'Не задано'


def make_published(modeladmin, request, queryset):
    queryset.update(is_published=True)


make_published.short_description = 'Опубликовать выбранные'


def make_unpublished(modeladmin, request, queryset):
    queryset.update(is_published=False)


make_unpublished.short_description = 'Снять с публикации выбранные'


COMMON_ACTIONS = (make_published, make_unpublished)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'description',
                    'is_published', 'created_at')
    list_filter = ('is_published', 'created_at')
    list_editable = ('is_published', 'slug')
    search_fields = ('title', 'slug', 'description')
    ordering = ('-created_at',)
    list_per_page = 25
    actions = COMMON_ACTIONS


class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published', 'created_at')
    list_filter = ('is_published', 'created_at')
    list_editable = ('is_published',)
    search_fields = ('name',)
    ordering = ('name',)
    list_per_page = 25
    actions = COMMON_ACTIONS


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'pub_date',
                    'is_published', 'created_at')
    list_filter = ('is_published', 'category', 'author', 'pub_date')
    search_fields = ('title', 'text', 'category__title', 'author__username')
    list_select_related = ('category', 'author', 'location')
    list_editable = ('is_published', 'author', 'category')
    date_hierarchy = 'pub_date'
    ordering = ('-pub_date', '-created_at')
    list_per_page = 25
    actions = COMMON_ACTIONS


class CommentAdmin(admin.ModelAdmin):
    list_display = ('text', 'author', 'post', 'created_at')
    list_filter = ('author', 'created_at', 'post')
    search_fields = ('text', 'author__username', 'post__title')
    list_select_related = ('author', 'post')
    ordering = ('-created_at',)
    list_per_page = 25


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
