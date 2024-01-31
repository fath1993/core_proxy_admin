from django.contrib import admin
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.contrib.auth.models import User
from django.db.models import Q

from accounts.models import Profile, Panel
from utils.utils import random_name, random_password

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
    actions_on_top = True

    list_display = (
        'username',
        'password',
        'panel',
        'created_at_display',
        'updated_at_display',
        'created_by',
    )

    list_filter = (
        'user__is_staff',
    )

    readonly_fields = (
        'username',
        'created_at',
        'updated_at',
        'created_by',
    )

    fields = (
        'username',
        'password',
        'panel',
        'created_at',
        'updated_at',
        'created_by',
    )

    def save_model(self, request, instance, form, change):
        instance = form.save(commit=False)
        if not change:
            instance.created_by = request.user
        instance.save()
        form.save_m2m()
        return instance

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
            q = Q()
            q &= Q(**{f'user': request.user})
            q |= (Q(user__is_staff=False) & Q(created_by=request.user))
            qs = qs.filter(q)
            pass
        return qs

    def has_add_permission(self, request):
        return False

    def changelist_view(self, request, extra_context=None):
        if 'action' in request.POST and request.POST['action'] == 'create_profile':
            if not request.POST.getlist(ACTION_CHECKBOX_NAME):
                post = request.POST.copy()
                for u in Profile.objects.all():
                    post.update({ACTION_CHECKBOX_NAME: str(u.id)})
                request._set_post(post)
        return super(ProfileAdmin, self).changelist_view(request, extra_context)

    @admin.action(description='ساخت کاربر')
    def create_profile(self, request, queryset):
        print(1)
        username = random_name()
        password = random_password()
        new_user = User.objects.create_user(username=username)
        new_user.set_password(password)
        Profile.objects.create(user=new_user, username=username, password=password, created_by=request.user)

    create_profile.acts_on_all = True

    actions = (
        'create_profile',
    )