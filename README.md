# Smart Student Course Allocation System

A complete web-based system to automate student course allocation based on preferences and seat limits.

## Features

- **Efficient Allocation**: Logic prioritizes Preference 1, falls back to Preference 2 and 3 if seats are full.
- **Data Cleaning**: Automatically removes duplicates and handles missing fields.
- **Export Formats**: Generate Excel results and professional PDF reports.
- **Modern UI**: Clean, responsive dashboard for uploading and viewing results.
- **Modular Code**: Separate engines for data processing, allocation, and reporting.

## Project Structure

- `app.py`: Main Flask application shell.
- `data_processor.py`: Handles file validation and cleaning.
- `allocation_engine.py`: Core preference-based allocation logic.
- `report_generator.py`: Generates final Excel and PDF files.
- `templates/`: HTML frontend files.
- `static/`: CSS for styling.
- `uploads/`: Temporary storage for uploaded student lists.
- `outputs/`: Generated reports and results.

## Requirements

- Python 3.8+
- Flask
- Pandas
- Openpyxl (for Excel support)
- Reportlab (for PDF generation)

## How to Run Locally

1. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:

   ```bash
   python app.py
   ```

3. **Access the App**:
   Open your browser and go to `http://127.0.0.1:5000`

## Sample Format

The system expects a CSV or Excel file with at least the following columns:

- `Student ID`
- `Name`
- `Preference 1`
- `Preference 2` (Optional)
- `Preference 3` (Optional)

A `sample_data.csv` is provided in the root directory for testing. Note: In the demo, each course is limited to **2 seats** to demonstrate the fallback/unassigned logic. This can be adjusted in `app.py`.
