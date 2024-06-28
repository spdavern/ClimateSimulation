import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

# pull in excel file and plot it
df = pd.read_excel("rpi/day3.xlsx")
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

plt.gcf().autofmt_xdate()

third_row_time = times[2]  # Get the time value at the third row
plt.axvline(x=third_row_time, color='r', linestyle='--', label='now')
plt.xticks(times[::10], rotation=45)
           
plt.savefig("this.png")
#plt.close()
plt.show()