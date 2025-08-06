from rest_framework.decorators import api_view
from rest_framework import permissions, viewsets
from .models import Technology, Vacancy
from .serializers import TechnologyListSerializer, VacancyListSerializer
from rest_framework.views import APIView
from rest_framework.response import Response

# Create your views here.

@api_view(["GET"])
def vacancy_list(request):
    vacancy = Vacancy.objects.all()
    serializers = VacancyListSerializer(vacancy, many=True)
    return Response(serializers.data)