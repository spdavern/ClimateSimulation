import matplotlib
import matplotlib.pyplot as plt
import os
import pandas as pd

matplotlib.use('Agg')

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


