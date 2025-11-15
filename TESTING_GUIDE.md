# 🧪 Testing Guide - Role-Based Dashboard System

## Server Status
✅ Server running at: **http://127.0.0.1:8000/**

---

## Quick Test Steps

### 1️⃣ Test Radiologist Registration & Login

#### Step 1: Register Radiologist
1. Open: http://127.0.0.1:8000/register/
2. Fill in:
   - **Full Name**: Dr. Sarah Johnson
   - **Email**: sarah@hospital.com
   - **Role**: Select **Radiologist**
   - **Password**: password123
   - **Confirm Password**: password123
3. Click "Register"
4. You should see: "Registration successful! Please login."

#### Step 2: Login as Radiologist
1. Should redirect to: http://127.0.0.1:8000/login/
2. Enter:
   - **Email**: sarah@hospital.com
   - **Password**: password123
3. Click "Login"
4. ✅ **Should automatically redirect to**: `/radiologist/dashboard/`

#### Step 3: Verify Radiologist Dashboard
- ✅ Purple gradient header
- ✅ Welcome message: "Welcome, Dr. Sarah Johnson!"
- ✅ 3 Quick stats cards
- ✅ Pending Scans table with 3 sample scans
- ✅ "Analyze" buttons for each scan
- ✅ "View Completed Reports" button
- ✅ Navigation bar shows: Dashboard, Pending Scans, Completed Reports, Logout

#### Step 4: Test Radiologist Features
1. Click "Analyze" button → Should show "Coming soon" message
2. Click "View Completed Reports" → Should show "Coming soon" message
3. Click "Pending Scans" in navbar → Returns to dashboard
4. Click "Logout" → Redirects to home

---

### 2️⃣ Test Technician Registration & Login

#### Step 1: Register Technician
1. Open: http://127.0.0.1:8000/register/
2. Fill in:
   - **Full Name**: Mike Anderson
   - **Email**: mike@hospital.com
   - **Role**: Select **Technician**
   - **Password**: password123
   - **Confirm Password**: password123
3. Click "Register"
4. You should see: "Registration successful! Please login."

#### Step 2: Login as Technician
1. Should redirect to: http://127.0.0.1:8000/login/
2. Enter:
   - **Email**: mike@hospital.com
   - **Password**: password123
3. Click "Login"
4. ✅ **Should automatically redirect to**: `/technician/dashboard/`

#### Step 3: Verify Technician Dashboard
- ✅ Green gradient header
- ✅ Welcome message: "Welcome, Mike Anderson!"
- ✅ 4 Quick stats cards (Total, Pending, Review, Completed)
- ✅ Large "Upload New Scan" button
- ✅ Uploaded Scans table with 3 sample scans
- ✅ Color-coded status badges
- ✅ "View" buttons for each scan
- ✅ Navigation bar shows: Dashboard, Upload Scan, View Scans, Logout

#### Step 4: Test Technician Features
1. Click "Upload New Scan" → Should show "Coming soon" message
2. Click "View" button → Should show "Coming soon" message
3. Click "View All Scans" → Returns to dashboard
4. Click "Upload Scan" in navbar → Should show "Coming soon" message
5. Click "Logout" → Redirects to home

---

### 3️⃣ Test Role-Based Access Control

#### Test 1: Radiologist trying to access Technician pages
1. Login as Radiologist (sarah@hospital.com)
2. Try to visit: http://127.0.0.1:8000/technician/dashboard/
3. ✅ Should see error: "You do not have permission to access this page."
4. ✅ Should redirect to home page

#### Test 2: Technician trying to access Radiologist pages
1. Login as Technician (mike@hospital.com)
2. Try to visit: http://127.0.0.1:8000/radiologist/dashboard/
3. ✅ Should see error: "You do not have permission to access this page."
4. ✅ Should redirect to home page

#### Test 3: Accessing protected pages without login
1. Logout completely
2. Try to visit: http://127.0.0.1:8000/radiologist/dashboard/
3. ✅ Should see: "Please login to access this page."
4. ✅ Should redirect to login page

---

### 4️⃣ Test Navigation Bar Changes

#### When Logged Out
- ✅ Should show: Login | Register

#### When Logged In as Radiologist
- ✅ Should show: Hello, Dr. Sarah Johnson | Dashboard | Pending Scans | Completed Reports | Logout

#### When Logged In as Technician
- ✅ Should show: Hello, Mike Anderson | Dashboard | Upload Scan | View Scans | Logout

---

### 5️⃣ Test Registration Validation

#### Test 1: Role validation
1. Open browser developer tools → Network tab
2. Try to register with invalid role (manual form manipulation)
3. ✅ Should see error: "Invalid role selected!"

#### Test 2: All fields required
1. Try to submit registration form without selecting role
2. ✅ Browser should prevent submission (HTML5 required attribute)

#### Test 3: Duplicate email
1. Try to register with sarah@hospital.com again
2. ✅ Should see error: "Email already registered!"

---

## 📊 MongoDB Verification

### Check Registered Users
```bash
mongosh
use radiology_db
db.users.find().pretty()
```

Expected output:
```json
{
  "_id": ObjectId("..."),
  "full_name": "Dr. Sarah Johnson",
  "email": "sarah@hospital.com",
  "role": "radiologist",
  "password": "$2b$12$..."
}
{
  "_id": ObjectId("..."),
  "full_name": "Mike Anderson",
  "email": "mike@hospital.com",
  "role": "technician",
  "password": "$2b$12$..."
}
```

### Check User Count by Role
```javascript
db.users.countDocuments({role: "radiologist"})  // Should be 1
db.users.countDocuments({role: "technician"})   // Should be 1
```

---

## 🎨 Visual Checklist

### Radiologist Dashboard
- [ ] Purple gradient header (top)
- [ ] Welcome message with name
- [ ] 3 stats cards with icons
- [ ] Table with patient data
- [ ] "Analyze" buttons in table
- [ ] Green "View Completed Reports" button
- [ ] Red "Logout" button
- [ ] Bootstrap styling applied
- [ ] Icons showing correctly
- [ ] Responsive on mobile

### Technician Dashboard
- [ ] Green gradient header (top)
- [ ] Welcome message with name
- [ ] 4 stats cards with icons
- [ ] Large blue "Upload New Scan" button
- [ ] Table with uploaded scans
- [ ] Color-coded status badges (Yellow, Blue, Green)
- [ ] "View" buttons in table
- [ ] Blue "View All Scans" button
- [ ] Red "Logout" button
- [ ] Bootstrap styling applied
- [ ] Icons showing correctly
- [ ] Responsive on mobile

---

## 🐛 Known Issues (Expected)

### Non-Issues
1. **Favicon 404** - Normal, no favicon file created yet
2. **"Coming Soon" messages** - Expected for placeholder features
3. **Sample data only** - Real data will come in Phase 3

### If You See These, It's Working Correctly:
- ✅ "Coming soon" alerts when clicking placeholder buttons
- ✅ Redirect to home when accessing wrong role's pages
- ✅ Redirect to login when accessing protected pages without login

---

## ✅ Success Criteria

All tests passed if:
- ✅ Can register as both Radiologist and Technician
- ✅ Login redirects to correct dashboard based on role
- ✅ Each dashboard has unique design and features
- ✅ Navigation bar changes based on role
- ✅ Access control prevents unauthorized access
- ✅ Sample data displays correctly in tables
- ✅ Bootstrap styling loads properly
- ✅ All buttons show appropriate messages
- ✅ Users stored in MongoDB with role field

---

## 🚀 Ready for Phase 3

Once all tests pass, the system is ready for:
- Image upload functionality
- Real scan data storage
- AI model integration
- Report generation system

---

**Test Status**: ⏳ Ready to test
**Server**: http://127.0.0.1:8000/
**Documentation**: See ROLE_BASED_SYSTEM.md for details

---

*Last Updated: November 15, 2025*
