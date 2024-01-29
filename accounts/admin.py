from django.contrib import admin
from accounts.models import Profile, Panel


@admin.register(Panel)
class PanelAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'deadline',
        'price',
    )

    fields = (
        'name',
        'deadline',
        'price',
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'panel',
        'created_at_display',
        'updated_at_display',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    fields = (
        'user',
        'panel',
        'created_at',
        'updated_at',
    )

    @admin.display(description="تاریخ ایجاد", empty_value='???')
    def created_at_display(self, obj):
        data_time = str(obj.created_at.strftime('%Y-%m-%d - %H:%M'))
        return data_time

    @admin.display(description="تاریخ بروزرسانی", empty_value='???')
    def updated_at_display(self, obj):
        data_time = str(obj.updated_at.strftime('%Y-%m-%d - %H:%M'))
        return data_time
