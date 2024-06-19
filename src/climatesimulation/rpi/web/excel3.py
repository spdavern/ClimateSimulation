from flask import Flask, request, render_template_string, url_for
import pandas
import os

# run this using >> python3 <file>
# do not use >> flask --app <file> run as it doesn't run the if __name__ == '__main__' portion of the script 

app = Flask(__name__)

# HTML form as a string
main_page_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Upload/View Excel</title>
</head>
<body>
    <h1>Algae Pond Climate Simulator</h1>
    
    <h3>Instructions</h3>
    <p>1. Select 'Choose File' and select an Excel light profile (.xlsx).</p>
    <p>2. (optional) Click the 'View file' button to view its contents. Then come back to this page. </p>
    <p>3. Select 'Send to Pond' when ready!</p>
    
    <h3>Excel Format</h3>
    <p>- No headers!</p>
    <p>- Column 1: time (HH:MM:SS formatted as time in excel to the nearest second, can be at whatever time interval or not at intervals)</p>
    <p>- Column 2: light intensity (integer from 0 to 100, no percents!)</p>
    <p>note: The minimum light intensity to turn Vivosun on is ~18. To be safe, assume any value < 20 turns the Vivosun 'off'.</p>
    <button onclick="window.location.href='{{ url_for('example_page') }}'">See example</button>
    
    <h3>Actions</h3>
    <form action="{{ url_for('view') }}" method="post" enctype="multipart/form-data">
        <input type="file" name="file" accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel">
        <input type="submit" value="View file">
    </form>

</body>
</html>
"""

# HTML for the second page
example_page_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Example Excel Light Profile</title>
</head>
<body>

    <h3>An Example Excel Light Profile</h3>
    <p>The below light profile would run for twelve hours and has 1 minute time intervals. The 'times' are all relative, and the first time-value pair listed will be sent to the lights immediately!</p>
    <p> 00:00:00  |   25 </p>
    <p> 00:01:00  |   42.5 </p>
    <p> 00:02:00  |   99 </p>
    <p> ... </p>
    <p> 10:27:00  |   31 </p>
    <p> 10:28:00  |   0 </p>
    <p> ... </p>
    <p> 11:59:00  |   67 </p>
    <p> 12:00:00  |   55.1 </p>    

    <button onclick="window.location.href='{{ url_for('upload') }}'">Back to Main Page</button>
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
        # save file in local directory
        file.save(file.filename)
 
        # Parse the data as a Pandas DataFrame type
        data = pandas.read_excel(file.filename)
 
        # Return HTML snippet that will render the table
        return data.to_html()
    except Exception as e:
        return f"An error occurred: {e}"
 
@app.get('/example')
def example_page():
    return render_template_string(example_page_html)

# Main Driver Function
if __name__ == '__main__':
    # Run the application on the local development server
    app.run(host="0.0.0.0", port=5000, debug=True)
