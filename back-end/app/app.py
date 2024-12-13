from flask import Flask, request, redirect, render_template, send_from_directory, send_file, session, url_for
import os
from youhou import anon

app = Flask(__name__)


# Define the directory to save the uploaded PDF file
UPLOAD_FOLDER = 'uploads'  # You can change this path as needed


# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Route de login
@app.route('/login', methods=['POST'])
def login():
    session['username'] = request.form['username']
    return redirect(url_for('list_files'))

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username')
    return redirect(url_for('index'))

@app.route('/')
def index():
    context={"name":"Anonymiser un PDF",
             "test":"Entrer un fichier PDF",
             "ok":"Valider"}
      
    return render_template('index.html', context=context)

@app.route('/upload', methods=['POST'])
def upload_file():
  
    # Check if a file is part of the request
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']
    
    # If no file is selected
    if file.filename == '':
        return 'No selected file', 400
    
    # Check if the file is a PDF
    if file and file.filename.endswith('.pdf'):
        # Save the file to the uploads directory
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        anon(file_path)
        os.remove(file_path)
        return render_template('succes.html')
    else:
        return 'Invalid file format. Only PDF files are allowed.', 400
    
@app.route('/files')
def list_files():
    if 'username' in session:
        # Get a list of all files in the 'files' folder
        files = os.listdir("files")
        # Filter to only show PDF files
        pdf_files = [file for file in files if file.endswith('.pdf')]
        return render_template('list_files.html', files=pdf_files)
    else:
        return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_file(filename):
    # Send the requested file from the 'files' folder
    print("files/"+filename)
    return send_file("../files/"+filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
