from django.contrib import admin
from django.contrib.auth.models import User

from proxy.models import Proxy


@admin.register(Proxy)
class ProxyAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'code',
        'is_active',
        'created_at_display',
        'updated_at_display',
        'belong_to',
    )

    readonly_fields = (
        'name',
        'created_at',
        'updated_at',
    )

    fields = (
        'name',
        'code',
        'is_active',
        'created_at',
        'updated_at',
        'belong_to',
    )

    @admin.display(description="تاریخ ایجاد", empty_value='???')
    def created_at_display(self, obj):
        data_time = str(obj.created_at.strftime('%Y-%m-%d - %H:%M'))
        return data_time

    @admin.display(description="تاریخ بروزرسانی", empty_value='???')
    def updated_at_display(self, obj):
        data_time = str(obj.updated_at.strftime('%Y-%m-%d - %H:%M'))
        return data_time

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(belong_to=request.user)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'belong_to':
            if request.user.is_superuser:
                kwargs['queryset'] = User.objects.filter(is_staff=True)
            else:
                kwargs['queryset'] = User.objects.filter(username=request.user.username)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)