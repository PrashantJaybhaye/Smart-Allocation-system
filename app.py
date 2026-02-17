from flask import Flask, render_template, request, redirect, url_for, send_file, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from io import BytesIO, StringIO
import pandas as pd
from models import db, User, Student, Course, SystemConfig
from data_processor import DataProcessor
from allocation_engine import AllocationEngine
from report_generator import ReportGenerator
from datetime import datetime
from flask_wtf.csrf import CSRFProtect
import logging
from dotenv import load_dotenv
import re

# Automatically load .env file if it exists, but don't fail if it doesn't
load_dotenv()

app = Flask(__name__)

# Security: Load secret key from environment or generate a secure one for development
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
if not app.config['SECRET_KEY']:
    if os.environ.get('FLASK_ENV') == 'development' or os.environ.get('FLASK_DEBUG') == '1':
        app.config['SECRET_KEY'] = 'dev-key-secure-in-prod'
    else:
        # Generate a random one if missing in prod (safer than hardcoded)
        app.config['SECRET_KEY'] = os.urandom(24).hex()

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.config['OUTPUT_FOLDER'] = os.path.join(os.getcwd(), 'outputs')

csrf = CSRFProtect(app)
db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Auth Routes ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.verify_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Sanitization
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        student_class = request.form.get('student_class', '').strip()
        roll_no = request.form.get('roll_no', '').strip()
        mobile = request.form.get('mobile', '').strip()
        department = request.form.get('department', '').strip()
        
        # Validation
        if not all([username, password, full_name, email, student_class, roll_no, mobile, department]):
            flash('All fields are required.', 'error')
            return render_template('register.html')

        # 1. UserID Validation
        if not re.match(r'^\d{12}$', username):
            flash('UserID must be exactly 12 digits.', 'error')
            return render_template('register.html')
            
        if not (1 <= len(roll_no) <= 10):
            flash('Roll number must be between 1 and 10 characters.', 'error')
            return render_template('register.html')

        # 2. Password Strength
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('register.html')
            
        # 3. Mobile Validation
        if not re.match(r'^\d{10}$', mobile):
            flash('Mobile number must be exactly 10 digits.', 'error')
            return render_template('register.html')

        # 4. Email Validation (Stricter)
        if not re.match(r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$', email):
           flash('Invalid email address format.', 'error')
           return render_template('register.html')

        # 5. Full Name Validation
        if not re.match(r'^[a-zA-Z\s]+$', full_name) or len(full_name) < 3 or len(full_name) > 30:
            flash('Full name must contain only letters and spaces (3-30 chars).', 'error')
            return render_template('register.html')

        # 6. Allowed Values
        allowed_classes = ['FY', 'SY', 'TY', 'Final Year']
        if student_class not in allowed_classes:
            flash('Invalid class selection.', 'error')
            return render_template('register.html')
            
        allowed_departments = [
            "Agricultural Engineering", "Computer Science Engineering", "Civil Engineering",
            "Computer Science Design", "Electronics and Computer Engineering", 
            "Artificial Intelligence and Data Science", "Mechanical Engineering", 
            "Electrical Engineering", "Mechatronics Engineering", 
            "Plastics and Polymer Engineering", "Electronics and Telecommunication Engineering", 
            "Information Technology"
        ]
        if department not in allowed_departments:
            flash('Invalid department selection.', 'error')
            return render_template('register.html')
        
        # Security: Prevent privilege escalation by ignoring 'role' from form
        role = 'student' # Default role
        
        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            flash('UserID already exists', 'error')
        else:
            # 1. Create User Login
            new_user = User(username=username, role=role)
            new_user.password = password
            db.session.add(new_user)
            
            # 2. Create Student Profile
            # Check if student record exists (e.g. from bulk upload)
            student = Student.query.filter_by(student_id=username).first()
            
            if student:
                # Update existing record with registration details
                student.name = full_name
                student.email = email
                student.student_class = student_class
                student.roll_no = roll_no
                student.mobile_no = mobile
                student.department = department
            else:
                # Create new student record
                new_student = Student(
                    student_id=username,
                    name=full_name,
                    email=email,
                    student_class=student_class,
                    roll_no=roll_no,
                    mobile_no=mobile,
                    department=department
                )
                db.session.add(new_student)
            
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- Helpers ---
def get_config(key, default=None):
    cfg = SystemConfig.query.filter_by(key=key).first()
    return cfg.value if cfg else default

def set_config(key, value):
    cfg = SystemConfig.query.filter_by(key=key).first()
    if not cfg:
        cfg = SystemConfig(key=key, value=str(value))
        db.session.add(cfg)
    else:
        cfg.value = str(value)
    db.session.commit()

# --- Main App Routes ---
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    allow_repref = get_config('allow_repref', 'false').lower() == 'true'
    if current_user.role == 'admin':
        students = Student.query.all()
        courses = Course.query.all()
        return render_template('admin_dashboard.html', 
                               students=students, 
                               courses=courses, 
                               allow_repref=allow_repref)
    else:
        student_record = Student.query.filter_by(student_id=current_user.username).first()
        courses = Course.query.all()
        recommendations = student_record.get_recommendations() if student_record else []
        
        # Check if they can still submit
        already_submitted = student_record and student_record.preferences
        can_submit = not already_submitted or allow_repref
        
        # Number of preference slots = min(available courses, 8)
        num_preferences = min(len(courses), 8)
        
        return render_template('student_dashboard.html', 
                               student=student_record, 
                               courses=courses,
                               recommendations=recommendations,
                               can_submit=can_submit,
                               num_preferences=num_preferences)

@app.route('/submit_preferences', methods=['POST'])
@login_required
def submit_preferences():
    if current_user.role != 'student':
        return "Unauthorized", 403
    
    student = Student.query.filter_by(student_id=current_user.username).first()
    allow_repref = get_config('allow_repref', 'false').lower() == 'true'
    
    if student and student.preferences and not allow_repref:
        flash('Preference re-submission is currently disabled.', 'error')
        return redirect(url_for('dashboard'))

    prefs = request.form.getlist('preferences')
    
    # Validate: all preference slots must be filled (not empty)
    courses = Course.query.all()
    expected_count = min(len(courses), 8)
    # Remove any empty values
    prefs = [p for p in prefs if p.strip()]
    if len(prefs) < expected_count:
        flash(f'All {expected_count} preference fields are required. Please fill every slot.', 'error')
        return redirect(url_for('dashboard'))
    
    # Update or Create Student Record
    student = Student.query.filter_by(student_id=current_user.username).first()
    if not student:
        student = Student(student_id=current_user.username, name=current_user.username)
        db.session.add(student)
    
    student.preferences = prefs
    student.submission_time = datetime.now() 
    db.session.commit()
    flash('Preferences submitted successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/admin/students')
@login_required
def admin_students_list():
    if current_user.role != 'admin':
        return "Unauthorized", 403
    
    students = Student.query.all()
    return render_template('admin_students.html', students=students)

@app.route('/admin/student/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_student(id):
    if current_user.role != 'admin':
        return "Unauthorized", 403
        
    student = Student.query.get_or_404(id)
    
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        student_class = request.form.get('student_class')
        roll_no = request.form.get('roll_no')
        mobile = request.form.get('mobile')
        department = request.form.get('department')
        
        # Validation (mirrors register)
        if not all([full_name, email, student_class, roll_no, mobile, department]):
            flash('All fields are required.', 'error')
            return render_template('edit_student.html', student=student)

        if not re.match(r'^\d{10}$', mobile):
            flash('Mobile number must be exactly 10 digits.', 'error')
            return render_template('edit_student.html', student=student)

        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
           flash('Invalid email address format.', 'error')
           return render_template('edit_student.html', student=student)

        student.name = full_name
        student.email = email
        student.student_class = student_class
        student.roll_no = roll_no
        student.mobile_no = mobile
        student.department = department
        
        try:
            db.session.commit()
            flash('Student updated successfully!', 'success')
            return redirect(url_for('admin_students_list'))
        except Exception as e:
            db.session.rollback()
            app.logger.exception("Error updating student")
            flash('Error updating student, please try again.', 'error')
            
    return render_template('edit_student.html', student=student)

@app.route('/admin/student/delete/<int:id>', methods=['POST'])
@login_required
def delete_student(id):
    if current_user.role != 'admin':
        return "Unauthorized", 403
        
    student = Student.query.get_or_404(id)
    try:
        # Check if student has a linked User account and delete it too
        user = User.query.filter_by(username=student.student_id).first()
        if user:
            db.session.delete(user)
            
        db.session.delete(student)
        db.session.commit()
        flash('Student deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.exception("Error deleting student")
        flash('An error occurred while deleting the student.', 'error')
        
    return redirect(url_for('admin_students_list'))

@app.route('/admin/course/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_course(id):
    if current_user.role != 'admin':
        return "Unauthorized", 403
        
    course = Course.query.get_or_404(id)
    
    if request.method == 'POST':
        course.name = request.form.get('name')
        
        cap_raw = request.form.get('capacity')
        if cap_raw:
            try:
                cap = int(cap_raw)
                if cap < 1: 
                    raise ValueError("Capacity must be >= 1")
                course.capacity = cap
            except ValueError:
                flash('Invalid capacity value', 'error')
                return render_template('edit_course.html', course=course)
            
        try:
            db.session.commit()
            flash('Course updated successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            app.logger.exception("Error updating course")
            flash('An error occurred updating the course. Please try again or contact support.', 'error')
            
    return render_template('edit_course.html', course=course)

@app.route('/admin/course/delete/<int:id>', methods=['POST'])
@login_required
def delete_course(id):
    if current_user.role != 'admin':
        return "Unauthorized", 403
        
    course = Course.query.get_or_404(id)
    try:
        db.session.delete(course)
        db.session.commit()
        flash('Course deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting course: {str(e)}', 'error')
        
    return redirect(url_for('dashboard'))

@app.route('/admin/upload_students', methods=['POST'])
@login_required
def upload_students():
    if current_user.role != 'admin':
        return "Unauthorized", 403
    
    file = request.files.get('file')
    if file:
        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        
        try:
            df, _ = DataProcessor.process_file(path)
            for _, row in df.iterrows():
                # Check if student already exists
                student = Student.query.filter_by(student_id=str(row['Student ID'])).first()
                if not student:
                    student = Student(student_id=str(row['Student ID']), name=row['Name'])
                    db.session.add(student)
                
                student.name = row['Name']
                # Collect all preference columns
                prefs = [row[f'Preference {i}'] for i in range(1, 9) if f'Preference {i}' in row and pd.notna(row[f'Preference {i}'])]
                student.preferences = prefs
                
                # GPA removed
                # if 'GPA' in row: student.gpa = float(row['GPA'])
                
            db.session.commit()
            flash('Students imported successfully!', 'success')
        except Exception:
            logging.exception("Error during student upload")
            flash('Unable to complete the student import. Please check the file format.', 'error')
            
    return redirect(url_for('dashboard'))

@app.route('/admin/setup_courses', methods=['POST'])
@login_required
def setup_courses():
    if current_user.role != 'admin':
        return "Unauthorized", 403
    
    name = request.form.get('name')
    cap_raw = request.form.get('capacity')
    
    if not name or not cap_raw:
        flash('Course name and capacity are required.', 'error')
        return redirect(url_for('dashboard'))
        
    try:
        cap = int(cap_raw)
        if cap < 1:
            raise ValueError("Capacity must be at least 1")
    except (ValueError, TypeError):
        flash('Invalid capacity value. Must be a positive integer.', 'error')
        return redirect(url_for('dashboard'))
    
    course = Course.query.filter_by(name=name).first()
    # faculty_name is no longer used/collected
    
    if not course:
        course = Course(name=name, capacity=cap) # Faculty removed
        db.session.add(course)
    else:
        course.capacity = cap
    
    db.session.commit()
    flash(f'Course {name} updated/added.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/admin/run_allocation', methods=['POST'])
@login_required
def run_allocation():
    if current_user.role != 'admin':
        return "Unauthorized", 403
    
    students = Student.query.all()
    courses = Course.query.all()
    
    try:
        engine = AllocationEngine(students, courses)
        results = engine.allocate()
        db.session.commit() # Save allocations to DB
        
        # Generate reports
        summary = engine.get_analytics()
        ReportGenerator.generate_excel(results, os.path.join(app.config['OUTPUT_FOLDER'], 'results.xlsx'))
        ReportGenerator.generate_pdf(results, summary, os.path.join(app.config['OUTPUT_FOLDER'], 'report.pdf'))
        
        flash('Allocation optimized and completed!', 'success')
    except Exception:
        logging.exception("Error during allocation engine run")
        flash('An error occurred during allocation processing.', 'error')
        
    return redirect(url_for('admin_results'))

@app.route('/admin/results')
@login_required
def admin_results():
    if current_user.role != 'admin':
        return "Unauthorized", 403
    
    students = Student.query.all()
    courses = Course.query.all()
    engine = AllocationEngine(students, courses)
    analytics = engine.get_analytics()
    
    return render_template('admin_results.html', students=students, analytics=analytics, courses=courses)

@app.route('/download/<type>')
@login_required
def download_file(type):
    if current_user.role != 'admin':
        return "Unauthorized", 403
        
    if type == 'excel':
        filename = 'results.xlsx'
    elif type == 'pdf':
        filename = 'report.pdf'
    else:
        return "Invalid download type", 400
        
    path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "File not found. Please run allocation first.", 404

@app.route('/admin/toggle_repref', methods=['POST'])
@login_required
def toggle_repref():
    if current_user.role != 'admin':
        return "Unauthorized", 403
    
    current_val = get_config('allow_repref', 'false')
    new_val = 'true' if current_val == 'false' else 'false'
    set_config('allow_repref', new_val)
    
    status = "enabled" if new_val == 'true' else "disabled"
    flash(f'Student re-preference {status}!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/admin/reset_data', methods=['POST'])
@login_required
def reset_data():
    if current_user.role != 'admin':
        return "Unauthorized", 403
    
    if request.form.get('confirm') != 'yes':
        flash('Reset cancelled. You must confirm to proceed.', 'error')
        return redirect(url_for('dashboard'))

    try:
        # Delete students and courses
        # We keep Users (accounts) but reset their roles' data
        Student.query.delete()
        Course.query.delete()
        db.session.commit()
        
        # Also delete generated reports
        for f in ['results.xlsx', 'report.pdf']:
            path = os.path.join(app.config['OUTPUT_FOLDER'], f)
            if os.path.exists(path): os.remove(path)
            
        flash('All system data (Students & Courses) has been reset.', 'success')
    except Exception:
        logging.exception("Error during system reset")
        flash('An error occurred during system reset.', 'error')
        
    return redirect(url_for('dashboard'))

@app.cli.command("init-db")
def init_db_command():
    """Clear existing data and create new tables."""
    db.create_all()
    
    # Use environment provided password if available
    admin_pass = os.environ.get('ADMIN_PASSWORD', 'admin123')
    
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', role='admin')
        admin.password = admin_pass
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user created with username 'admin'")
    else:
        print("Admin user already exists.")
        
    if not SystemConfig.query.filter_by(key='allow_repref').first():
        config = SystemConfig(key='allow_repref', value='false')
        db.session.add(config)
        db.session.commit()
        print("Default system configuration initialized.")
    
    print("Database initialized successfully.")

@app.route('/admin/export_course/<int:course_id>')
@login_required
def export_course_data(course_id):
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'error')
        return redirect(url_for('dashboard'))

    course = Course.query.get(course_id)
    if not course:
        flash('Course not found.', 'error')
        return redirect(url_for('admin_results'))

    # Fetch students allocated to this course
    students = Student.query.filter_by(allocated_course_id=course.id).all()
    
    if not students:
        flash(f'No students allocated to {course.name}.', 'warning')
        return redirect(url_for('admin_results'))

    # Create CSV data
    data = []
    for s in students:
        data.append({
            'Student ID': s.student_id,
            'Name': s.name,
            'Department': s.department,
            'Class': s.student_class,
            'Roll No': s.roll_no,
            'Mobile': s.mobile_no,
            'Email': s.email
        })
    
    df = pd.DataFrame(data)
    
    # Generate response
    output = StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    
    return send_file(
        BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'{course.name.replace(" ", "_")}_Allocations.csv'
    )

if __name__ == "__main__":
    # Check if we are in development mode (default to true for local run)
    if os.environ.get('FLASK_ENV', 'development') == 'development':
        try:
            from livereload import Server
            server = Server(app.wsgi_app)
            # Watch templates and static files for changes
            server.watch('templates/*.html')
            server.watch('static/*.css')
            server.watch('static/*.js')
            print("🚀 Starting development server with LiveReload on http://127.0.0.1:5000")
            server.serve(port=5000, debug=True)
        except ImportError:
            print("⚠️ LiveReload not installed. Falling back to standard Flask runner.")
            print("💡 Tip: Run 'pip install livereload' for auto-browser refreshing.")
            app.run(debug=True)
    else:
        # Production mode
        app.run(debug=False, host='0.0.0.0')
