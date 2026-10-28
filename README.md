
# ResumeAI — AI-Powered Resume Screening System

ResumeAI is a Django-based recruitment platform designed to simplify the initial resume screening process.

## Features

- Job posting and job listings
- Candidate job applications without requiring candidate accounts
- PDF resume text extraction
- TF-IDF cosine similarity scoring between resumes and job requirements
- Employer dashboard for reviewing applications
- Application status management
- Protected resume downloads for authorized staff

## Technology Stack

- Python
- Django
- HTML and CSS
- SQLite for local development
- PostgreSQL configuration for future deployment
- pypdf for PDF text extraction
- scikit-learn for TF-IDF and cosine similarity
- WhiteNoise for static files

## Local Setup

1. Clone or download this repository.
2. Create and activate a Python virtual environment.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run database migrations:

   ```bash
   python manage.py migrate
   ```

5. Create an administrator account:

   ```bash
   python manage.py createsuperuser
   ```

6. Start the development server:

   ```bash
   python manage.py runserver
   ```

7. Open http://127.0.0.1:8000/ in your browser.

## Deployment Status

The project source code is maintained on GitHub. The Django application has not been deployed to a public hosting service yet.

## Security Notes

- Do not commit passwords, secret keys, database credentials, uploaded resumes, or private user data.
- Configure a strong secret key through the `DJANGO_SECRET_KEY` environment variable before production deployment.
- Set `DJANGO_DEBUG=False` in production.
