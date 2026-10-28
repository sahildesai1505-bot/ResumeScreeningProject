
from django.contrib import admin
from .models import Candidate, Company, Job, Application


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "similarity_score", "uploaded_at")
    search_fields = ("name", "email")
    ordering = ("-similarity_score",)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at")
    search_fields = ("name", "email")


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "location", "is_active", "posted_at")
    list_filter = ("is_active", "location")
    search_fields = ("title", "company__name", "required_skills")


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "candidate_name",
        "candidate_email",
        "job",
        "similarity_score",
        "status",
        "applied_at",
    )
    list_filter = ("status", "job")
    search_fields = ("candidate_name", "candidate_email", "job__title")
    list_editable = ("status",)
    readonly_fields = ("similarity_score", "resume_text", "applied_at")
