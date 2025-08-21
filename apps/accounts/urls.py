from django.urls import path, include
from .views import UserViewSet, EmployerViewSet, EmployeeViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'employers', EmployerViewSet, basename='employer')
router.register(r'employees', EmployeeViewSet, basename='employee')

urlpatterns = [
    path("", include(router.urls)),
]