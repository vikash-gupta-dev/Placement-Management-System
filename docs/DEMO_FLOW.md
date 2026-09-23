# Capstone demo flow

Student side:
- Create account with a unique email.
- Login.
- Edit profile.
- Upload resume PDF.
- Add LinkedIn, GitHub and LeetCode.
- Browse jobs.
- Apply.
- See application status.

Admin side:
- Login.
- See dashboard statistics.
- Manage companies.
- View all applications.
- For each application, view the company, job and candidate details.
- Change application status.

Architecture:
React.js + CSS -> Flask REST API -> Python business validation -> Supabase PostgreSQL.
