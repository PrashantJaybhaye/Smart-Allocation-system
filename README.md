# Smart Student Course Allocation System 🎓

A robust, secure, and modern web application built with **Flask** for automating the course allocation process for university students. The system ensures fairness and efficiency by using a **First-Come-First-Serve (FCFS)** based matching algorithm, prioritizing students based on their submission timestamp.

---

## 🚀 Key Features

### 🔹 For Administrators

- **Automated Allocation**: One-click execution of the allocation algorithm based on course capacity and student preferences.
- **Fairness Priority**: Students are strictly prioritized by their **Submission Timestamp**, ensuring a fair FCFS process.
- **Course Management**: Add, edit, and delete courses with real-time capacity tracking.
- **Student Management**:
  - Bulk upload students via **Excel/CSV**.
  - Manually edit student details.
  - Reset system data (Clear all students/courses) for new cycles.
- **System Configuration**: Toggle "Re-submission" mode to allow or block students from changing their preferences.
- **Analytics Dashboard**:
  - Real-time visualization of course demand vs. capacity.
  - Allocation success rates.
  - Faculty load distribution stats.
- **Export Reports**: Generate comprehensive results in **Excel** and professional **PDF** formats.

### 🔹 For Students

- **Secure Access**: Individual login accounts for every student.
- **Preference Submission**: Interactive drag-and-drop or selection interface to rank courses (Top 8 choices).
- **Personalized Dashboard**: View allocation status, assigned course, and profile details.
- **Mobile-Responsive**: Fully optimized for phones and tablets.

---

## 🛠️ Tech Stack

- **Backend**: Python (Flask), SQLAlchemy (ORM)
- **Database**: SQLite (Built-in, zero configuration)
- **Frontend**: HTML5, CSS3 (Custom Glassmorphism Design), JavaScript
- **Reporting**: ReportLab (PDF), Pandas/OpenPyXL (Excel)
- **Security**: Flask-Login, CSRF Protection, Werkzeug Security

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd SmartCourseAllocation
```

### 2. Create a Virtual Environment

**Windows:**

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

**macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize the Database

This command creates the database file and sets up the default admin account.

```bash
flask init-db
```

_Output: Admin user created with username 'admin'_

### 5. Run the Application

```bash
python app.py
```

Visit **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your browser.

---

## 🔑 Default Credentials

### Admin Account

- **Username**: `admin`
- **Password**: `admin123` (Change this in `.env` for production!)

### Student Account

- **Registration**: Students can register themselves via the `/register` page.
- **Bulk Upload**: Admin can upload a CSV with columns: `Student ID`, `Name`.

---

## 📂 Project Structure

```
SmartCourseAllocation/
├── app.py                 # Main application entry point & routes
├── models.py              # Database models (User, Student, Course)
├── allocation_engine.py   # Core logic for preference matching
├── data_processor.py      # handles CSV/Excel file parsing
├── report_generator.py    # Generates PDF/Excel reports
├── requirements.txt       # Project dependencies
├── instance/              # Contains the SQLite database
├── static/                # CSS, JS, and images
└── templates/             # HTML templates (Jinja2)
```

---

## ⚠️ Troubleshooting

- **"Command not found: flask"**: Ensure your virtual environment is activated. On Windows, try `python -m flask init-db`.
- **Database Errors**: If you encounter schema issues, delete the `instance/` folder and run `flask init-db` again to start fresh.
- **File Uploads**: Ensure your CSV/Excel file headers match the expected format: `Student ID`, `Name`, `Preference 1`, etc.

---

## 📝 License

Distributed under the MIT License.
