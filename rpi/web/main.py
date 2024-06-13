import pandas
from flask import Flask, render_template, request
from fileinput import filename
 
# Flask constructor
app = Flask(__name__)
 
# Root endpoint
@app.get('/')
def upload():
    return render_template('upload-excel.html')
 
 
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
    app.run(debug=True)