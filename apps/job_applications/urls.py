from django.urls import path, include
from .views import VacancyViewSet, ThechnologyViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'vacancies', VacancyViewSet, basename='vacancy')
router.register(r'technologies', ThechnologyViewSet, basename='technology')

urlpatterns = [
    path("", include(router.urls)),
]