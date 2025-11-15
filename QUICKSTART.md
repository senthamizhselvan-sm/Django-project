# 🚀 Quick Start Guide - Radiology AI System

## Prerequisites Checklist
- ✅ Python 3.13 installed
- ✅ Virtual environment created (`.venv`)
- ✅ MongoDB installed and running
- ✅ All dependencies installed

## 5-Minute Setup

### Step 1: Verify MongoDB is Running
```powershell
# Check MongoDB service status
Get-Service -Name MongoDB

# If not running, start it
Start-Service -Name MongoDB
```

### Step 2: Activate Virtual Environment
```powershell
# Navigate to project directory
cd D:\Django-project

# Activate virtual environment
.\.venv\Scripts\Activate.ps1
```

### Step 3: Run Migrations (Already Done)
```bash
python manage.py migrate
```

### Step 4: Start Development Server
```bash
python manage.py runserver
```

### Step 5: Access the Application
Open your browser and navigate to:
- **Home Page**: http://127.0.0.1:8000/
- **Register**: http://127.0.0.1:8000/register/
- **Login**: http://127.0.0.1:8000/login/

---

## 🧪 Quick Test Workflow

### 1. Register a New User
1. Go to: http://127.0.0.1:8000/register/
2. Fill in the form:
   - Full Name: `Dr. John Smith`
   - Email: `john.smith@hospital.com`
   - Password: `password123`
   - Confirm Password: `password123`
3. Click "Register"
4. You should see: "Registration successful! Please login."

### 2. Login
1. You'll be redirected to: http://127.0.0.1:8000/login/
2. Enter credentials:
   - Email: `john.smith@hospital.com`
   - Password: `password123`
3. Click "Login"
4. You should see: "Welcome back, Dr. John Smith!"

### 3. Explore Dashboard
1. After login, you're at: http://127.0.0.1:8000/dashboard/
2. View:
   - Welcome message with your name
   - System features and benefits
   - Quick action buttons (coming soon)

### 4. Logout
1. Click "Logout" in the navigation bar
2. You'll be redirected to home page
3. You should see: "You have been logged out successfully!"

---

## 📊 Verify MongoDB Data

### Option 1: Using MongoDB Shell
```bash
mongosh
use radiology_db
db.users.find().pretty()
```

### Option 2: Using MongoDB Compass
1. Open MongoDB Compass
2. Connect to: `mongodb://localhost:27017`
3. Select database: `radiology_db`
4. View collection: `users`
5. You should see your registered user with hashed password

---

## 🛠️ Common Commands

### Start Server
```bash
python manage.py runserver
```

### Stop Server
Press `CTRL+C` in the terminal

### Create Superuser (Django Admin)
```bash
python manage.py createsuperuser
```

### Access Django Admin
http://127.0.0.1:8000/admin/

### Check for Errors
```bash
python manage.py check
```

### Run Migrations
```bash
python manage.py migrate
```

### Create New Migration
```bash
python manage.py makemigrations
```

---

## 🐛 Troubleshooting

### Issue: MongoDB Connection Error
**Error**: `ServerSelectionTimeoutError`

**Solution**:
```powershell
# Check MongoDB service
Get-Service -Name MongoDB

# Start if not running
Start-Service -Name MongoDB

# Verify connection
mongosh
```

### Issue: Port 8000 Already in Use
**Error**: `Error: That port is already in use.`

**Solution**:
```bash
# Use a different port
python manage.py runserver 8080

# Or kill the process using port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Issue: Template Not Found
**Error**: `TemplateDoesNotExist`

**Solution**:
- Check `TEMPLATES` setting in `radiology/settings.py`
- Verify `templates/` folder exists
- Ensure `'DIRS': [BASE_DIR / 'templates']` is set

### Issue: Static Files Not Loading
**Error**: CSS not applied

**Solution**:
- Check `STATIC_URL` in `settings.py`
- Verify `static/css/style.css` exists
- Ensure `{% load static %}` is in template
- Run: `python manage.py collectstatic` (for production)

### Issue: Session Not Working
**Error**: User logged in but session lost

**Solution**:
- Check `django.contrib.sessions` is in `INSTALLED_APPS`
- Check `SessionMiddleware` is in `MIDDLEWARE`
- Run migrations: `python manage.py migrate`

---

## 📝 Development Tips

### 1. Check Logs
Monitor the terminal where `runserver` is running for:
- Request logs
- Error messages
- Warning messages

### 2. Test Different Scenarios
- Try registering with existing email (should fail)
- Try login with wrong password (should fail)
- Try accessing `/dashboard/` without login (should redirect)
- Test password mismatch on registration
- Test short password (< 6 characters)

### 3. MongoDB Queries for Testing
```javascript
// View all users
db.users.find()

// Count users
db.users.countDocuments()

// Delete test user
db.users.deleteOne({email: "test@example.com"})

// Clear all users (careful!)
db.users.deleteMany({})
```

---

## 🎯 Next Steps (After Phase 1)

Once you're comfortable with the current system:

1. **Image Upload Feature**
   - Add file upload functionality
   - Implement image storage
   - Create patient records model

2. **AI Integration**
   - Train/import ML model
   - Create prediction API
   - Generate automated reports

3. **Report Management**
   - Build report review interface
   - Add edit capabilities
   - Implement approval workflow

4. **User Roles**
   - Add role-based access (Radiologist, Technician, Admin)
   - Implement permissions
   - Create role-specific dashboards

---

## 📞 Need Help?

- Check `README.md` for detailed documentation
- Review `MONGODB_SETUP.md` for MongoDB configuration
- Contact development team for support

---

**Happy Coding! 🚀**
