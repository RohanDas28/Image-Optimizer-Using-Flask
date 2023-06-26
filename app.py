import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from PIL import Image

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['COMPRESSED_FOLDER'] = 'compressed'

def create_directories():
    """Create the 'uploads' and 'compressed' directories if they don't exist"""
    for folder in [app.config['UPLOAD_FOLDER'], app.config['COMPRESSED_FOLDER']]:
        if not os.path.exists(folder):
            os.makedirs(folder)

def format_filesize(filesize):
    """Format the file size in a human-readable format (KB or MB)"""
    KB = 1024
    MB = KB * 1024

    if filesize >= MB:
        return f"{filesize / MB:.2f} MB"
    elif filesize >= KB:
        return f"{filesize / KB:.2f} KB"
    else:
        return f"{filesize} bytes"

@app.route('/')
def index():
    """Render the index.html template"""
    return render_template('index.html')

@app.route('/compress', methods=['POST'])
def compress():
    """Handle the image compression"""
    create_directories()

    if 'image' not in request.files:
        return redirect(url_for('index'))

    file = request.files['image']
    if file.filename == '':
        return redirect(url_for('index'))

    filename = file.filename
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    output_path = os.path.join(app.config['COMPRESSED_FOLDER'], os.path.splitext(filename)[0] + '.webp')

    file.save(input_path)

    original_filesize = os.path.getsize(input_path)
    
    if file.filename.lower().endswith((".png", ".jpg", ".jpeg", "jfif", ".bmp", ".tiff", ".tif")):
        Image.open(input_path).save(output_path, 'webp')
        compressed_filesize = os.path.getsize(output_path)

        original_filesize = format_filesize(original_filesize)
        compressed_filesize = format_filesize(compressed_filesize)

        return render_template('success.html', original_filename=filename, compressed_filename=os.path.basename(output_path), original_filesize=original_filesize, compressed_filesize=compressed_filesize)
    else:
        return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve the uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/compressed/<filename>')
def compressed_file(filename):
    """Serve the compressed files"""
    return send_from_directory(app.config['COMPRESSED_FOLDER'], filename)

@app.route('/download/<filename>')
def download_compressed(filename):
    """Download the compressed file"""
    return send_from_directory(app.config['COMPRESSED_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run()
