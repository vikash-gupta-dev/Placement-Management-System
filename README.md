# Placement Management System v2

React.js + CSS + Flask + Python + Supabase PostgreSQL.

## New features
- Multiple student accounts using email + password.
- Student registration and login.
- Student profile editing: name, roll no, department, CGPA, graduation year, phone, city, skills, bio.
- LinkedIn, GitHub and LeetCode URLs.
- Resume PDF upload (demo stores it through Flask locally; production can move it to Supabase Storage).
- Admin can view applicant details for applications.
- Admin can change application status: Applied, Shortlisted, Interview, Selected, Rejected.
- Company-specific application information is included in the admin application view.
- Eligibility and duplicate/deadline validation.
- Supabase-backed data with a local fallback for UI development.

## Existing Supabase project
If you already ran the previous schema, open Supabase SQL Editor and run:
`supabase/migration_existing_project.sql`

Do NOT run the fresh schema on top of an existing project unless you understand the table changes.

## Fresh Supabase project
Run `supabase/schema.sql`.

## Environment
backend/.env:
SUPABASE_URL=...
SUPABASE_KEY=...

Do not commit .env or any secret/service-role key.

## Run
Backend:
cd backend
venv\Scripts\activate
pip install -r requirements.txt
python app.py

Frontend in a second terminal:
cd frontend
npm install
npm run dev

Open http://localhost:5173

## Demo credentials
Student: vikash@example.com / demo1234
Admin: admin@example.com / admin1234

## Demo flow
1. Register another student with a different email.
2. Login as that student.
3. Edit profile and add LinkedIn/LeetCode/GitHub.
4. Upload a PDF resume.
5. Apply for a company job.
6. Logout and login as Admin.
7. Open All Applications.
8. Click View Details to see the applicant's academic/profile/contact/links/resume information and the company/job applied for.
9. Change status to Shortlisted or Interview.
10. Explain: React -> Flask -> validation -> Supabase PostgreSQL.
