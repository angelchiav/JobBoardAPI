from django.urls import path
from . import views

urlpatterns = [
    path("vacancy_list", views.vacancy_list, name="vacancy_list")
]