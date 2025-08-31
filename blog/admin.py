from django.contrib import admin
from .models import Article, Category, Post, Activity

admin.site.register(Category)
admin.site.register(Article)
admin.site.register(Activity)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'status')
    list_filter = ('status', 'created_at', 'categories')
    search_fields = ('title', 'text', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    show_facets = admin.ShowFacets.ALWAYS
