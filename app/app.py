from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_mysqldb import MySQL
import os
import pandas as pd
from fpdf import FPDF
import pdfkit

app = Flask(__name__)
app.secret_key = 'secret_key'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'hospital'
mysql = MySQL(app)

# File Upload Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'csv'}

# PDF Export Configuration
pdf_options = {
    'page-size': 'A4',
    'margin-top': '0.75in',
    'margin-right': '0.75in',
    'margin-bottom': '0.75in',
    'margin-left': '0.75in'
}

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/facilities')
def facilities():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM facilities')
    facilities = cur.fetchall()
    cur.close()
    return render_template('facilities.html', facilities=facilities)

@app.route('/procedures')
def procedures():
    cur = mysql.connection.cursor()
    cur.execute('SELECT procedures.*, facilities.name AS facility_name, pro_types.name AS procedure_type FROM procedures \
                 JOIN facilities ON procedures.fac_id = facilities.id \
                 JOIN pro_types ON procedures.proc_type_id = pro_types.id')
    procedures = cur.fetchall()
    cur.close()
    return render_template('procedures.html', procedures=procedures)

@app.route('/pro_types')
def pro_types():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM pro_types')
    pro_types = cur.fetchall()
    cur.close()
    return render_template('pro_types.html', pro_types=pro_types)

@app.route('/ratings')
def ratings():
    cur = mysql.connection.cursor()
    cur.execute('SELECT rating.*, facilities.name AS facility_name FROM rating \
                 JOIN facilities ON rating.fac_id = facilities.id')
    ratings = cur.fetchall()
    cur.close()
    return render_template('ratings.html', ratings=ratings)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file and '.' in file.filename and file.filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']:
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash(f'{filename} uploaded successfully.')
    else:
        flash('Invalid file type. Please upload a CSV file.')
    return redirect(url_for(request.form['redirect']))
@app.route('/export', methods=['POST'])
def export():
    cur = mysql.connection.cursor()
    query = request.form['query']
    filename = request.form['filename']
    if query == 'same_rating_safety':
        cur.execute('SELECT rating.*, facility.name AS facility_name FROM rating \
                     JOIN facility ON rating.fac_id = facility.id \
                     WHERE rating.safety = (SELECT safety FROM rating \
                                           WHERE fac_id = 1)')
    elif query == 'avg_heart_attack_quality':
        cur.execute('SELECT facility.*, AVG(procedures.quality) AS avg_quality FROM facility \
                     JOIN procedures ON facility.id = procedures.fac_id \
                     WHERE procedures.proc_type_id = (SELECT id FROM pro_types WHERE name = "Heart Attack") \
                     GROUP BY facility.id \
                     HAVING avg_quality >= (SELECT AVG(quality) FROM procedures \
                                            WHERE proc_type_id = (SELECT id FROM pro_types WHERE name = "Heart Attack"))')
    elif query == 'zero_hip_knee_cost':
        cur.execute('SELECT * FROM procedures \
                     WHERE cost = 0 AND proc_type_id = (SELECT id FROM pro_types WHERE name = "Hip Knee")')
    else:
        flash('Invalid query', 'danger')
        return redirect(url_for('dashboard'))

    data = cur.fetchall()
    cur.close()

    column_names = [i[0] for i in cur.description]

    # Create PDF report
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(40, 10, 'Report')
    pdf.ln()

    # Add table
    pdf.set_font('Arial', 'B', 12)
    for col_name in column_names:
        pdf.cell(40, 10, col_name, 1)
    pdf.ln()
    pdf.set_font('Arial', '', 12)
    for row in data:
        for col in row:
            pdf.cell(40, 10, str(col), 1)
        pdf.ln()

    # Save PDF file
    pdf.output(f'{filename}.pdf')

    flash(f'Report saved as {filename}.pdf', 'success')
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run(debug=True, port=8000)