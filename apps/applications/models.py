from django.db import models
from apps.users.models import EmployerProfile

# Create your models here.

class Technology(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class Vacancy(models.Model):
    worker_id = models.ForeignKey(
        EmployerProfile, 
        on_delete=models.CASCADE, 
        related_name="vacancies"
    )
    title = models.CharField(
        max_length=50
        )
    description = models.TextField(
        max_length=200
    )
    tecnologies = models.ManyToManyField(
        Technology, related_name="vantec"
        )
    modality = models.CharField(
        max_length=20
    )
    location = models.CharField(
        max_length=30
    )
    publication_date = models.DateField(
        auto_now_add=True
        )
    STATUS_CHOICES = [
        ("O", "Open"),
        ("C", "Closed")
    ]
    state = models.CharField(
        max_length=1, 
        choices=STATUS_CHOICES, default='O'
        )