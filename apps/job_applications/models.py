from django.db import models
from django.core.exceptions import ValidationError
from apps.users.models import EmployeeProfile, EmployerProfile, User

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

class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('reviewing', 'Under Review'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('interview_completed', 'Interview Completed'),
        ('rejected', 'Rejected'),
        ('accepted', 'Accepted'),
        ('withdrawn', 'Withdrawn by Candidate')
    ]

    employee = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.CASCADE,
        related_name="job_applications"
    )

    vacancy = models.ForeignKey(
        Vacancy,
        on_delete=models.CASCADE,
        related_name="job_applications"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    cover_letter = models.TextField(
        max_length=1000,
        blank=True,
        help_text="Optional cover letter (max 1000 characters)"
    )

    applied_date = models.DateTimeField(
        auto_now_add=True
    )

    last_updated = models.DateTimeField(
        auto_now=True
    )

    notes = models.TextField(
        blank=True,
        help_text="Internal notes from employer"
    )

    salary_expectation = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Salary expectations (optional)"
    )

    availability_date = models.DateField(
        null=True,
        blank=True,
        help_text="When can you start working?"
    )

    class Meta:
        verbose_name = "Job Application"
        verbose_name_plural = "Job Applications"
        ordering = ['-applied_date']
        unique_together = ['employee', 'vacancy']

    def clean(self):
        if self.vacancy and self.vacancy.state == "C":
            raise ValidationError(
                "Cannot apply to a closed vacancy"
            )
        
        if self.employee and self.vacancy and self.employee.user == self.vacancy.employer.user:
            raise ValidationError(
                "Cannot apply to your own vacancy"
            )
        
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.user.get_full_name()} - {self.vacancy.title}"
    
    @property
    def can_withdraw(self):
        return self.status in ["pending", "reviewing", "interview_scheduled"]
    
    @property
    def is_active(self):
        return self.status not in ["rejected", "accepted", "withdrawn"]
    
class ApplicationStatusHistory(models.Model):
    application = models.ForeignKey(
        JobApplication,
        on_delete=models.CASCADE,
        related_name='status_history'
    )
    
    previous_status = models.CharField(
        max_length=20,
        choices=JobApplication.STATUS_CHOICES
    )
    
    new_status = models.CharField(
        max_length=20,
        choices=JobApplication.STATUS_CHOICES
    )
    
    changed_by = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='status_changes'
    )
    
    changed_date = models.DateTimeField(auto_now_add=True)
    
    reason = models.TextField(
        blank=True,
        help_text="Reason for status change"
    )

    class Meta:
        verbose_name = 'Application Status History'
        verbose_name_plural = 'Application Status Histories'
        ordering = ['-changed_date']
    
    def __str__(self):
        return f"{self.application} - {self.previous_status} → {self.new_status}"
    
class Interview(models.Model):
    INTERVIEW_TYPES = [
        ('phone', 'Phone Interview'),
        ('video', 'Video Interview'),
        ('in_person', 'In Person Interview'),
        ('technical', 'Technical Interview'),
    ]

    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled')
    ]

    application = models.ForeignKey(
        JobApplication,
        on_delete=models.CASCADE,
        related_name="interviews"
    )

    interview_type = models.CharField(
        max_length=20,
        choices=INTERVIEW_TYPES,
        default='video'
    )

    scheduled_date = models.DateTimeField()

    duration_minutes = models.PositiveIntegerField(
        default=60,
        help_text="Expected duration in minutes."
    )

    location = models.CharField(
        max_length=200,
        blank=True,
        help_text="Physical address or video link."
    )

    interviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="conducted_interviews"
    )

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='scheduled'
    )

    feedback = models.TextField(
        blank=True,
        help_text="Interview feedback and notes"
    )
    
    score = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Interview score (1-10)"
    )
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Interview'
        verbose_name_plural = 'Interviews'
        ordering = ['scheduled_date']
    
    def clean(self):
        from django.utils import timezone
        
        if self.scheduled_date and self.scheduled_date < timezone.now():
            raise ValidationError(
                "Interview cannot be scheduled in the past."
            )
        
        if self.score is not None and (self.score < 1 or self.score > 10):
            raise ValidationError(
                "Score must be between 1 and 10."
            )
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.application.employee.user.get_full_name()} - {self.interview_type} - {self.scheduled_date.strftime('%Y-%m-%d %H:%M')}"


class ApplicationDocument(models.Model):
    DOCUMENT_TYPES = [
        ('CV', 'CV/Resume'),
        ('Portfolio', 'Portfolio'),
        ('Certificate', 'Certificate'),
        ('Diploma', 'Diploma'),
        ('Cover Letter', 'Cover Letter'),
        ('References', 'References'),
        ('Other', 'Other')
    ]
    
    application = models.ForeignKey(
        JobApplication,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    
    document = models.FileField(
        upload_to='application_documents/',
        help_text="Additional documents (CV, portfolio, certificates, etc.)"
    )
    
    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPES,
        default='Other',
        help_text="Type of document"
    )
    
    description = models.CharField(
        max_length=200,
        blank=True,
        help_text="Brief description of the document"
    )
    
    uploaded_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Application Document'
        verbose_name_plural = 'Application Documents'
        ordering = ['-uploaded_date']
    
    def __str__(self):
        return f"{self.application} - {self.document_type}"