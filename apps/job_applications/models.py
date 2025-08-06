from django.db import models
from django.core.exceptions import ValidationError
from apps.users.models import EmployeeProfile, EmployerProfile

class Technology(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True
    )

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Technology'
        verbose_name_plural = "Technologies"
        ordering = ['name']

class Vacancy(models.Model):
    STATUS_CHOICES = [
        ("O", "Open"),
        ("C", "Closed")
    ]

    MODALITY_CHOICES = [
        ("remote", "Remote"),
        ("onsite", "On-site"),
        ("hybrid", "Hybrid")
    ]

    employer = models.ForeignKey(
        EmployerProfile,
        on_delete=models.CASCADE,
        related_name="vacancies"
    )

    title = models.CharField(max_length=100)

    description = models.TextField(max_length=1000)

    technologies = models.ManyToManyField(
        Technology,
        related_name="vacancies",
        blank=True
    )

    modality = models.CharField(
        max_length=20,
        choices=MODALITY_CHOICES,
        default="hybrid"
    )

    location = models.CharField(max_length=100)

    salary_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum salary range."
    )

    salary_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum salary range."
    )

    experience_required = models.CharField(
        max_length=50,
        blank=True,
        help_text="Required years of experience (e.g. '2-5 years')."
    )

    publication_date = models.DateTimeField(
        auto_now_add=True
    )

    closing_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When applications close."
    )

    state = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default="O"
    )

    def clean(self):
        if self.salary_min and self.salary_max:
            if self.salary_min >= self.salary_max:
                raise ValidationError(
                    "Minimum salary must be less than maximum salary."
                )
            
        if self.closing_date and self.closing_date <= self.publication_date:
            raise ValidationError(
                "Closing date must be after publication date."
            )
        
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.employer.company_name} ({self.modality})"
    
    @property
    def is_open(self):
        return self.state == "O"
    
    @property
    def salary_range(self):
        if self.salary_min and self.salary_max:
            return f"${self.salary_min} - ${self.salary_max}"
        elif self.salary_min:
            return f"From ${self.salary_min}"
        elif self.salary_max:
            return f"Up to ${self.salary_max}"
        return "Salary not specified"
    
    class Meta:
        verbose_name = "Vacancy"
        verbose_name_plural = "Vacancies"
        ordering = ["-publication_date"]