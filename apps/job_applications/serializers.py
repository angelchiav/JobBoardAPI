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

    technology = serializers.ListField(
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
            'technology',
            'technologies',
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
            'applications_count',
            'is_open'
        ]
        read_only_fields = ['id', 'publication_date', 'employer_name', 'employer_website', 'technologies',
            'status_display', 'modality_display', 'applications_count', 'salary_range', 'is_open']

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

        today = timezone.now().date()

        if value and value <= today:
            raise serializers.ValidationError(
                "Closing date must be in the future."
            )

        return value

    def create(self, validated_data):
        technology_names = validated_data.pop('technologies', [])
        validated_data['employer'] = self.context['request'].user.employer_profile

        vacancy = super().create(validated_data)

        for tech_name in technology_names:
            technology, created = Technology.objects.get_or_create(
                name=tech_name.title()
            )
            vacancy.technologies.add(technology)
        
        return vacancy
        
    def update(self, instance, validated_data):
        technology_names = validated_data.pop('technology', None)
        instance = super().update(instance, validated_data)

        if technology_names is not None:
            instance.technologies.clear()
            for tech_name in technology_names:
                technology, created = Technology.objects.get_or_create(
                    name=tech_name.title()
                )
                instance.technologies.add(technology)

        return instance
    
class VacancyListSerializer(serializers.ModelSerializer):
    technologies = serializers.StringRelatedField(many=True)
    employer_name = serializers.CharField(source='employer.company_name', read_only=True)
    modality_display = serializers.CharField(source='get_modality_display', read_only=True)
    salary_range = serializers.ReadOnlyField()
    applications_count = serializers.ReadOnlyField()

    class Meta:
        model = Vacancy
        fields = [
            'id',
            'title',
            'employer_name',
            'technologies',
            'modality',
            'modality_display',
            'location',
            'salary_range',
            'publication_date',
            'state',
            'applications_count'
        ]

class VacancyCreateSerializer(serializers.ModelSerializer):
    technology_names = serializers.ListField(
        child=serializers.CharField(max_length=50, required=False)
    )
    
    class Meta:
        model = Vacancy
        fields = [
            'title',
            'description',
            'technologies',
            'technology_names',
            'modality',
            'location',
            'salary_min',
            'salary_max',
            'experience_required',
            'closing_date'
        ]
    
    def create(self, validated_data):
        technology_names = validated_data.pop('technologies')
        validated_data['employer'] = self.context['request'].user.employer_profile
        vacancy = super().create(validated_data)

        for tech_name in technology_names:
            technology, created = Technology.objects.get_or_create(
                name=tech_name.title()
            )
            vacancy.technologies.add(technology)
        
        return vacancy
    
class JobApplicationSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    employee_email = serializers.CharField(source='employee.user.email', read_only=True)
    vacancy_title = serializers.CharField(source='vacancy.title', read_only=True)
    company_name = serializers.CharField(source='vacancy.employer.company_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    class Meta:
        model = JobApplication
        fields = [
            'id',
            'employee',
            'vacancy',
            'status',
            'cover_letter',
            'applied_date',
            'last_updated',
            'notes',
            'salary_expectation',
            'availability_date',
            'can_withdraw',
            'is_active'
        ]
        read_only_fields = ['id', 'applied_data','last_updated', 'availability_date', 'employee_name', 'employee_email', 'vacancy_title', 'company_name', 'status_display', 'can_withdraw', 'is_active']
        extra_kwargs = {
            'cover_letter': {'required': False},
            'notes': {'required': False, 'write_only': True},
        }
    
    def validate_cover_letter(self, value):
        if len(value) > 1000:
            raise serializers.ValidationError(
                "Cover letter cannot exceed 1000 characters."
            )
        return value
    
    def validate_salary_expectation(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError(
                "Salary expectation cannot be negative."
            )
        
        if value is not None and value > 1000000:
            raise serializers.ValidationError(
                "Salary expectation seems unrealistic."
            )
        return value
    
    def validate_availability_date(self, value):
        if value and value < timezone.now().date():
            raise serializers.ValidationError(
                "Availability date cannot be in the past."
            )
        return value
    
    def validate(self, data):
        if 'vacancy' in data and data['vacancy'].state == 'C':
            raise serializers.ValidationError(
                "This vacancy is closed."
            )
        return data
    
class JobApplicationListSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    vacancy_title = serializers.CharField(source='vacancy.title', read_only=True)
    company_name = serializers.CharField(source='vacancy.employer.company_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = JobApplication
        fields = [
            'id',
            'employee_name',
            'vacancy_title',
            'company_name',
            'status',
            'status_display',
            'applied_date',
            'salary_expectation'
        ]

class JobApplicationCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = JobApplication
        fields = [
            'vacancy',
            'cover_letter',
            'salary_expectation',
            'availability_date'
        ]
    
    def create(self, validated_data):
        validated_data['employee'] = self.context['request'].user.employee_profile
        return super().create(validated_data)
    
class JobApplicationUpdateSerializer(serializers.ModelSerializer):
    reason = serializers.CharField(write_only=True, required=False, max_length=500)

    class Meta:
        model = JobApplication
        fields = ['status', 'notes', 'reason']
        extra_kwargs = {
            'status': {'required': False},
            'notes': {'required': False},
            'reason': {'required': False}
        }

    def update(self, instance, validated_data):
        reason = validated_data.pop('reason', '')
        previous_status = instance.status

        instance = super().update(instance, validated_data)

        if previous_status != instance.status:
            ApplicationStatusHistory.objects.create(
                application=instance,
                previous_status=previous_status,
                new_status=instance.status,
                changed_by=self.context['request'].user,
                reason=reason
            )

        return instance