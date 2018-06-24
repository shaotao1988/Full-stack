from django.contrib import admin
from blogpost.models import BlogPost

# Register your models here.
class BlogPostAdmin(admin.ModelAdmin):
    exclude = ['posted']
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(BlogPost, BlogPostAdmin)
print("'Hello, it's my my first django project")