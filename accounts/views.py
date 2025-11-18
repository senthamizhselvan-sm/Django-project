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
    # Get all scans from MongoDB
    scans_collection = MongoDB.get_scans_collection()
    
    # Query pending scans
    pending_cursor = scans_collection.find({'status': 'Pending Analysis'}).sort('uploaded_at', -1)
    pending_scans = []
    for scan in pending_cursor:
        pending_scans.append({
            'id': str(scan['_id']),
            'patient_name': scan['patient_name'],
            'patient_id': scan.get('patient_id', 'N/A'),
            'scan_type': scan['scan_type'],
            'uploaded_date': scan['uploaded_at'].strftime('%Y-%m-%d') if hasattr(scan['uploaded_at'], 'strftime') else str(scan['uploaded_at']),
            'status': scan['status']
        })
    
    # Query completed scans
    completed_cursor = scans_collection.find({'status': 'Completed'}).sort('uploaded_at', -1).limit(5)
    completed_scans = []
    for scan in completed_cursor:
        completed_scans.append({
            'id': str(scan['_id']),
            'patient_name': scan['patient_name'],
            'patient_id': scan.get('patient_id', 'N/A'),
            'scan_type': scan['scan_type'],
            'uploaded_date': scan['uploaded_at'].strftime('%Y-%m-%d') if hasattr(scan['uploaded_at'], 'strftime') else str(scan['uploaded_at']),
            'status': scan['status']
        })
    
    # Calculate stats
    total_pending = len(pending_scans)
    total_completed = scans_collection.count_documents({'status': 'Completed'})
    total_under_review = scans_collection.count_documents({'status': 'Under Review'})
    
    context = {
        'user_name': request.session.get('user_name', 'Radiologist'),
        'pending_scans': pending_scans,
        'completed_scans': completed_scans,
        'total_pending': total_pending,
        'total_completed': total_completed,
        'total_under_review': total_under_review,
    }
    return render(request, 'radiologist_dashboard.html', context)


@role_required(['technician'])
def technician_dashboard(request):
    """Technician dashboard view"""
    # Get scans from MongoDB uploaded by current user
    scans_collection = MongoDB.get_scans_collection()
    user_email = request.session.get('user_email')
    
    # Query scans uploaded by this technician
    scans_cursor = scans_collection.find({'uploaded_by': user_email}).sort('uploaded_at', -1)
    
    uploaded_scans = []
    for scan in scans_cursor:
        uploaded_scans.append({
            'id': str(scan['_id']),
            'patient_name': scan['patient_name'],
            'patient_id': scan.get('patient_id', 'N/A'),
            'scan_type': scan['scan_type'],
            'uploaded_date': scan['uploaded_at'].strftime('%Y-%m-%d') if hasattr(scan['uploaded_at'], 'strftime') else str(scan['uploaded_at']),
            'status': scan['status']
        })
    
    # Calculate stats
    total_uploads = len(uploaded_scans)
    pending = sum(1 for s in uploaded_scans if s['status'] == 'Pending Analysis')
    under_review = sum(1 for s in uploaded_scans if s['status'] == 'Under Review')
    completed = sum(1 for s in uploaded_scans if s['status'] == 'Completed')
    
    context = {
        'user_name': request.session.get('user_name', 'Technician'),
        'uploaded_scans': uploaded_scans,
        'total_uploads': total_uploads,
        'pending': pending,
        'under_review': under_review,
        'completed': completed,
    }
    return render(request, 'technician_dashboard.html', context)


@role_required(['radiologist'])
def analyze_scan(request, scan_id):
    """Analyze scan view - display scan details and allow report submission"""
    from bson.objectid import ObjectId
    
    scans_collection = MongoDB.get_scans_collection()
    
    # Get scan from MongoDB
    try:
        scan = scans_collection.find_one({'_id': ObjectId(scan_id)})
    except:
        messages.error(request, 'Invalid scan ID!')
        return redirect('radiologist_dashboard')
    
    if not scan:
        messages.error(request, 'Scan not found!')
        return redirect('radiologist_dashboard')
    
    # Handle POST request - submit report
    if request.method == 'POST':
        report_text = request.POST.get('report_text', '').strip()
        
        if not report_text:
            messages.error(request, 'Report text is required!')
        else:
            from datetime import datetime
            # Update scan with report and status
            scans_collection.update_one(
                {'_id': ObjectId(scan_id)},
                {
                    '$set': {
                        'radiologist_report': report_text,
                        'reviewed_by': request.session.get('user_email'),
                        'reviewed_at': datetime.now(),
                        'status': 'Completed'
                    }
                }
            )
            messages.success(request, f'Report submitted successfully for patient {scan["patient_name"]}!')
            return redirect('radiologist_dashboard')
    
    # Prepare scan data for template
    scan_data = {
        'id': str(scan['_id']),
        'patient_name': scan['patient_name'],
        'patient_id': scan.get('patient_id', 'N/A'),
        'age': scan.get('age', 'N/A'),
        'gender': scan.get('gender', 'N/A'),
        'scan_type': scan['scan_type'],
        'scan_file_path': scan.get('scan_file_path', ''),
        'uploaded_by': scan.get('uploaded_by', 'Unknown'),
        'uploaded_at': scan['uploaded_at'].strftime('%Y-%m-%d %H:%M') if hasattr(scan['uploaded_at'], 'strftime') else str(scan['uploaded_at']),
        'status': scan['status'],
        'ai_prediction': scan.get('ai_prediction', None),
        'ai_confidence': scan.get('ai_confidence', None),
        'radiologist_report': scan.get('radiologist_report', ''),
    }
    
    context = {
        'scan': scan_data,
    }
    return render(request, 'view_scan.html', context)


@role_required(['radiologist', 'technician'])
def view_completed_reports(request):
    """View completed reports with filtering and pagination"""
    from datetime import datetime, timedelta
    from django.core.paginator import Paginator
    
    scans_collection = MongoDB.get_scans_collection()
    
    # Build query filter based on request parameters
    query_filter = {'status': 'Completed'}
    
    # Filter by patient name (search)
    patient_name = request.GET.get('name', '').strip()
    if patient_name:
        query_filter['patient_name'] = {'$regex': patient_name, '$options': 'i'}  # Case-insensitive search
    
    # Filter by scan type
    scan_type = request.GET.get('scan_type', '').strip()
    if scan_type:
        query_filter['scan_type'] = scan_type
    
    # Filter by date range
    from_date = request.GET.get('from_date', '').strip()
    to_date = request.GET.get('to_date', '').strip()
    
    if from_date or to_date:
        date_filter = {}
        if from_date:
            try:
                date_filter['$gte'] = datetime.strptime(from_date, '%Y-%m-%d')
            except ValueError:
                pass
        if to_date:
            try:
                # Add one day to include the entire end date
                to_datetime = datetime.strptime(to_date, '%Y-%m-%d')
                date_filter['$lte'] = to_datetime + timedelta(days=1)
            except ValueError:
                pass
        if date_filter:
            query_filter['uploaded_at'] = date_filter
    
    # Query completed scans with filters
    completed_cursor = scans_collection.find(query_filter).sort('reviewed_at', -1)
    
    # Convert to list for pagination
    all_completed_scans = []
    for scan in completed_cursor:
        all_completed_scans.append({
            'id': str(scan['_id']),
            'patient_name': scan['patient_name'],
            'patient_id': scan.get('patient_id', 'N/A'),
            'scan_type': scan['scan_type'],
            'uploaded_date': scan['uploaded_at'].strftime('%Y-%m-%d') if hasattr(scan['uploaded_at'], 'strftime') else str(scan['uploaded_at']),
            'reviewed_date': scan.get('reviewed_at').strftime('%Y-%m-%d %H:%M') if scan.get('reviewed_at') and hasattr(scan.get('reviewed_at'), 'strftime') else 'N/A',
            'reviewed_by': scan.get('reviewed_by', 'Unknown'),
            'status': scan['status']
        })
    
    # Pagination - 15 per page
    paginator = Paginator(all_completed_scans, 15)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get unique scan types for filter dropdown
    all_scan_types = scans_collection.distinct('scan_type')
    
    # Calculate statistics
    total_completed = len(all_completed_scans)
    
    context = {
        'page_obj': page_obj,
        'completed_scans': page_obj.object_list,
        'all_scan_types': all_scan_types,
        'total_completed': total_completed,
        # Preserve filter values
        'filter_name': patient_name,
        'filter_scan_type': scan_type,
        'filter_from_date': from_date,
        'filter_to_date': to_date,
    }
    return render(request, 'completed_reports.html', context)


@role_required(['radiologist'])
def view_pending_scans(request):
    """View pending scans - redirect to dashboard which shows pending scans"""
    return redirect('radiologist_dashboard')


@role_required(['technician'])
def upload_scan(request):
    """Upload scan view"""
    if request.method == 'POST':
        # Get form data
        patient_name = request.POST.get('patient_name', '').strip()
        patient_id = request.POST.get('patient_id', '').strip()
        age = request.POST.get('age', '').strip()
        gender = request.POST.get('gender', '').strip()
        scan_type = request.POST.get('scan_type', '').strip()
        scan_file = request.FILES.get('scan_file')
        
        # Validation
        if not all([patient_name, patient_id, age, gender, scan_type, scan_file]):
            messages.error(request, 'All fields are required!')
            return render(request, 'upload_scan.html')
        
        # Validate age
        try:
            age = int(age)
            if age <= 0 or age > 150:
                messages.error(request, 'Please enter a valid age!')
                return render(request, 'upload_scan.html')
        except ValueError:
            messages.error(request, 'Age must be a number!')
            return render(request, 'upload_scan.html')
        
        # Validate file extension
        allowed_extensions = ['jpg', 'jpeg', 'png', 'dcm', 'dicom']
        file_ext = scan_file.name.split('.')[-1].lower()
        if file_ext not in allowed_extensions:
            messages.error(request, 'Invalid file format! Allowed: JPG, PNG, JPEG, DICOM')
            return render(request, 'upload_scan.html')
        
        # Create media/scans directory if it doesn't exist
        import os
        from django.conf import settings
        from datetime import datetime
        
        scans_dir = os.path.join(settings.MEDIA_ROOT, 'scans')
        os.makedirs(scans_dir, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{patient_id}_{timestamp}.{file_ext}"
        file_path = os.path.join(scans_dir, filename)
        
        # Save file
        with open(file_path, 'wb+') as destination:
            for chunk in scan_file.chunks():
                destination.write(chunk)
        
        # Save to MongoDB
        scans_collection = MongoDB.get_scans_collection()
        scan_data = {
            'patient_name': patient_name,
            'patient_id': patient_id,
            'age': age,
            'gender': gender,
            'scan_type': scan_type,
            'scan_file_path': f'media/scans/{filename}',
            'uploaded_by': request.session.get('user_email'),
            'status': 'Pending Analysis',
            'uploaded_at': datetime.now()
        }
        scans_collection.insert_one(scan_data)
        
        messages.success(request, f'Scan uploaded successfully for patient {patient_name}!')
        return redirect('technician_dashboard')
    
    return render(request, 'upload_scan.html')


@role_required(['technician'])
def view_scans(request):
    """View all scans - placeholder"""
    return redirect('technician_dashboard')


@role_required(['technician'])
def view_scan_detail(request, scan_id):
    """View scan detail - placeholder"""
    messages.info(request, f'View scan detail feature coming soon! (Scan ID: {scan_id})')
    return redirect('technician_dashboard')


