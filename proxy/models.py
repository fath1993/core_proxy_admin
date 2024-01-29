from django.contrib.auth.models import User
from django.db import models
from django_jalali.db import models as jmodel
from utils.utils import random_name


class Proxy(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False, editable=False, verbose_name="نام")
    code = models.CharField(max_length=255, null=False, blank=False, verbose_name="کد")
    is_active = models.BooleanField(default=True, verbose_name="وضعیت")
    created_at = jmodel.jDateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = jmodel.jDateTimeField(auto_now=True, verbose_name='تاریخ بروز رسانی')
    belong_to = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, verbose_name='متعلق به کابر')

    def __str__(self):
        return f'name: {self.name} | code: {self.code}'

    class Meta:
        verbose_name = 'پروکسی'
        verbose_name_plural = "پروکسی ها"

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = random_name()
        super().save(*args, **kwargs)
