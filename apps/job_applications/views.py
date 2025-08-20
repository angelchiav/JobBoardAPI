from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets, status
from .models import Technology, Vacancy, JobApplication, ApplicationStatusHistory, Interview, ApplicationDocument
from .serializers import TechnologySerializer, VacancySerializer, VacancyListSerializer, VacancyCreateSerializer, JobApplicationSerializer, JobApplicationListSerializer, JobApplicationCreateSerializer, JobApplicationUdpateSerializer


# ya hay funciones crud de forma automatica
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
