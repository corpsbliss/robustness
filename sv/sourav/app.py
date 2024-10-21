import os
import subprocess
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'log'}
COUNTER_FILE = 'counter.txt'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def read_counter():
    """Read the counter from the file."""
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, 'r') as f:
            return int(f.read().strip())
    return 0

def write_counter(count):
    """Write the counter to the file."""
    with open(COUNTER_FILE, 'w') as f:
        f.write(str(count))

@app.route('/')
def index():
    # Rendering the index page
    current_count = read_counter()
    return render_template('index.html', analysis_count=current_count)

@app.route('/upload', methods=['POST'])
def upload_file():
    # File upload route
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']

    # Check if the file is allowed (txt or log)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Get the selected script from form data
        selected_script = request.form.get('script')
        if not selected_script:
            return jsonify({'error': 'No script selected'}), 400
        
        # Construct the shell script path and run it
        script_path = os.path.join('scripts', selected_script)
        if not os.path.exists(script_path):
            return jsonify({'error': 'Script not found'}), 400

        try:
            # Execute the shell script with the uploaded file as an argument
            analysis_output = subprocess.check_output([script_path, file_path], stderr=subprocess.STDOUT)
            
            # Increment and save the counter
            current_count = read_counter()
            write_counter(current_count + 1)

            return jsonify({'result': analysis_output.decode('utf-8')})
        except subprocess.CalledProcessError as e:
            return jsonify({'error': e.output.decode('utf-8')}), 500

    return jsonify({'error': 'Invalid file type'}), 400

if __name__ == '__main__':
    app.run(debug=True)
