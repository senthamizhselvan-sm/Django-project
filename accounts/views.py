"""
Views for user authentication and pages
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
import bcrypt
from .mongodb import MongoDB


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
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        # Validation
        if not all([full_name, email, password, confirm_password]):
            messages.error(request, 'All fields are required!')
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
            
            messages.success(request, f'Welcome back, {user["full_name"]}!')
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

