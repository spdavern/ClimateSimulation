import matplotlib
import matplotlib.pyplot as plt
import os
import pandas as pd
from datetime import time

matplotlib.use('Agg')

def expand_profile_points(df: pd.DataFrame) -> pd.DataFrame:
    """Pads a dataframe of duration, intensity values to capture step nature of profiles.

    Arguments:
        df(DataFrame): Dataframe with first column of times in "23:59:59" format and
            second column of light intensity values.

    Returns (DataFrame):
        Dataframe with extra rows facilitating the plotting of light intensity setting
        steps where the source dataframe specifies only the time and intensity values
        at the steps.
    """
    df2 = pd.DataFrame(columns=df.columns)
    idx2 = 0
    zero = time().fromisoformat("00:00:00")
    time_col = df.columns[0]
    intensity_col = df.columns[1]
    for idx, row in df.iterrows():
        duration = row[time_col]
        if idx == 1:
            # If the first row isn't duration = zero create one.
            if duration == zero:
                row.name = 0
                df2 = df2._append(row)
                last_row = row
            else:
                # Otherwise use the initial row.
                first_row = row.copy()
                first_row.name = 0
                first_row[time_col] = zero
                first_row[intensity_col] = 0
                df2 = df2._append(first_row)
                last_row = first_row
            idx2 += 1
        if duration == zero:
            # Skip any duplicate duration = zero rows in profile
            continue
        # Add a row that has time minus 1 sec from the next row and intensity from the last row.
        new_row = last_row.copy()
        hour = duration.hour - 1 if duration.second == 0 and duration.minute == 0 else duration.hour
        minute = duration.minute - 1 if duration.second == 0 else duration.minute
        minute = 59 if minute < 0 else minute
        second = 59 if duration.second == 0 else duration.second - 1
        new_row[time_col] = time().fromisoformat(f"{hour:02}:{minute:02}:{second:02}")
        new_row.name = idx2
        df2 = df2._append(new_row)
        idx2 += 1
        # Finally append the next row
        row.name = idx2
        df2 = df2._append(row)
        last_row = row.copy()
        idx2 += 1
    # If the last row isn't at time 23:59:59 add that point.
    if duration != time().fromisoformat("23:59:59"):
        last_row[time_col] = time().fromisoformat("23:59:59")
        last_row.name = idx2
        df2 = df2._append(last_row)
    return df2

def plot_excel(filepath):
    
    # pull in excel file and plot it
    df = pd.read_excel(filepath)
    df = expand_profile_points(df)
    plt.figure(figsize=(10, 6))

    # Prepare x and y data for plotting
    times = [dt.hour + dt.minute/60 + dt.second/60/60 for dt in df[df.columns[0]]]
    values = df.iloc[:, 1]

    # plot cols
    plt.plot(times, values, marker='.')
    plt.grid('both')
    plt.xlabel('Duration from Start of Profile (hours)')
    plt.ylabel('Light Intensity Value')
    plt.title(str(os.path.basename(filepath)))

    # xaxis labels - reduce clutter
    if len(times) > 50:
        plt.xticks(times[::10], rotation=45)
    else:
        plt.xticks(times, rotation=45)

    # save plot to 'static' folder
    plot_path = os.path.join(os.path.dirname(filepath), 'plot.png')
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


