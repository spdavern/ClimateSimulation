from flask import Flask, request, render_template, url_for, redirect
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import os
matplotlib.use('Agg')

app = Flask(__name__)
UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.get('/')
def upload():
    return render_template('main_page.html', file_uploaded=False)

@app.get('/example')
def example_page():
    return render_template('example_page.html')

# this is triggered when user clicks "View profile" button
@app.post('/upload')
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and file.filename.endswith('.xlsx'):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        plot_excel(filepath)
        #print('got here!')
        return render_template('main_page.html', file_uploaded=True)
    return 'Invalid file format. Please upload an Excel file (.xlsx).'


def plot_excel(filepath):
    
    # pull in excel file and plot it
    df = pd.read_excel(filepath)
    plt.figure(figsize=(10, 6))

    # convert first col to pd time
    df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], format='%H:%M:%S').dt.time
    
    # Prepare x and y data for plotting
    times = [t.strftime('%H:%M:%S') for t in df.iloc[:, 0]]
    values = df.iloc[:, 1]

    # plot cols
    plt.plot(times, values, marker='o')

    plt.xlabel('Time')
    plt.ylabel('Light Intensity Value')
    plt.title('Light Profile')
    
    # save plot to 'static' folder
    plot_path = os.path.join(app.config['UPLOAD_FOLDER'], 'plot.png')
    plt.savefig(plot_path)
    plt.close()

@app.get('/display_plot')
def display_plot():
    return redirect(url_for('static', filename='plot.png'))

# Custom error handler for 400 Bad Request
@app.errorhandler(400)
def bad_request(error):
    return 'Bad Request: Please check your request and try again.', 400




# Main Driver Function
if __name__ == '__main__':

    app.run(host="0.0.0.0", port=5000, debug=True)
