from django.contrib import admin
from .models import Article, Category, Post

admin.site.register(Category)
admin.site.register(Post)
admin.site.register(Article)
