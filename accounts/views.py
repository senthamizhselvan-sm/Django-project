"""
Views for user authentication and pages
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import FileResponse, HttpResponse, JsonResponse
from django.conf import settings
from functools import wraps
import bcrypt
from .mongodb import MongoDB
import os
from datetime import datetime, timedelta
from bson import ObjectId
from io import BytesIO
import qrcode
from collections import defaultdict, Counter
import calendar

# ReportLab imports for PDF generation
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas


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
        try:
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
            
        except Exception as e:
            print(f"MongoDB Error in registration: {e}")  # Log to server
            messages.error(request, 'Database connection error. Please try again later.')
            return render(request, 'register.html')
    
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
        
        try:
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
                
        except Exception as e:
            print(f"MongoDB Error in login: {e}")  # Log to server
            messages.error(request, 'Database connection error. Please try again later.')
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


@role_required(['radiologist', 'technician'])
def generate_pdf(request, scan_id):
    """
    Generate PDF report for completed radiology scan
    Accessible to both Radiologist and Technician roles
    """
    try:
        # Get scan from MongoDB
        scans_collection = MongoDB.get_scans_collection()
        scan = scans_collection.find_one({'_id': ObjectId(scan_id)})
        
        if not scan:
            messages.error(request, 'Scan not found.')
            return redirect('radiologist_dashboard' if request.session.get('user_role') == 'radiologist' else 'technician_dashboard')
        
        # Check if scan is completed
        if scan.get('status') != 'Completed':
            messages.warning(request, 'PDF can only be generated for completed reports.')
            return redirect('radiologist_dashboard' if request.session.get('user_role') == 'radiologist' else 'technician_dashboard')
        
        # Prepare file paths
        patient_name = scan.get('patient_name', 'Unknown').replace(' ', '_')
        pdf_filename = f"report_{patient_name}_{scan_id}.pdf"
        pdf_dir = os.path.join(settings.MEDIA_ROOT, 'reports')
        pdf_path = os.path.join(pdf_dir, pdf_filename)
        
        # Ensure reports directory exists
        os.makedirs(pdf_dir, exist_ok=True)
        
        # Create PDF buffer
        buffer = BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                              rightMargin=0.75*inch, leftMargin=0.75*inch,
                              topMargin=1*inch, bottomMargin=0.75*inch)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#6f42c1'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#6f42c1'),
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            fontName='Helvetica'
        )
        
        # Add Hospital Header
        elements.append(Paragraph("<b>🏥 AI-ASSISTED RADIOLOGY REPORTING SYSTEM</b>", title_style))
        elements.append(Paragraph("<i>Advanced Diagnostic Imaging Center</i>", 
                                ParagraphStyle('Subtitle', parent=styles['Normal'], 
                                             fontSize=12, alignment=TA_CENTER, 
                                             textColor=colors.grey, spaceAfter=20)))
        elements.append(Spacer(1, 0.3*inch))
        
        # Add horizontal line
        elements.append(Table([['']], colWidths=[6.5*inch], 
                             style=TableStyle([('LINEABOVE', (0,0), (-1,-1), 2, colors.HexColor('#6f42c1'))])))
        elements.append(Spacer(1, 0.2*inch))
        
        # Patient Information Section
        elements.append(Paragraph("PATIENT INFORMATION", heading_style))
        
        patient_data = [
            ['Patient Name:', scan.get('patient_name', 'N/A'), 'Patient ID:', scan.get('patient_id', 'N/A')],
            ['Age:', str(scan.get('age', 'N/A')), 'Gender:', scan.get('gender', 'N/A')],
            ['Scan Type:', scan.get('scan_type', 'N/A'), 'Status:', scan.get('status', 'N/A')]
        ]
        
        patient_table = Table(patient_data, colWidths=[1.5*inch, 1.75*inch, 1.5*inch, 1.75*inch])
        patient_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6f42c1')),
            ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#6f42c1')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(patient_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Date Information
        upload_date = scan.get('uploaded_at', datetime.now())
        review_date = scan.get('reviewed_at', datetime.now())
        
        date_data = [
            ['Scan Upload Date:', upload_date.strftime('%B %d, %Y at %I:%M %p') if isinstance(upload_date, datetime) else str(upload_date)],
            ['Report Completion Date:', review_date.strftime('%B %d, %Y at %I:%M %p') if isinstance(review_date, datetime) else str(review_date)]
        ]
        
        date_table = Table(date_data, colWidths=[2*inch, 4.5*inch])
        date_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6f42c1')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(date_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Radiologist Report Section
        elements.append(Paragraph("RADIOLOGIST REPORT", heading_style))
        
        report_content = scan.get('radiologist_report', 'No report available.')
        report_text = Paragraph(report_content, normal_style)
        
        report_table = Table([[report_text]], colWidths=[6.5*inch])
        report_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.grey),
            ('BACKGROUND', (0, 0), (-1, -1), colors.beige),
            ('PADDING', (0, 0), (-1, -1), 12),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(report_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # AI Prediction Section (if available)
        if scan.get('ai_prediction'):
            elements.append(Paragraph("AI ANALYSIS", heading_style))
            ai_data = [
                ['AI Prediction:', scan.get('ai_prediction', 'N/A')],
                ['Confidence Score:', f"{scan.get('ai_confidence', 'N/A')}%" if scan.get('ai_confidence') else 'N/A']
            ]
            ai_table = Table(ai_data, colWidths=[2*inch, 4.5*inch])
            ai_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6f42c1')),
                ('BACKGROUND', (0, 0), (-1, -1), colors.lightblue),
                ('PADDING', (0, 0), (-1, -1), 8),
            ]))
            elements.append(ai_table)
            elements.append(Spacer(1, 0.2*inch))
        
        # Radiologist Information
        elements.append(Spacer(1, 0.2*inch))
        radiologist_name = scan.get('reviewed_by', 'N/A')
        
        radiologist_data = [
            ['Reviewed By:', f"Dr. {radiologist_name}"],
            ['Role:', 'Radiologist'],
        ]
        
        radiologist_table = Table(radiologist_data, colWidths=[2*inch, 4.5*inch])
        radiologist_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6f42c1')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(radiologist_table)
        
        # Digital Signature Section
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("__________________________", 
                                ParagraphStyle('Signature', parent=styles['Normal'], 
                                             fontSize=10, alignment=TA_LEFT)))
        elements.append(Paragraph("<i>Digital Signature</i>", 
                                ParagraphStyle('SigText', parent=styles['Normal'], 
                                             fontSize=9, alignment=TA_LEFT, 
                                             textColor=colors.grey)))
        
        # Generate QR Code for verification
        elements.append(Spacer(1, 0.3*inch))
        
        # Create QR code with scan verification URL
        verification_url = f"{request.build_absolute_uri('/')[:-1]}/radiologist/analyze/{scan_id}/"
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(verification_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Save QR code to buffer
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        
        # Add QR code to PDF
        qr_image = Image(qr_buffer, width=1.2*inch, height=1.2*inch)
        
        qr_data = [
            [qr_image, Paragraph("<b>Scan Verification QR Code</b><br/><i>Scan to verify report authenticity</i>", 
                               ParagraphStyle('QRText', parent=styles['Normal'], 
                                            fontSize=9, alignment=TA_LEFT))]
        ]
        
        qr_table = Table(qr_data, colWidths=[1.5*inch, 5*inch])
        qr_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ]))
        elements.append(qr_table)
        
        # Footer
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Table([['']], colWidths=[6.5*inch], 
                             style=TableStyle([('LINEABOVE', (0,0), (-1,-1), 1, colors.grey)])))
        elements.append(Paragraph(
            f"<i>Report generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')} | Document ID: {scan_id}</i>",
            ParagraphStyle('Footer', parent=styles['Normal'], 
                         fontSize=8, alignment=TA_CENTER, 
                         textColor=colors.grey, spaceAfter=10)
        ))
        
        # Build PDF
        doc.build(elements)
        
        # Save PDF to file
        buffer.seek(0)
        with open(pdf_path, 'wb') as f:
            f.write(buffer.read())
        
        # Update MongoDB with PDF path
        relative_pdf_path = f"reports/{pdf_filename}"
        scans_collection.update_one(
            {'_id': ObjectId(scan_id)},
            {'$set': {'pdf_path': relative_pdf_path}}
        )
        
        # Return PDF as download response
        buffer.seek(0)
        response = FileResponse(buffer, as_attachment=True, filename=pdf_filename)
        response['Content-Type'] = 'application/pdf'
        
        messages.success(request, f'PDF report generated successfully: {pdf_filename}')
        return response
        
    except Exception as e:
        messages.error(request, f'Error generating PDF: {str(e)}')
        return redirect('radiologist_dashboard' if request.session.get('user_role') == 'radiologist' else 'technician_dashboard')


# ============================================================================
# ANALYTICS DASHBOARD VIEWS
# ============================================================================

@role_required(['radiologist', 'technician', 'admin'])
def analytics_dashboard(request):
    """
    LeetCode-style analytics dashboard with comprehensive statistics
    Accessible to all authenticated users (role-based data filtering)
    """
    try:
        scans_collection = MongoDB.get_scans_collection()
        users_collection = MongoDB.get_users_collection()
        
        user_role = request.session.get('user_role', '')
        user_email = request.session.get('user_email', '')
        
        # Base query filter based on role
        if user_role == 'technician':
            base_filter = {'uploaded_by': user_email}
        elif user_role == 'radiologist':
            base_filter = {'$or': [{'reviewed_by': user_email}, {'status': 'Pending Analysis'}]}
        else:  # admin
            base_filter = {}
        
        # Get all scans for this user
        all_scans = list(scans_collection.find(base_filter))
        
        # Add string ID to each scan for template rendering
        for scan in all_scans:
            scan['id'] = str(scan['_id'])
        
        # Calculate metrics
        total_scans = len(all_scans)
        completed_scans = len([s for s in all_scans if s.get('status') == 'Completed'])
        pending_scans = len([s for s in all_scans if s.get('status') == 'Pending Analysis'])
        under_review = len([s for s in all_scans if s.get('status') == 'Under Review'])
        
        # Calculate average processing time
        processing_times = []
        for scan in all_scans:
            if scan.get('status') == 'Completed' and scan.get('reviewed_at') and scan.get('uploaded_at'):
                upload_time = scan.get('uploaded_at')
                review_time = scan.get('reviewed_at')
                if isinstance(upload_time, datetime) and isinstance(review_time, datetime):
                    delta = review_time - upload_time
                    processing_times.append(delta.total_seconds() / 3600)  # hours
        
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
        
        # Get user stats
        total_users = users_collection.count_documents({})
        radiologists_count = users_collection.count_documents({'role': 'radiologist'})
        technicians_count = users_collection.count_documents({'role': 'technician'})
        
        # Scan type distribution
        scan_types = Counter([scan.get('scan_type', 'Unknown') for scan in all_scans])
        
        # Calculate badges/achievements
        badges = []
        if completed_scans >= 100:
            badges.append({'name': '100 Reports Completed', 'icon': '🏆', 'color': 'gold'})
        if completed_scans >= 50:
            badges.append({'name': '50 Reports Milestone', 'icon': '⭐', 'color': 'silver'})
        if completed_scans >= 10:
            badges.append({'name': '10 Reports Completed', 'icon': '🎯', 'color': 'bronze'})
        if avg_processing_time > 0 and avg_processing_time < 24:
            badges.append({'name': 'Fast Response 24H', 'icon': '⚡', 'color': 'blue'})
        if pending_scans == 0 and total_scans > 0:
            badges.append({'name': 'All Caught Up', 'icon': '✅', 'color': 'green'})
        
        # Calculate completion percentage
        completion_percentage = (completed_scans / total_scans * 100) if total_scans > 0 else 0
        
        context = {
            'user_name': request.session.get('user_name', ''),
            'user_email': user_email,
            'user_role': user_role,
            'total_scans': total_scans,
            'completed_scans': completed_scans,
            'pending_scans': pending_scans,
            'under_review': under_review,
            'avg_processing_time': round(avg_processing_time, 2),
            'total_users': total_users,
            'radiologists_count': radiologists_count,
            'technicians_count': technicians_count,
            'scan_types': dict(scan_types),
            'badges': badges,
            'completion_percentage': round(completion_percentage, 1),
            'recent_scans': all_scans[:10]  # Last 10 scans
        }
        
        return render(request, 'analytics_dashboard.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading dashboard: {str(e)}')
        return redirect('home')


@role_required(['radiologist', 'technician', 'admin'])
def api_daily_scans(request):
    """
    API endpoint: Returns daily scan counts for the last 30 days
    Returns JSON: {labels: [...], data: [...]}
    """
    try:
        scans_collection = MongoDB.get_scans_collection()
        user_role = request.session.get('user_role', '')
        user_email = request.session.get('user_email', '')
        
        # Filter based on role
        if user_role == 'technician':
            base_filter = {'uploaded_by': user_email}
        elif user_role == 'radiologist':
            base_filter = {'reviewed_by': user_email}
        else:
            base_filter = {}
        
        # Get scans from last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        all_scans = list(scans_collection.find(base_filter))
        
        # Group by date
        daily_counts = defaultdict(int)
        for scan in all_scans:
            upload_date = scan.get('uploaded_at')
            if upload_date and isinstance(upload_date, datetime) and upload_date >= thirty_days_ago:
                date_key = upload_date.strftime('%Y-%m-%d')
                daily_counts[date_key] += 1
        
        # Generate labels for all 30 days
        labels = []
        data = []
        for i in range(30):
            date = datetime.now() - timedelta(days=29-i)
            date_key = date.strftime('%Y-%m-%d')
            labels.append(date.strftime('%b %d'))
            data.append(daily_counts.get(date_key, 0))
        
        return JsonResponse({
            'labels': labels,
            'data': data
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@role_required(['radiologist', 'technician', 'admin'])
def api_scan_types(request):
    """
    API endpoint: Returns scan type distribution
    Returns JSON: {labels: [...], data: [...]}
    """
    try:
        scans_collection = MongoDB.get_scans_collection()
        user_role = request.session.get('user_role', '')
        user_email = request.session.get('user_email', '')
        
        if user_role == 'technician':
            base_filter = {'uploaded_by': user_email}
        elif user_role == 'radiologist':
            base_filter = {'reviewed_by': user_email}
        else:
            base_filter = {}
        
        all_scans = list(scans_collection.find(base_filter))
        scan_types = Counter([scan.get('scan_type', 'Unknown') for scan in all_scans])
        
        return JsonResponse({
            'labels': list(scan_types.keys()),
            'data': list(scan_types.values())
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@role_required(['admin', 'radiologist'])
def api_workload_distribution(request):
    """
    API endpoint: Returns workload distribution among radiologists
    Returns JSON: {labels: [...], data: [...]}
    """
    try:
        scans_collection = MongoDB.get_scans_collection()
        
        # Get completed scans
        completed_scans = list(scans_collection.find({'status': 'Completed'}))
        
        # Count scans per radiologist
        workload = Counter([scan.get('reviewed_by', 'Unassigned') for scan in completed_scans])
        
        return JsonResponse({
            'labels': list(workload.keys()),
            'data': list(workload.values())
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@role_required(['radiologist', 'technician', 'admin'])
def api_heatmap_data(request):
    """
    API endpoint: Returns heatmap data for activity grid (last 365 days)
    Returns JSON: [{date: 'YYYY-MM-DD', count: X}, ...]
    """
    try:
        scans_collection = MongoDB.get_scans_collection()
        user_role = request.session.get('user_role', '')
        user_email = request.session.get('user_email', '')
        
        if user_role == 'technician':
            base_filter = {'uploaded_by': user_email}
        elif user_role == 'radiologist':
            base_filter = {'reviewed_by': user_email}
        else:
            base_filter = {}
        
        # Get scans from last 365 days
        one_year_ago = datetime.now() - timedelta(days=365)
        all_scans = list(scans_collection.find(base_filter))
        
        # Group by date
        daily_counts = defaultdict(int)
        for scan in all_scans:
            upload_date = scan.get('uploaded_at')
            if upload_date and isinstance(upload_date, datetime) and upload_date >= one_year_ago:
                date_key = upload_date.strftime('%Y-%m-%d')
                daily_counts[date_key] += 1
        
        # Convert to list format
        heatmap_data = [{'date': date, 'count': count} for date, count in daily_counts.items()]
        
        return JsonResponse(heatmap_data, safe=False)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@role_required(['radiologist', 'technician', 'admin'])
def api_performance_chart(request):
    """
    API endpoint: Returns daily performance metrics (last 7 days)
    Returns JSON: {labels: [...], completed: [...], pending: [...]}
    """
    try:
        scans_collection = MongoDB.get_scans_collection()
        user_role = request.session.get('user_role', '')
        user_email = request.session.get('user_email', '')
        
        if user_role == 'technician':
            base_filter = {'uploaded_by': user_email}
        elif user_role == 'radiologist':
            base_filter = {'reviewed_by': user_email}
        else:
            base_filter = {}
        
        # Get scans from last 7 days
        seven_days_ago = datetime.now() - timedelta(days=7)
        all_scans = list(scans_collection.find(base_filter))
        
        # Group by date and status
        daily_completed = defaultdict(int)
        daily_pending = defaultdict(int)
        
        for scan in all_scans:
            upload_date = scan.get('uploaded_at')
            if upload_date and isinstance(upload_date, datetime) and upload_date >= seven_days_ago:
                date_key = upload_date.strftime('%Y-%m-%d')
                if scan.get('status') == 'Completed':
                    daily_completed[date_key] += 1
                else:
                    daily_pending[date_key] += 1
        
        # Generate labels for all 7 days
        labels = []
        completed_data = []
        pending_data = []
        
        for i in range(7):
            date = datetime.now() - timedelta(days=6-i)
            date_key = date.strftime('%Y-%m-%d')
            labels.append(date.strftime('%a'))
            completed_data.append(daily_completed.get(date_key, 0))
            pending_data.append(daily_pending.get(date_key, 0))
        
        return JsonResponse({
            'labels': labels,
            'completed': completed_data,
            'pending': pending_data
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


