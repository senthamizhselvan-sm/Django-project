"""
Views for user authentication and pages
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from functools import wraps
import bcrypt
from .mongodb import MongoDB


def role_required(allowed_roles):
    """Decorator to check if user has required role"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if 'user_id' not in request.session:
                messages.warning(request, 'Please login to access this page.')
                return redirect('login')
            
            user_role = request.session.get('user_role', '')
            if user_role not in allowed_roles:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('home')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def home(request):
    """Landing page view"""
    return render(request, 'home.html')


@require_http_methods(["GET", "POST"])
def register(request):
    """User registration view"""
    if request.method == 'POST':
        # Get form data
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        role = request.POST.get('role', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        # Validation
        if not all([full_name, email, role, password, confirm_password]):
            messages.error(request, 'All fields are required!')
            return render(request, 'register.html')
        
        if role not in ['radiologist', 'technician']:
            messages.error(request, 'Invalid role selected!')
            return render(request, 'register.html')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return render(request, 'register.html')
        
        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters long!')
            return render(request, 'register.html')
        
        # Check if email already exists
        users_collection = MongoDB.get_users_collection()
        existing_user = users_collection.find_one({'email': email})
        
        if existing_user:
            messages.error(request, 'Email already registered!')
            return render(request, 'register.html')
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Insert user into MongoDB
        user_data = {
            'full_name': full_name,
            'email': email,
            'role': role,
            'password': hashed_password.decode('utf-8')
        }
        users_collection.insert_one(user_data)
        
        messages.success(request, 'Registration successful! Please login.')
        return redirect('login')
    
    return render(request, 'register.html')


@require_http_methods(["GET", "POST"])
def login(request):
    """User login view"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        
        # Validation
        if not email or not password:
            messages.error(request, 'Email and password are required!')
            return render(request, 'login.html')
        
        # Find user in MongoDB
        users_collection = MongoDB.get_users_collection()
        user = users_collection.find_one({'email': email})
        
        if not user:
            messages.error(request, 'Invalid email or password!')
            return render(request, 'login.html')
        
        # Verify password
        if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            # Store user info in session
            request.session['user_id'] = str(user['_id'])
            request.session['user_name'] = user['full_name']
            request.session['user_email'] = user['email']
            request.session['user_role'] = user.get('role', 'user')
            
            messages.success(request, f'Welcome back, {user["full_name"]}!')
            
            # Role-based redirect
            user_role = user.get('role', 'user')
            if user_role == 'radiologist':
                return redirect('radiologist_dashboard')
            elif user_role == 'technician':
                return redirect('technician_dashboard')
            else:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid email or password!')
            return render(request, 'login.html')
    
    return render(request, 'login.html')


def dashboard(request):
    """Dashboard view for logged-in users"""
    # Check if user is logged in
    if 'user_id' not in request.session:
        messages.warning(request, 'Please login to access the dashboard.')
        return redirect('login')
    
    context = {
        'user_name': request.session.get('user_name', 'User'),
    }
    return render(request, 'dashboard.html', context)


def logout(request):
    """Logout view"""
    # Clear session
    request.session.flush()
    messages.success(request, 'You have been logged out successfully!')
    return redirect('home')


@role_required(['radiologist'])
def radiologist_dashboard(request):
    """Radiologist dashboard view"""
    # Sample data - will be replaced with real database queries later
    pending_scans = [
        {
            'id': 1,
            'patient_name': 'John Doe',
            'scan_type': 'X-Ray - Chest',
            'uploaded_date': '2025-11-14',
            'status': 'Pending Analysis'
        },
        {
            'id': 2,
            'patient_name': 'Jane Smith',
            'scan_type': 'CT Scan - Brain',
            'uploaded_date': '2025-11-13',
            'status': 'Pending Analysis'
        },
        {
            'id': 3,
            'patient_name': 'Robert Johnson',
            'scan_type': 'MRI - Spine',
            'uploaded_date': '2025-11-12',
            'status': 'Pending Analysis'
        },
    ]
    
    context = {
        'user_name': request.session.get('user_name', 'Radiologist'),
        'pending_scans': pending_scans,
    }
    return render(request, 'radiologist_dashboard.html', context)


@role_required(['technician'])
def technician_dashboard(request):
    """Technician dashboard view"""
    # Sample data - will be replaced with real database queries later
    uploaded_scans = [
        {
            'id': 1,
            'patient_name': 'John Doe',
            'scan_type': 'X-Ray - Chest',
            'uploaded_date': '2025-11-14',
            'status': 'Pending Analysis'
        },
        {
            'id': 2,
            'patient_name': 'Jane Smith',
            'scan_type': 'CT Scan - Brain',
            'uploaded_date': '2025-11-13',
            'status': 'Under Review'
        },
        {
            'id': 3,
            'patient_name': 'Robert Johnson',
            'scan_type': 'MRI - Spine',
            'uploaded_date': '2025-11-12',
            'status': 'Completed'
        },
    ]
    
    context = {
        'user_name': request.session.get('user_name', 'Technician'),
        'uploaded_scans': uploaded_scans,
    }
    return render(request, 'technician_dashboard.html', context)


@role_required(['radiologist'])
def analyze_scan(request, scan_id):
    """Analyze scan view - placeholder"""
    messages.info(request, f'Analyze scan feature coming soon! (Scan ID: {scan_id})')
    return redirect('radiologist_dashboard')


@role_required(['radiologist'])
def view_completed_reports(request):
    """View completed reports - placeholder"""
    messages.info(request, 'View completed reports feature coming soon!')
    return redirect('radiologist_dashboard')


@role_required(['radiologist'])
def view_pending_scans(request):
    """View pending scans - placeholder"""
    return redirect('radiologist_dashboard')


@role_required(['technician'])
def upload_scan(request):
    """Upload scan view - placeholder"""
    messages.info(request, 'Upload scan feature coming soon!')
    return redirect('technician_dashboard')


@role_required(['technician'])
def view_scans(request):
    """View all scans - placeholder"""
    return redirect('technician_dashboard')


@role_required(['technician'])
def view_scan_detail(request, scan_id):
    """View scan detail - placeholder"""
    messages.info(request, f'View scan detail feature coming soon! (Scan ID: {scan_id})')
    return redirect('technician_dashboard')


