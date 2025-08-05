from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_OPTIONS = [
        ('admin', 'Admin'),
        ('employee', 'Employee'),
        ('employer', 'Employer')
    ]
    email = models.EmailField(
        'E-mail',
        unique=True
    )

    bio = models.TextField(
        'Biography',
        null=True,
        blank=True,
        max_length=500,
        help_text='Optional. 500 characters maximum.'
    )

    role = models.CharField(
        'Role',
        max_length=10,
        choices=ROLE_OPTIONS,
        default='employee'
    )

    birth_date = models.DateField(
        'Birth Date',
        null=True
    )

    phone_number = models.CharField(
        'Phone Number',
        max_length=15,
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    profile_pic = models.ImageField(
         upload_to='avatars/',
         null=True,
         blank=True
    )

    date_joined = models.DateTimeField(
        auto_now_add=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    @property
    def is_employee(self):
        return self.role == 'employee'
    
    @property
    def is_employer(self):
        return self.role == 'employer'

    @property
    def age(self):
        from datetime import date
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return None
    
    def clean(self):
        if self.age is not None and self.age < 18:
            raise ValidationError(
                "User must be at least 18 years old."
            )
        
    def __str__(self):
            return f"{self.first_name} {self.last_name} ({self.email}) - {self.role}"
    
    class Meta:
         verbose_name = 'User'
         verbose_name_plural = 'Users'
         ordering = ['-date_joined']

class EmployeeProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='employee_profile'
    )

    resume = models.FileField(
        upload_to='resumes/',
        null=True,
        blank=True
    )

    skills = models.TextField(
        blank=True
    )

    github_url = models.URLField(
        blank=True
    )

    linkedin_url = models.URLField(
        blank=True
    )

    date_joined = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Employee profile - {self.user.email}"
    
    class Meta:
        verbose_name = 'Employee Profile'
        verbose_name_plural = 'Employee Profiles'
        ordering = ['-date_joined']

class EmployerProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='employer_profile'
    )

    company_name = models.CharField(
        max_length=255
    )

    company_website = models.URLField(
        blank=True
    )
    
    company_description = models.TextField(
        blank=True
    )

    founded_year = models.PositiveIntegerField(
        blank=True,
        null=True
    )

    date_joined = models.DateTimeField(
        auto_now_add=True
    )

    def clean(self):
        from datetime import date
        if self.founded_year and self.founded_year > date.today().year:
            raise ValidationError("Founded year cannot be in the future.")

    def __str__(self):
        return f"Employer profile - {self.company_name}"
    
    class Meta:
        verbose_name = 'Employer Profile'
        verbose_name_plural = 'Employer Profiles'
        ordering = ['-date_joined']


class tecchnology(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class vacancies(models.Model):
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
        tecchnology, related_name="vantec"
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
    STATUS_CHOISES = [
        ("O", "Open"),
        ("C", "Closed")
    ]
    state = models.CharField(
        max_length=1, 
        choices=STATUS_CHOISES, default='O'
        )