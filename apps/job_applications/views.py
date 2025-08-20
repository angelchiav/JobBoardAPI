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
class ThechnologyViewSet(viewsets.ModelViewSet):
    queryset = Technology.objects.all()
    serializer_class = TechnologySerializer

    # crear tecnologia segun la información del serializer
    def createTechnology(self, request, *args, **kwargs):
        serializer = TechnologySerializer(data=request.data)

        if serializer.is_valid:
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)

        return Response(
            {"error": "register failed", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


class VacancyViewSet(viewsets.ModelViewSet):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer
    # filterset_fields = ('title') #filtrado por titulo

    # listar vacantes
    def listVacancy(self, request):
        queryset = Vacancy.objects.all()
        serializer = VacancySerializer(queryset, many=True)
        return Response(serializer.data)

    # crear vacante
    def createVacancy(self, request, *args, **kwargs):
        serializer = VacancyCreateSerializer(data=request.data)

        if serializer.is_valid:
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)

        return Response(
            {"error": "register failed", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

