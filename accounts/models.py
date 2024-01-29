from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
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
    panel = models.ForeignKey(Panel, null=True, blank=True, on_delete=models.PROTECT, verbose_name="پنل")
    created_at = jmodel.jDateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = jmodel.jDateTimeField(auto_now=True, verbose_name='تاریخ بروز رسانی')

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'پروفایل'
        verbose_name_plural = 'پروفایل ها'


@receiver(post_save, sender=User)
def auto_create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
