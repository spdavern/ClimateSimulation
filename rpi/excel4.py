# Flask app with updated /view endpoint
from flask import Flask, request, render_template_string, url_for
import pandas
import os

app = Flask(__name__)

# Path to the 'profile' folder
PROFILE_FOLDER = 'profile'

# HTML form as a string (main_page_html and example_page_html remain unchanged)
main_page_html = """
<!-- Updated main_page_html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Upload/View Excel</title>
</head>
<body>
    <h1>Algae Pond Climate Simulator</h1>
    
    <h3>Instructions</h3>
    <!-- Your existing instructions -->

    <h3>Actions</h3>
    <!-- Form with updated JavaScript function -->
    <form action="{{ url_for('view') }}" method="post" enctype="multipart/form-data" onsubmit="return checkUpload()">
        <input type="file" name="file" accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel">
        <input type="submit" value="View file">
    </form>

    <!-- JavaScript function to check if file is uploaded -->
    <script>
        function checkUpload() {
            var fileInput = document.querySelector('input[type="file"]');
            if (fileInput.files.length === 0) {
                alert('Please upload a file first.');
                return false;
            }
            return true;
        }
    </script>
</body>
</html>
"""



@app.get('/')
def upload():
    return render_template_string(main_page_html)
 
@app.post('/view')
def view():
    try:
        # Read the File using Flask request
        file = request.files['file']
        
        # Check if file is uploaded
        if file.filename == '':
            return "No file uploaded."
        
        # Save the file to 'profile' folder
        file_path = os.path.join(PROFILE_FOLDER, file.filename)
        file.save(file_path)
 
        # Parse the data as a Pandas DataFrame type (not necessary for saving to 'profile' folder)
        # data = pandas.read_excel(file_path)
 
        # Return HTML snippet or redirect as needed
        return f"File '{file.filename}' uploaded successfully to '{PROFILE_FOLDER}' folder."
    except Exception as e:
        return f"An error occurred: {e}"
 
@app.get('/example')
def example_page():
    return render_template_string(example_page_html)

# Main Driver Function
if __name__ == '__main__':
    # Ensure 'profile' folder exists
    if not os.path.exists(PROFILE_FOLDER):
        os.makedirs(PROFILE_FOLDER)
    
    # Run the application on the local development server
    app.run(host='0.0.0.0', port=5000, debug=True)
