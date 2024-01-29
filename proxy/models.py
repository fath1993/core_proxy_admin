from django.db import models
from user.models import random_name
from django_jalali.db import models as jmodels
from django.contrib.auth.models import User
# Create your models here.

class Proxies(models.Model):
    name = models.CharField(max_length=10, default = random_name, verbose_name="نام پروکسی")
    proxy_code = models.CharField(max_length=1000, primary_key=True, verbose_name="پروکسی")
    created_time = jmodels.jDateTimeField(auto_now_add=True, verbose_name="زمان ثبت")
    activate = models.BooleanField(default = True, verbose_name="فعال")


    class Meta:
        verbose_name_plural = "لیست پروکسی"
