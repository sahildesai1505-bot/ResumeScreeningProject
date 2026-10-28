
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path(
        "employer/dashboard/",
        views.employer_dashboard,
        name="employer_dashboard",
    ),

    path("jobs/post/", views.post_job, name="post_job"),

    path(
        "jobs/<int:job_id>/apply/",
        views.apply_job,
        name="apply_job",
    ),

    path(
        "resume/upload/",
        views.legacy_resume_upload,
        name="legacy_resume_upload",
    ),
    path(
    "applications/<int:application_id>/update-status/",
    views.update_application_status,
    name="update_application_status",
),

path(
    "applications/<int:application_id>/resume/",
    views.download_resume,
    name="download_resume",
),

]
