# AI-Assisted Radiology Reporting System 🏥

A Django-based web application for hospital radiology departments to automate and streamline medical imaging report generation using AI assistance.

## 📋 Project Overview

This system enables technicians to upload medical imaging scans (X-rays, CT, MRI) which are automatically analyzed by machine learning models. The AI generates preliminary diagnostic reports with confidence scores that radiologists can review, edit, and finalize.

### Key Features
- ✅ User Registration & Login with MongoDB
- ✅ Role-based authentication (Radiologist & Technician)
- ✅ Secure password hashing with bcrypt
- ✅ Session-based authentication
- ✅ Responsive dashboards with Bootstrap 5
- ✅ **Image Upload System** for Technicians
- ✅ **Scan Review System** for Radiologists
- ✅ **Report Submission & Management**
- ✅ **MongoDB Scans Collection** for storing scan metadata
- ✅ **File Storage System** in /media/scans/
- 🔜 AI model integration (Coming Soon)
- 🔜 AI prediction & confidence scoring (Coming Soon)

## 🎯 Target Users
- **Radiologists**: Review and finalize AI-generated reports
- **Technicians**: Upload scans and manage patient cases
- **Administrators**: Manage user roles and system data

## 🛠️ Technology Stack

- **Backend**: Django 4.2.16
- **Database**: MongoDB
- **Authentication**: Custom authentication with bcrypt
- **Frontend**: HTML5, CSS3 (Responsive Design)
- **Python Version**: 3.13

## 📦 Installation & Setup

### Prerequisites
- Python 3.13+
- MongoDB (running on localhost:27017)
- Virtual Environment

### Installation Steps

1. **Clone the repository**
   ```bash
   cd D:\Django-project
   ```

2. **Activate virtual environment**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install dependencies** (Already installed)
   ```bash
   pip install django pymongo bcrypt
   ```

4. **Start MongoDB**
   - Ensure MongoDB is running on `mongodb://localhost:27017/`
   - Database name: `radiology_db`
   - Collection: `users`

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Start the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Open browser: `http://127.0.0.1:8000/`

## 🌐 Application Routes

| Route | Description | Access |
|-------|-------------|--------|
| `/` | Home page with feature overview | Public |
| `/register/` | User registration page | Public |
| `/login/` | User login page | Public |
| `/dashboard/` | Generic dashboard | Authenticated |
| `/logout/` | Logout and clear session | Authenticated |
| `/radiologist/dashboard/` | Radiologist dashboard | Radiologist only |
| `/radiologist/analyze/<id>/` | Analyze scan | Radiologist only |
| `/radiologist/reports/` | View completed reports | Radiologist only |
| `/radiologist/pending/` | View pending scans | Radiologist only |
| `/technician/dashboard/` | Technician dashboard | Technician only |
| `/technician/upload/` | Upload scan form | Technician only |
| `/technician/scans/` | View all scans | Technician only |
| `/technician/scan/<id>/` | View scan details | Technician only |

## 📁 Project Structure

```
Django-project/
├── radiology/              # Main project directory
│   ├── settings.py         # Project settings
│   ├── urls.py             # Main URL configuration
│   └── wsgi.py
├── accounts/               # Authentication app
│   ├── views.py            # View functions
│   ├── urls.py             # App URL patterns
│   └── mongodb.py          # MongoDB connection utility
├── templates/              # HTML templates
│   ├── base.html           # Base template
│   ├── home.html           # Landing page
│   ├── register.html       # Registration form
│   ├── login.html          # Login form
│   └── dashboard.html      # User dashboard
├── static/                 # Static files
│   └── css/
│       └── style.css       # Main stylesheet
├── manage.py               # Django management script
└── .venv/                  # Virtual environment
```

## 🔐 Security Features

- **Password Hashing**: Bcrypt with salt
- **Email Validation**: Duplicate email prevention
- **Session Management**: Secure session-based authentication
- **CSRF Protection**: Django built-in CSRF middleware

## 💾 MongoDB Schema

### Users Collection
```json
{
  "_id": "ObjectId",
  "full_name": "string",
  "email": "string (unique, lowercase)",
  "role": "string (radiologist/technician)",
  "password": "string (bcrypt hashed)"
}
```

### Scans Collection
```json
{
  "_id": "ObjectId",
  "patient_name": "string",
  "patient_id": "string (alphanumeric)",
  "age": "number",
  "gender": "string (Male/Female/Other)",
  "scan_type": "string (X-Ray/CT Scan/MRI/Ultrasound)",
  "scan_file_path": "string (media/scans/filename)",
  "uploaded_by": "string (technician email)",
  "status": "string (Pending Analysis/Under Review/Completed)",
  "uploaded_at": "datetime",
  "radiologist_report": "string (optional)",
  "reviewed_by": "string (radiologist email, optional)",
  "reviewed_at": "datetime (optional)",
  "ai_prediction": "string (optional)",
  "ai_confidence": "number (optional, 0-100)"
}
```

## 🎨 Features Implemented

### ✅ Phase 1: Authentication & Role-Based Access
- Landing page with feature showcase
- User registration with role selection (Radiologist/Technician)
- User login with MongoDB authentication
- Session management with role tracking
- Separate dashboards for each role
- Role-based navigation and access control
- Logout functionality
- Professional UI/UX with Bootstrap 5

### ✅ Phase 2: Image Upload & Scan Review (Current)

**Technician Features:**
- **Upload Scan Form** with comprehensive fields:
  - Patient Name, Patient ID, Age, Gender
  - Scan Type selection (X-Ray, CT, MRI, Ultrasound)
  - File upload with validation (JPG, PNG, JPEG, DICOM)
- **File Storage System**:
  - Automatic directory creation
  - Unique filename generation (patient_id_timestamp)
  - Files stored in `/media/scans/`
- **MongoDB Integration**:
  - Scans collection for metadata storage
  - Track uploaded_by (technician email)
  - Status tracking (Pending/Under Review/Completed)
- **Technician Dashboard**:
  - Real-time stats (Total Uploads, Pending, Under Review, Completed)
  - List of uploaded scans with patient info
  - Status badges for visual tracking

**Radiologist Features:**
- **Scan Review Dashboard**:
  - View all pending scans requiring analysis
  - Real-time stats (Pending, Under Review, Completed)
  - Recently completed reports section
- **Scan Detail View** (`view_scan.html`):
  - Complete patient information display
  - Medical scan image preview
  - AI prediction results (when available)
  - AI confidence score visualization
- **Report Submission**:
  - Rich text area for detailed radiological findings
  - Submit report and auto-update status to "Completed"
  - Track reviewed_by and reviewed_at timestamps
- **Completed Reports List**:
  - View all finalized reports
  - **Advanced Filtering**:
    * Search by patient name (case-insensitive)
    * Filter by scan type (X-Ray, CT, MRI, Ultrasound)
    * Filter by date range (from/to dates)
  - **Pagination** (15 reports per page)
  - Access for both Radiologist and Technician roles
  - Query parameters support: `?scan_type=CT&name=john&from_date=2025-01-01&to_date=2025-12-31`
  - Clear filters functionality
  - Results summary with count

### 🔜 Phase 3: AI Integration (Next Steps)
- ML model integration
- Automated report generation
- Confidence score calculation

### 🔜 Phase 4: Report Management
- Radiologist review interface
- Report editing capabilities
- Report approval workflow
- Historical data access

## 🚀 Usage

1. **Register a new account**
   - Navigate to `/register/`
   - Fill in: Full Name, Email, Password, Confirm Password
   - Click "Register"

2. **Login**
   - Navigate to `/login/`
   - Enter email and password
   - Click "Login"

3. **Access Dashboard**
   - After successful login, you'll be redirected to the dashboard
   - View system information and features

4. **Logout**
   - Click "Logout" in the navigation bar

## 🧪 Testing

### Test User Registration
1. Go to `http://127.0.0.1:8000/register/`
2. Create a test user
3. Verify user is stored in MongoDB

### Test Login
1. Go to `http://127.0.0.1:8000/login/`
2. Login with registered credentials
3. Verify redirect to dashboard

## 📊 Current Status

✅ **Completed**:
- MongoDB connection setup
- User authentication system
- Static website with responsive design
- Session management
- All templates and styling

🔄 **In Progress**:
- None

⏳ **Upcoming**:
- Image upload functionality
- AI model integration
- Report generation system

## 🤝 Contributing

This is a hospital-internal project. Contact the development team for contribution guidelines.

## 📝 License

Internal Hospital Project - Confidential

## 📞 Support

For issues or questions, contact the development team.

---

**Version**: 1.0.0  
**Last Updated**: November 15, 2025  
**Status**: Phase 1 Complete ✅
