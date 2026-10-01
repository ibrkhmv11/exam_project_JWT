from django.contrib import admin

from .models import (
    Category,
    Product,
    Like,
    Comment,
)


admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Like)
admin.site.register(Comment)