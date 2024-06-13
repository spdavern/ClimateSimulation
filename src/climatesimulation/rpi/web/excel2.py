import pandas
from flask import Flask, render_template, request
from fileinput import filename
 
# Flask constructor
app = Flask(__name__)
 
upload_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Upload/View Excel</title>
</head>
<body>
    <h1>Upload Excel File (.xlsx)</h1>
    <form action="{{ url_for('view') }}" method="post" enctype="multipart/form-data">
        <input type="file" name="file"
            accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel">
        <input type="submit" value="Upload">
    </form>
</body>
</html>
"""

# Root endpoint
@app.get('/')
def upload():
    return upload_html
 
 
@app.post('/view')
def view():
 
    # Read the File using Flask request
    file = request.files['file']
    # save file in local directory
    file.save(file.filename)
 
    # Parse the data as a Pandas DataFrame type
    data = pandas.read_excel(file)
 
    # Return HTML snippet that will render the table
    return data.to_html()
 
 
# Main Driver Function
if __name__ == '__main__':
    # Run the application on the local development server
    app.run(host='0.0.0.0', port=5000, debug=True)