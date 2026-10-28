
from django.db import models


class Candidate(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    resume = models.FileField(upload_to="resumes/")
    job_description = models.TextField()
    similarity_score = models.FloatField(default=0.0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Company(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Job(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="jobs"
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    required_skills = models.TextField(
        help_text="Enter required skills separated by commas."
    )
    salary = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    posted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.company.name}"


class Application(models.Model):
    STATUS_CHOICES = [
        ("RECEIVED", "Received"),
        ("REVIEWING", "Under Review"),
        ("SHORTLISTED", "Shortlisted"),
        ("REJECTED", "Rejected"),
        ("HIRED", "Hired"),
    ]

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="applications"
    )
    candidate_name = models.CharField(max_length=150)
    candidate_email = models.EmailField()
    candidate_phone = models.CharField(max_length=20)
    resume = models.FileField(upload_to="applications/resumes/")
    resume_text = models.TextField(blank=True)
    similarity_score = models.FloatField(default=0.0)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="RECEIVED"
    )
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.candidate_name} - {self.job.title}"
