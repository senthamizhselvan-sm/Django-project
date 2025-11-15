# AI-Assisted Radiology Reporting System 🏥

A Django-based web application for hospital radiology departments to automate and streamline medical imaging report generation using AI assistance.

## 📋 Project Overview

This system enables technicians to upload medical imaging scans (X-rays, CT, MRI) which are automatically analyzed by machine learning models. The AI generates preliminary diagnostic reports with confidence scores that radiologists can review, edit, and finalize.

### Key Features
- ✅ User Registration & Login with MongoDB
- ✅ Secure password hashing with bcrypt
- ✅ Session-based authentication
- ✅ Responsive static website with modern UI
- ✅ Dashboard for logged-in users
- 🔜 Image upload functionality (Coming Soon)
- 🔜 AI model integration (Coming Soon)
- 🔜 Report generation & review (Coming Soon)

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

| Route | Description |
|-------|-------------|
| `/` | Home page with feature overview |
| `/register/` | User registration page |
| `/login/` | User login page |
| `/dashboard/` | Dashboard (requires authentication) |
| `/logout/` | Logout and clear session |

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
  "password": "string (bcrypt hashed)"
}
```

## 🎨 Features Implemented

### ✅ Phase 1: Static Website + Authentication (Current)
- Landing page with feature showcase
- User registration with validation
- User login with MongoDB authentication
- Session management
- Dashboard with system overview
- Logout functionality
- Responsive navigation bar
- Professional UI/UX design

### 🔜 Phase 2: Image Upload & Processing (Next Steps)
- Medical image upload (X-ray, CT, MRI)
- Image storage system
- Patient record management

### 🔜 Phase 3: AI Integration
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
