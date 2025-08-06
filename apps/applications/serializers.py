from rest_framework import serializers
from .models import Technology, Vacancy

class TechnologyListSerializer(serializers.Serializer):
    class Meta:
        model = Technology
        fields = "__all__"
        
        
class VacancyListSerializer(serializers.Serializer):
    class Meta:
        model = Vacancy
        fields = ["title", "description", "technologies", "modality", "location", "publication_date", "state"]
        
        