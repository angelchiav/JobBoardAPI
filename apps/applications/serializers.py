from rest_framework import serializers
from .models import Technology, Vacancy

class TechnologySerializer(serializers.Serializer):
    class Meta:
        model = Technology
        fields = [
            'id',
            'name'
        ]
        read_only_fields = ['id']
    
    def validate_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError(
                "Technology name cannot be least than 3 characters."
            )
        return value
    
class VacancySerializer(serializers.Serializer):
    class Meta:
        model = Vacancy
        fields = [
            'id',
            "title", 
            "description", 
            "technologies", 
            "modality", 
            "location", 
            "publication_date", 
            "state"
        ]
        read_only_fields = ['id', 'publication_date', 'state']

    def validate_title(self, value):
        if len(value) > 50:
            raise serializers.ValidationError(
                "Length of title can't be greater than 50 characters."
            )
        return value

    def validate_state(self, value):
        if not value in ['O', 'C']:
            raise serializers.ValidationError(
                "The state is not valid."
            )
        return value
    
