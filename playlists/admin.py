from django.contrib import admin
from .models import Playlist, Photo, Song, VpnConfig


admin.site.register(Playlist)
admin.site.register(Photo)
admin.site.register(Song)


@admin.register(VpnConfig)
class VpnConfigAdmin(admin.ModelAdmin):
    list_display = ('flag', 'name', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    list_display_links = ('name',)
    ordering = ('order',)
    search_fields = ('name',)
    fieldsets = (
        ('اطلاعات سرور', {
            'fields': ('name', 'flag', 'is_active', 'order')
        }),
        ('کانفیگ', {
            'fields': ('url',),
            'classes': ('wide',),
        }),
    )
