from django.contrib import admin
from django.contrib.auth.models import Permission

# Register your models here.

from .models import Key


class KeyAdmin(admin.ModelAdmin):
    model = Key
    list_display = ('symbols', 'verbose_status')


admin.site.register(Key, KeyAdmin)
admin.site.register(Permission)
