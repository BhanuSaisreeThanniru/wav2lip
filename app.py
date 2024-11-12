from flask import Flask, request, redirect, url_for, render_template, flash
import os
import tempfile
import subprocess
import logging
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder='front_end')

# Configure logging
logging.basicConfig(level=logging.INFO)

# Allowed file extensions
ALLOWED_AUDIO_VIDEO_EXTENSIONS = {'mp3', 'mp4', 'wav'}

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@app.route('/', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        # Check if the post request has the files
        if 'file1' not in request.files or 'file2' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file1 = request.files['file1']  # Audio/Video file
        file2 = request.files['file2']  # Text file

        # Validate the files
        if not (file1 and allowed_file(file1.filename, ALLOWED_AUDIO_VIDEO_EXTENSIONS)):
            flash('File 1 must be an audio/video file (mp3, mp4, wav).')
            return redirect(request.url)
        if not (file2 and allowed_file(file2.filename, ALLOWED_AUDIO_VIDEO_EXTENSIONS)):
            flash('File 2 must be an audio/video file (mp3, mp4, wav).')
            return redirect(request.url)

        # Create a temporary directory
        with tempfile.TemporaryDirectory() as tempdir:
            # Secure filenames and save them
            file1_path = os.path.join(tempdir, secure_filename(file1.filename))
            file2_path = os.path.join(tempdir, secure_filename(file2.filename))
            file1.save(file1_path)
            file2.save(file2_path)

            # Path for the checkpoint file
            checkpoint_path = "checkpoints/wav2lip_gan.pth"

            # Run the inference script with the file paths as arguments
            try:
                result = subprocess.run(
                    ['python', 'inference.py', '--checkpoint_path', checkpoint_path, '--face', file1_path, '--audio', file2_path],
                    capture_output=True, text=True
                )
                output = result.stdout or result.stderr
                return f"Output: {output}"
            except Exception as e:
                logging.error(f"Error running inference script: {e}")
                return "An error occurred while processing the files."

    return render_template('file_upload.html')

if __name__ == '__main__':
    app.run(debug=False)  # Set to False in production
