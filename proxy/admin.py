
from django.contrib import admin
from .models import Proxies
# Register your models here.
@admin.register(Proxies)
class ProxiesAdmin(admin.ModelAdmin):
    list_display = ["name", "showing_created_at", "activate"]

    @admin.display()
    def showing_created_at(self, obj):
        return obj.created_time.strftime("%y/%m/%d %H:%M")
    
