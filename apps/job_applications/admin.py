from django.contrib import admin
from .models import Technology, Vacancy, JobApplication, ApplicationStatusHistory, Interview, ApplicationDocument

# Register your models here.

admin.site.register(Vacancy)
