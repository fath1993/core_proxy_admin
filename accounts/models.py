from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django_jalali.db import models as jmodel


class Panel(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False, verbose_name="نام پنل")
    deadline = models.PositiveIntegerField(default=30, null=False, blank=False, verbose_name="مدت زمان بر اساس روز")
    price = models.DecimalField(max_digits=6, decimal_places=2, null=False, blank=False, verbose_name="قیمت")

    def __str__(self):
        return f"$ {self.name}, {self.deadline}, {self.price} "

    class Meta:
        verbose_name = "مدیریت پنل و فروش"
        verbose_name_plural = "مدیریت پنل ها و فروش"


class Profile(models.Model):
    user = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE, verbose_name="کاربر")
    username = models.CharField(max_length=255, null=True, blank=True, editable=False, verbose_name='نام کاربری')
    password = models.CharField(max_length=255, null=True, blank=True, verbose_name='کلمه عبور')
    panel = models.ForeignKey(Panel, null=True, blank=True, on_delete=models.PROTECT, verbose_name="پنل")
    created_at = jmodel.jDateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = jmodel.jDateTimeField(auto_now=True, verbose_name='تاریخ بروز رسانی')
    created_by = models.ForeignKey(User, related_name='profile_created_by', null=False, blank=False, on_delete=models.CASCADE, verbose_name="ساخته شده توسط")

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'پروفایل'
        verbose_name_plural = 'پروفایل ها'

    def save(self, *args, **kwargs):
        if self.user and self.password:
            user = self.user
            user.set_password(self.password)
            user.save()
        super().save(*args, **kwargs)


@receiver(post_save, sender=User)
def auto_create_user_profile(sender, instance, created, **kwargs):
    if instance.is_staff or instance.is_superuser:
        try:
            Profile.objects.get(user=instance)
        except:
            Profile.objects.create(user=instance, username=instance.username, created_by=User.objects.get(username='admin'))



@receiver(post_delete, sender=Profile)
def auto_delete_user_on_profile_delete(sender, instance, **kwargs):
    try:
        instance.user.delete()
        related_profiles = Profile.objects.filter(created_by=instance.user).delete()
        for related_profile in related_profiles:
            try:
                related_profile.user.delete()
            except:
                pass
    except:
        pass