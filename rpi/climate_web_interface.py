from flask import Flask, request, render_template, url_for, redirect
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import os
matplotlib.use('Agg')

app = Flask(__name__)
UPLOAD_FOLDER = 'rpi/static'
LIVE_FOLDER = 'rpi/static/live'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['LIVE_FOLDER'] = LIVE_FOLDER


# Main Page
@app.get('/')
def main_page():
    return render_template('main_page.html', file_uploaded=False)


# Example and Instructions Page
@app.get('/example')
def example_page():
    return render_template('example_page.html')


# Live Light Profile Page
@app.get('/live')
def live_light_profile():
    return render_template('live_light_profile.html')


# Upload and Run Profile Page
@app.get('/run')
def run_light_profile():
    return render_template('run_light_profile.html')


# Light Profile Viewer Page
@app.get('/viewer')
def view_light_profile():
    return render_template('view_light_profile.html')


# this is triggered when user clicks "Choose File" button
@app.post('/viewer')
def view_profile():

    # check if file is real and in proper form
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    
    # save the file in 'static/'
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    # check file format validity 
    if check_profile_validity(filepath) == False:
        os.unlink(filepath) # delete the file if it's invalid
        return 'Invalid file format. Please upload .xlsx or .csv file with 2 columns: Time and Light Intensity Value.'


    # create a profile plot and save it
    plot_excel(filepath)

    # remove excel files to reduce clutter
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if filename.endswith('.xlsx'):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.unlink(file_path)


    # all is well, return .html with the plot
    return render_template('view_light_profile.html', file_uploaded=True)


# this is triggered when user clicks "Send to Lights" button on the 'run' page
@app.post('/run')
def send_light_profile():

    # check if file is real from the HTML request
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    
    # delete everything in the 'live' folder (commented out until actual operation)
    #for filename in os.listdir(app.config['LIVE_FOLDER']):
    #    file_path = os.path.join(app.config['LIVE_FOLDER'], filename)
    #    try:
    #        if os.path.isfile(file_path):
    #            os.unlink(file_path)
    #    except Exception as e:
    #        print(e)

    # save the file in 'static/live'
    filepath = os.path.join(app.config['LIVE_FOLDER'], file.filename)
    file.save(filepath)

    # check file format validity 
    if check_profile_validity(filepath) == False:
        os.unlink(filepath) # delete the file if it's invalid
        return 'Invalid file format. Please upload .xlsx or .csv file with 2 columns: Time and Light Intensity Value.'


    # if no issues, then return the 'run' page with the file name
    return render_template('run_light_profile.html', sent_to_lights=os.path.basename(filepath))
    


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
    plt.title(str(os.path.basename(filepath)))

    # xaxis labels - reduce clutter
    if len(times) > 50:
        plt.xticks(times[::10], rotation=45)
    else:
        plt.xticks(times, rotation=45)

    # save plot to 'static' folder
    plot_path = os.path.join(app.config['UPLOAD_FOLDER'], 'plot.png')
    plt.savefig(plot_path)
    plt.close()


# this is called by HTML after user clicks 'View Profile' button
# this grabs the plot.png that was created by upload_file() and displays it
@app.get('/display_plot')
def display_plot():
    return redirect(url_for('static', filename='plot.png'))


# Custom error handler for 400 Bad Request
@app.errorhandler(400)
def bad_request(error):
    return 'Bad Request: Please check your request and try again.', 400


@app.get('/live/live_plot.png') # this path doesn't do anything???
def display_live_plot(): 
    return redirect(url_for('static', filename='live/live_plot.png')) # must use subfolder within 'static'


def check_profile_validity(filepath):
    
    # 1. check if excel file or csv file
    if filepath.endswith('.xlsx'):
        df = pd.read_excel(filepath)

    elif filepath.endswith('.csv'):
        df = pd.read_csv(filepath)

    else:
        return False

    # 2. check if file has 2 columns
    if len(df.columns) != 2:
        return False
    
    # 3. check if first column is time
    try:     
        # convert first col to pd time
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], format='%H:%M:%S').dt.time
    except:
        return False
    
    # if passed all the tests, return True!
    return True




# Main Driver Function
if __name__ == '__main__':

    app.run(host="0.0.0.0", port=5000, debug=True)
