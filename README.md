# AI-Based Digital Forensics Investigation System
### New Horizon College — Final Year Project

A professional full-stack digital forensics platform for managing investigations, analyzing evidence, generating file hashes, and producing certified forensic PDF reports.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Tailwind CSS, Framer Motion, Recharts, React Router |
| Backend | Python Flask, Flask-JWT-Extended, Flask-PyMongo |
| Database | MongoDB |
| Auth | JWT + bcrypt |
| Reports | ReportLab (PDF generation) |

---

## Project Structure

```
forensics-system/
├── backend/
│   ├── app.py                  # Flask entry point
│   ├── requirements.txt
│   ├── .env                    # Environment variables
│   ├── models/models.py        # MongoDB document schemas
│   ├── middleware/auth_middleware.py
│   ├── routes/
│   │   ├── auth_routes.py      # /api/auth
│   │   ├── case_routes.py      # /api/cases
│   │   ├── evidence_routes.py  # /api/evidence
│   │   ├── report_routes.py    # /api/reports
│   │   ├── log_routes.py       # /api/logs
│   │   └── dashboard_routes.py # /api/dashboard
│   ├── services/
│   │   ├── forensics_service.py  # Hash generation, metadata extraction
│   │   └── report_service.py     # PDF report generation
│   └── uploads/
│       ├── evidence/           # Uploaded evidence files stored here
│       └── reports/            # Generated PDF reports stored here
│
└── frontend/
    ├── public/index.html
    ├── package.json
    ├── tailwind.config.js
    └── src/
        ├── App.jsx
        ├── index.js / index.css
        ├── api/axios.js
        ├── context/
        │   ├── AuthContext.jsx
        │   └── ThemeContext.jsx
        ├── components/layout/DashboardLayout.jsx
        └── pages/
            ├── LandingPage.jsx
            ├── LoginPage.jsx
            ├── RegisterPage.jsx
            ├── DashboardPage.jsx
            ├── CasesPage.jsx
            ├── EvidencePage.jsx
            ├── ReportsPage.jsx
            └── LogsPage.jsx
```

---

## Prerequisites

- Python 3.9+
- Node.js 18+
- MongoDB (local or Atlas)

---

## Setup & Installation

### 1. Clone / Extract the project

```bash
cd forensics-system
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Edit .env if needed (default uses localhost MongoDB)
# MONGO_URI=mongodb://localhost:27017/forensics_db
# JWT_SECRET_KEY=your-super-secret-jwt-key

# Start Flask server
python app.py
```

Backend runs on: `http://localhost:5000`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start React dev server
npm start
```

Frontend runs on: `http://localhost:3000`

---

## Configuration (.env)

```
MONGO_URI=mongodb://localhost:27017/forensics_db
JWT_SECRET_KEY=change-this-to-a-strong-secret-key
JWT_ACCESS_TOKEN_EXPIRES=86400
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=52428800
```

---

## Features

### Authentication
- Register as Admin or Investigator
- JWT-secured login with bcrypt password hashing
- Protected routes — unauthenticated users redirected to login

### Dashboard
- Real-time stats: cases, evidence, reports, logs
- Activity trend chart (last 30 days)
- Evidence breakdown by type (pie chart)
- Recent cases and activity feed

### Case Management
- Create, edit, delete investigation cases
- Set status: open / in_progress / closed / archived
- Set priority: low / medium / high / critical
- Search and filter cases

### Evidence Management
- Drag-and-drop file upload (PDF, images, docs, logs, ZIP, JSON, etc.)
- Auto-generate MD5 + SHA-256 hashes on upload
- Extract file metadata (size, timestamps, extension)
- View full hash details per file
- Download and soft-delete evidence
- Filter by type and case

### Report Generation
- Select any case and generate a forensic PDF report
- Report includes: case details, evidence inventory, hash verification table, findings
- Download report as PDF

### Activity Logs
- All user actions tracked automatically
- Filter by action type, search by user/details
- Admin sees all logs; investigators see their own

### Dark / Light Mode
- Toggle from the dashboard header
- Preference persisted in localStorage

---

## API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/register | Register new user |
| POST | /api/auth/login | Login, get JWT token |
| GET  | /api/auth/me | Get current user info |
| GET  | /api/auth/users | Get all users (admin) |

### Cases
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET  | /api/cases/ | List cases |
| POST | /api/cases/ | Create case |
| GET  | /api/cases/:id | Get case |
| PUT  | /api/cases/:id | Update case |
| DELETE | /api/cases/:id | Delete case |

### Evidence
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET  | /api/evidence/ | List evidence |
| POST | /api/evidence/upload | Upload evidence file |
| GET  | /api/evidence/:id | Get evidence details |
| DELETE | /api/evidence/:id | Soft-delete evidence |
| GET  | /api/evidence/download/:id | Download file |

### Reports
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/reports/generate/:case_id | Generate PDF report |
| GET  | /api/reports/ | List reports |
| GET  | /api/reports/download/:id | Download PDF |
| DELETE | /api/reports/:id | Delete report (admin) |

### Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/dashboard/stats | Summary statistics |
| GET | /api/dashboard/recent | Recent cases, evidence, logs |

### Logs
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/logs/ | Activity logs |

---

## Security

- All API routes protected with JWT Bearer tokens
- Passwords hashed with bcrypt (12 rounds)
- File type validation on upload
- Role-based access control (admin vs investigator)
- CORS configured for API

---

## Default Roles

| Role | Permissions |
|------|------------|
| admin | Full access to all data, can delete reports |
| investigator | Access to own cases and evidence |

---

*AI-Based Digital Forensics Investigation System — New Horizon College*
