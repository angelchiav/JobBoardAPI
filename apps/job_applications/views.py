from django.db.models import Prefetch
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Technology, Vacancy, JobApplication, ApplicationStatusHistory
from .serializers import (
    TechnologySerializer,
    VacancySerializer,
    VacancyListSerializer,
    VacancyCreateSerializer,
    JobApplicationSerializer,
    JobApplicationListSerializer,
    JobApplicationCreateSerializer,
    JobApplicationUpdateSerializer
)


class IsEmployer(permissions.BasePermission):

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and hasattr(request.user, "employer_profile")
        )
    
class IsEmployerOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, "employer_profile")
            and obj.employer == request.user.employer_profile
        )

class IsApplicationParticipantOrReadOnly(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        if not (user and user.is_authenticated):
            return False
        is_employee_owner = hasattr(user, "employee_profile") and obj.employee == user.employee_profile
        is_employer_owner = hasattr(user, "employer_profile") and obj.vacancy.employer == user.employer_profile
        return is_employee_owner or is_employer_owner
    
class TechnologyViewSet(viewsets.ModelViewSet):
    queryset = Technology.objects.all().order_by("name")
    serializer_class = TechnologySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["name", "id"]
    
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        # Writes require authentication (either role)
        return [permissions.IsAuthenticated()]