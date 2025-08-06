from rest_framework import serializers, permissions
from .models import (
    JobApplication, 
    ApplicationDocument, 
    ApplicationStatusHistory, 
    Interview,
    Technology,
    Vacancy
)
from django.utils import timezone

class TechnologySerializer(serializers.ModelSerializer):
    class Meta:
        model = Technology
        fields = [
            'id',
            'name'
        ]
        read_only_fields = ['id']

    def validate_name(self, value):
        if len(value) < 2:
            raise serializers.ValidationError(
                "The technology name has to be at least 3 characters long."
            )
        return value.title()

class VacancySerializer(serializers.ModelSerializer):
    technologies = TechnologySerializer(
        many=True,
        read_only=True
    )

    technology_name = serializers.ListField(
        child=serializers.CharField(max_length=50),
        write_only=True,
        required=False
    )

    employer_name = serializers.CharField(
        source='employer.company_name',
        read_only=True
    )

    employer_website = serializers.CharField(
        source='employer.company_website',
        read_only=True
    )

    status_display = serializers.CharField(
        source='get_state_display',
        read_only=True
    )

    modality_display = serializers.CharField(
        source='get_modality_display',
        read_only=True
    )

    applications_count = serializers.ReadOnlyField()
    salary_range = serializers.ReadOnlyField()
    is_open = serializers.ReadOnlyField()

    class Meta:
        model = Vacancy
        fields = [
            'id',
            'employer',
            'employer_name',
            'employer_website',
            'title',
            'description',
            'technologies',
            'technology_names',
            'modality',
            'modality_display',
            'location',
            'salary_min',
            'salary_max',
            'salary_range',
            'experience_required',
            'publication_date',
            'closing_date',
            'state',
            'status_display',
            'views_count',
            'applications_count',
            'is_open'
        ]
        read_only_fields = ['id', 'publication_date', 'employer_name', 'employer_website', 'status_display', 'modality_display', 'applications_count', 'salary_range', 'is_open', 'views_count']

        def validate_title(self, value):
            if len(value) < 5:
                raise serializers.ValidationError(
                    "Title must be at least 5 characters long."
                )
            return value
        
        def validate_description(self, value):
            if len(value) < 20:
                raise serializers.ValidationError(
                    "Description must be at least 20 characters long."
                )
            return value
        
        def validate_closing_date(self, value):
            if value and value <= timezone.now():
                raise serializers.ValidationError(
                    "Closing date must be in the future."
                )
            return value
        
        def validate(self, data):
            salary_min = data.get('salary_min')
            salary_max = data.get('salary_max')

            if salary_min and salary_max:
                if salary_min >= salary_max:
                    raise serializers.ValidationError(
                        "Minimum salary has to be less than maximum salary."
                    )
            
            return data
        
        def create(self, validated_data):
            technology_names = validated_data.pop('technology_names', [])
            validated_data['employer'] = self.context['request'].user.employer_profile

            vacancy = super().create(validated_data)

            for tech_name in technology_names:
                technology, created = Technology.objects.get_or_create(
                    name=tech_name.title()
                )
                vacancy.technologies.add(technology)
            
            return vacancy
        
        def update(self, instance, validated_data):
            technology_names = validated_data.pop('technology_names', None)
            instance = super().update(instance, validated_data)

            if technology_names is not None:
                instance.technologies.clear()
                for tech_name in technology_names:
                    technology, created = Technology.objects.get_or_create(
                        name=tech_name.title()
                    )
                instance.technologies.add(technology)

            return instance