
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.http import FileResponse

from .models import Candidate, Company, Job, Application


def calculate_similarity(resume_text, job_description):
    """Calculate TF-IDF cosine similarity as a percentage."""
    documents = [job_description, resume_text]
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(documents)
    score = cosine_similarity(
        tfidf_matrix[0:1], tfidf_matrix[1:2]
    )[0][0]
    return round(float(score) * 100, 2)


def extract_resume_text(resume_file):
    """Extract readable text from an uploaded PDF."""
    pdf_reader = PdfReader(resume_file)
    text = "\n".join(
        page.extract_text() or ""
        for page in pdf_reader.pages
    )
    return text.strip()


def home(request):
    """Public homepage with active job listings."""
    jobs = Job.objects.filter(is_active=True).select_related(
        "company"
    ).order_by("-posted_at")

    return render(
        request,
        "screening/home.html",
        {"jobs": jobs},
    )


def post_job(request):
    """Allow a company to publish a job without creating an account."""
    if request.method != "POST":
        return redirect("home")

    company_name = request.POST.get("company_name", "").strip()
    company_email = request.POST.get("company_email", "").strip()
    company_description = request.POST.get(
        "company_description", ""
    ).strip()

    title = request.POST.get("title", "").strip()
    description = request.POST.get("description", "").strip()
    required_skills = request.POST.get(
        "required_skills", ""
    ).strip()
    salary = request.POST.get("salary", "").strip()
    location = request.POST.get("location", "").strip()

    if not all([
        company_name,
        company_email,
        title,
        description,
        required_skills,
        location,
    ]):
        messages.error(
            request,
            "Please complete all required job and company fields.",
        )
        return redirect("home")

    company, created = Company.objects.get_or_create(
        name=company_name,
        email=company_email,
        defaults={"description": company_description},
    )

    if not created and company_description:
        company.description = company_description
        company.save(update_fields=["description"])

    Job.objects.create(
        company=company,
        title=title,
        description=description,
        required_skills=required_skills,
        salary=salary,
        location=location,
    )

    messages.success(request, "Your job has been posted successfully!")
    return redirect("home")


@require_POST
def apply_job(request, job_id):
    """Receive a job-specific application and score its resume."""
    job = get_object_or_404(Job, id=job_id, is_active=True)

    name = request.POST.get("candidate_name", "").strip()
    email = request.POST.get("candidate_email", "").strip()
    phone = request.POST.get("candidate_phone", "").strip()
    resume = request.FILES.get("resume")

    if not all([name, email, phone, resume]):
        messages.error(
            request,
            "Please complete all application fields and attach a resume.",
        )
        return redirect("home")

    if not resume.name.lower().endswith(".pdf"):
        messages.error(request, "Please upload a PDF resume.")
        return redirect("home")

    if resume.size > 5 * 1024 * 1024:
        messages.error(
            request,
            "Your resume must be smaller than 5 MB.",
        )
        return redirect("home")

    try:
        resume_text = extract_resume_text(resume)

        if not resume_text:
            messages.error(
                request,
                "No readable text was found in this PDF. "
                "Please upload a text-based PDF resume.",
            )
            return redirect("home")

        job_text = (
            f"{job.title}\n"
            f"{job.description}\n"
            f"{job.required_skills}"
        )

        score = calculate_similarity(resume_text, job_text)
        resume.seek(0)

        Application.objects.create(
            job=job,
            candidate_name=name,
            candidate_email=email,
            candidate_phone=phone,
            resume=resume,
            resume_text=resume_text,
            similarity_score=score,
        )

        messages.success(
            request,
            f"Application submitted successfully! "
            f"Resume similarity score: {score:.2f}%.",
        )

    except ValueError:
        messages.error(
            request,
            "The resume could not be processed. "
            "Please upload a valid text-based PDF.",
        )
    except Exception:
        messages.error(
            request,
            "Something went wrong while processing your resume. "
            "Please try another valid PDF.",
        )

    return redirect("home")


def legacy_resume_upload(request):
    """Retain the original general resume-upload workflow."""
    if request.method != "POST":
        return redirect("home")

    name = request.POST.get("name", "").strip()
    email = request.POST.get("email", "").strip()
    job_description = request.POST.get(
        "job_description", ""
    ).strip()
    resume = request.FILES.get("resume")

    if not all([name, job_description, resume]):
        messages.error(
            request,
            "Please complete all required fields.",
        )
        return redirect("home")

    if not resume.name.lower().endswith(".pdf"):
        messages.error(request, "Please upload a PDF resume.")
        return redirect("home")

    if resume.size > 5 * 1024 * 1024:
        messages.error(
            request,
            "The resume must be smaller than 5 MB.",
        )
        return redirect("home")

    try:
        resume_text = extract_resume_text(resume)

        if not resume_text:
            messages.error(
                request,
                "No readable text was found in this PDF.",
            )
            return redirect("home")

        score = calculate_similarity(resume_text, job_description)
        resume.seek(0)

        Candidate.objects.create(
            name=name,
            email=email,
            job_description=job_description,
            resume=resume,
            similarity_score=score,
        )

        messages.success(
            request,
            f"Resume uploaded! Text similarity score: {score:.2f}%.",
        )

    except Exception:
        messages.error(
            request,
            "The PDF could not be processed. "
            "Please try another valid PDF resume.",
        )

    return redirect("home")
@staff_member_required
def employer_dashboard(request):
    """Protected recruitment dashboard for authorized staff."""

    total_jobs = Job.objects.count()
    active_jobs = Job.objects.filter(is_active=True).count()
    total_applications = Application.objects.count()

    pending_applications = Application.objects.filter(
        status__in=["RECEIVED", "REVIEWING"]
    ).count()

    shortlisted_applications = Application.objects.filter(
        status="SHORTLISTED"
    ).count()

    jobs = Job.objects.annotate(
        application_count=Count("applications")
    ).select_related("company").order_by("-posted_at")

    applications = Application.objects.select_related(
        "job",
        "job__company",
    ).order_by("-similarity_score", "-applied_at")

    selected_status = request.GET.get("status", "").strip()
    selected_job = request.GET.get("job", "").strip()

    if selected_status in dict(Application.STATUS_CHOICES):
        applications = applications.filter(status=selected_status)
    else:
        selected_status = ""

    if selected_job.isdigit():
        applications = applications.filter(job_id=int(selected_job))
    else:
        selected_job = ""

    context = {
        "total_jobs": total_jobs,
        "active_jobs": active_jobs,
        "total_applications": total_applications,
        "pending_applications": pending_applications,
        "shortlisted_applications": shortlisted_applications,
        "jobs": jobs,
        "applications": applications,
        "status_choices": Application.STATUS_CHOICES,
        "selected_status": selected_status,
        "selected_job": selected_job,
    }

    return render(
        request,
        "screening/employer_dashboard.html",
        context,
    )


@staff_member_required
@require_POST
def update_application_status(request, application_id):
    """Allow authorized staff to update an application's status."""

    application = get_object_or_404(
        Application,
        id=application_id,
    )

    new_status = request.POST.get("status", "").strip()

    valid_statuses = dict(Application.STATUS_CHOICES)

    if new_status not in valid_statuses:
        messages.error(request, "Please select a valid application status.")
        return redirect("employer_dashboard")

    application.status = new_status
    application.save(update_fields=["status"])

    messages.success(
        request,
        f"Application status for {application.candidate_name} "
        f"updated to {valid_statuses[new_status]}.",
    )

    return redirect("employer_dashboard")


@staff_member_required
def download_resume(request, application_id):
    """Allow authorized staff to download a candidate's resume."""

    application = get_object_or_404(
        Application,
        id=application_id,
    )

    if not application.resume:
        messages.error(request, "No resume is attached to this application.")
        return redirect("employer_dashboard")

    try:
        resume_file = application.resume.open("rb")
        filename = application.resume.name.rsplit("/", 1)[-1]

        return FileResponse(
            resume_file,
            as_attachment=True,
            filename=filename,
        )
    except (FileNotFoundError, OSError, ValueError):
        messages.error(request, "The resume file could not be found.")
        return redirect("employer_dashboard")

