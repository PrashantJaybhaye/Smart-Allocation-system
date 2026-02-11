# Smart Student Course Allocation System 🎓

A robust, secure, and modern web application built with Flask for automating the course allocation process for students based on their preferences, GPA, and time of submission.

---

## 🚀 Features

- **Priority-Based Allocation**: Intelligent engine that considers GPA, submission time, and student preferences.
- **Student & Admin Dashboards**: Separate interfaces with glassmorphic design and real-time feedback.
- **Security First**: CSRF protection, password hashing (scrypt), and environment-based configuration.
- **Advanced Analytics**: Interactive charts showing course demand vs. occupancy.
- **Automated Reporting**: Export results to Excel and professional PDF reports.
- **Flexible Controls**: Admin can toggle preference re-submission and reset system data.

---

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.13+** (Recommended)
- **Git**

---

## ⚙️ Installation & Setup (Step-by-Step)

Follow these steps to get the project running on a new machine:

### 1. Clone the Repository

Open your terminal or PowerShell and run:

```bash
git clone <your-repo-url>
cd SmartCourseAllocation
```

### 2. Set Up a Virtual Environment (Recommended)

Windows:

```powershell
python -m venv venv
.\venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

Install the required packages. Note: The `requirements.txt` is optimized for Python 3.13.

```bash
pip install -r requirements.txt
```

### 4. Configure Environment (Optional)

The system has built-in defaults for local development. If you need custom settings (like a specific admin password), you can create a `.env` file:

```bash
# Optional: Create a .env file to override defaults
SECRET_KEY=your-secure-key
ADMIN_PASSWORD=your-password
```

_Open `.env` and update the `SECRET_KEY` and `ADMIN_PASSWORD` to your liking._

### 5. Initialize the Database

This step creates the tables and sets up the default admin account (`admin` / `admin123`).

```bash
$env:FLASK_APP="app.py"
python -m flask init-db
```

### 6. Run the Application

Start the Flask development server:

```bash
python -m flask run
```

---

## 🔑 Accessing the System

Once the server is running, visit **[http://127.0.0.1:5000](http://127.0.0.1:5000)**.

### Admin Login

- **Username**: `admin`
- **Password**: _The `ADMIN_PASSWORD` you set in `.env` (Default: `admin123`)_

### Student Access

- Students must **Register** first through the registration page.
- By default, newly registered accounts are assigned the `student` role.

---

## 📂 Project Structure

- `app.py`: Main application controller and routes.
- `models.py`: Database models (User, Student, Course, Config).
- `allocation_engine.py`: Logic for the priority-matching algorithm.
- `data_processor.py`: CSV/Excel file handling and validation.
- `report_generator.py`: PDF and Excel export logic.
- `templates/`: HTML templates with modern glassmorphism UI.
- `static/index.css`: Custom CSS for premium styling.

---

## ⚠️ Known Issues & Tips

- **Compiler Errors during Install**: If `pandas` fails to install, ensure you are using Python 3.12 or 3.13 which have pre-compiled wheels for newer versions.
- **Resetting Data**: Use the "Danger Zone" in the Admin dashboard carefully; it clears all student records while keeping user accounts intact.
- **DB Initialization**: If you change the schema in `models.py`, delete the `instance/smart_allocation.db` file and run `flask init-db` again.
