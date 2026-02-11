from flask import Flask, render_template, request, redirect, url_for, send_file, flash, jsonify
import os
import pandas as pd
from werkzeug.utils import secure_filename
from data_processor import DataProcessor
from allocation_engine import AllocationEngine
from report_generator import ReportGenerator

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Configuration
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
OUTPUT_FOLDER = os.path.join(os.getcwd(), 'outputs')
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Global variable to store last allocation result (for demo/simplicity)
# In a real app, this would be in a database
last_allocation = {
    'results': [],
    'summary': {}
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Process Data
            df, original_cols = DataProcessor.process_file(filepath)
            
            # For demo, let's set course capacities (e.g., 40 spots each)
            courses = DataProcessor.get_course_list(df)
            capacities = {course: 40 for course in courses}
            
            # Allocation
            engine = AllocationEngine(df, capacities)
            results = engine.allocate()
            summary = engine.get_summary()
            
            # Store globally
            last_allocation['results'] = results
            last_allocation['summary'] = summary
            
            # Generate Reports
            excel_path = os.path.join(app.config['OUTPUT_FOLDER'], 'allocation_results.xlsx')
            pdf_path = os.path.join(app.config['OUTPUT_FOLDER'], 'allocation_report.pdf')
            
            ReportGenerator.generate_excel(results, excel_path)
            ReportGenerator.generate_pdf(results, summary, pdf_path)
            
            flash('Allocation completed successfully!', 'success')
            return redirect(url_for('results_page'))
            
        except Exception as e:
            flash(f'Error processing file: {str(e)}', 'error')
            return redirect(url_for('index'))
    
    flash('Invalid file format. Please upload .csv or .xlsx', 'error')
    return redirect(url_for('index'))

@app.route('/results')
def results_page():
    if not last_allocation['results']:
        return redirect(url_for('index'))
    
    # Calculate number of preference columns
    pref_count = 0
    if last_allocation['results']:
        pref_count = sum(1 for key in last_allocation['results'][0].keys() if key.startswith('Preference'))

    return render_template('results.html', 
                           results=last_allocation['results'], 
                           summary=last_allocation['summary'],
                           pref_count=pref_count)

@app.route('/download/<type>')
def download_file(type):
    if type == 'excel':
        filename = 'allocation_results.xlsx'
    elif type == 'pdf':
        filename = 'allocation_report.pdf'
    else:
        return "Invalid download type", 400
        
    path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "File not found", 404

if __name__ == '__main__':
    app.run(debug=True)
