from django.contrib import admin
from .models import MenuItem

# Register your models here.
@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_available')
    list_filter = ('is_available',)
    search_fields = ('name',)

from .models import CafeItem
from django.utils.html import format_html

@admin.register(CafeItem)
class CafeItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'image_preview')
    search_fields = ('name',)
    list_per_page = 20

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="60" height="60" style="border-radius:8px;" />',
                obj.image.url
            )
        return "No Image"

    image_preview.short_description = 'Preview'
