# Smart Student Course Allocation System 🎓

A robust, secure, and modern web application built with Flask for automating the course allocation process for students. The system ensures fairness and efficiency by using a priority-based matching algorithm.

---

## 🚀 Features

- **Intelligent Allocation Engine**:
  - **Priority Sorting**: Students are ranked based on **GPA (descending)** and **Submission Timestamp (ascending)**.
  - **Preference Matching**: Automatically assigns students to their highest available choice based on course capacity.
- **Modern UI/UX**: Responsive dashboard with glassmorphism design, real-time analytics, and smooth transitions.
- **Security First**:
  - CSRF protection on all forms.
  - Password hashing via `scrypt`.
  - Admin-only access controlled by environment-based authentication.
- **Interactive Analytics**: Visualized course demand and occupancy rates.
- **Comprehensive Reporting**: Export allocation results to **Excel** or professional **PDF** formats.
- **Admin Control Panel**: Toggle preference edits, reset system state, and manage course capacities.

---

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.12+**
- **Git**

---

## ⚙️ Installation & Setup (Step-by-Step)

### 1. Clone the Repository

```powershell
git clone <your-repo-url>
cd SmartCourseAllocation
```

### 2. Set Up a Virtual Environment

**Windows:**

```powershell
python -m venv venv
.\venv\Scripts\activate
```

**macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Initialize the Database

This creates the SQLite database and sets up the default admin account.

```powershell
$env:FLASK_APP="app.py"
python -m flask init-db
```

### 5. Run the Application (Development)

```powershell
python -m flask run
```

_Visit **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your browser._

---

## 🌐 Production Deployment

For production environments, it is recommended to use a WSGI server like **Gunicorn**.

### Running with Gunicorn

```powershell
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

- `-w 4`: Number of worker processes.
- `-b 0.0.0.0:8000`: Binds the app to all interfaces on port 8000.

---

## 🔑 Accessing the System

### Admin Credentials

- **Username**: `admin`
- **Password**: Defined in your `.env` file (Default: `admin123`)

### Student Access

- Students must register via the **Registration** page.
- Once registered, they can login and submit their course preferences.

---

## 📂 Project Structure

- `app.py`: Main controller, routing, and Flask application factory.
- `models.py`: Database schema (Users, Students, Courses, Config).
- `allocation_engine.py`: Core logic for priority-matching and analytics.
- `data_processor.py`: Logic for parsing CSV/Excel uploads and validation.
- `report_generator.py`: Generates PDF and Excel export files.
- `templates/`: Jinja2 templates for the modern frontend.
- `static/index.css`: Custom CSS variables and styles.

---

## ⚠️ Troubleshooting

- **"Term 'flask' is not recognized"**: On Windows, always use `python -m flask` instead of just `flask` if the command is not in your PATH.
- **Dependency Issues**: Ensure you have `setuptools` updated (`pip install --upgrade setuptools`) if building `pandas` or `scikit-learn` from source.
- **Database Reset**: To start fresh, delete `instance/smart_allocation.db` and run `python -m flask init-db` again.

---

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.
