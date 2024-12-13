from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
import os
from werkzeug.utils import secure_filename

main = Blueprint('main', __name__)

UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
main.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@main.route('/')
def home():
    context={"name":"Bonjour",
             "test":"Entrer un fichier PDF",
             "ok":"Valider"}
    return render_template('index.html', context=context)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in main.config['ALLOWED_EXTENSIONS']

# Route to handle file upload
@main.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        # Create uploads folder if it doesn't exist
        if not os.path.exists(main.config['UPLOAD_FOLDER']):
            os.makedirs(main.config['UPLOAD_FOLDER'])
        
        filename = file.filename
        file_path = os.path.join(main.config['UPLOAD_FOLDER'], filename)
        
        # Save the file to the server
        file.save(file_path)
        return jsonify({"message": f"File {filename} uploaded successfully!"}), 200
    
    return jsonify({"error": "Invalid file type, only PDF allowed."}), 400

@main.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(main.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('download_file', name=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

