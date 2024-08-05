import os
import shutil
import time
from flask import Flask, request, render_template, url_for, redirect, send_file
from glob import glob
from typing import Optional
from werkzeug.utils import secure_filename
from climate_web_utilities import (
    plot_excel,
    check_profile_validity,
    ClimateConfig,
)

app = Flask(__name__)
UPLOAD_FOLDER: str = "static"
LIVE_FOLDER: str = "static/live"
ACTIVE_CONFIG: Optional[ClimateConfig] = None

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["LIVE_FOLDER"] = LIVE_FOLDER


# Main Page
@app.get("/")
def main_page():
    global ACTIVE_CONFIG, LIVE_FOLDER
    if not ACTIVE_CONFIG:
        if os.path.exists(os.path.join(LIVE_FOLDER, "climate_config.json")):
            ACTIVE_CONFIG = ClimateConfig()
    return render_template("main_page.html", file_uploaded=False)


# Example and Instructions Page
@app.get("/example")
def example_page():
    return render_template("example_page.html")


# Live Light Profile Page
@app.get("/live")
def live_light_profile():
    global ACTIVE_CONFIG, LIVE_FOLDER
    if ACTIVE_CONFIG:
        ACTIVE_CONFIG.update()
    else:
        if os.path.exists(os.path.join(LIVE_FOLDER, "climate_config.json")):
            ACTIVE_CONFIG = ClimateConfig()
            ACTIVE_CONFIG.update()
    return render_template("live_light_profile.html")


# Upload and Run Profile Page
@app.get("/run")
def run_light_profile():
    return render_template("run_light_profile.html")


# Light Profile Viewer Page
@app.get("/viewer")
def view_light_profile():
    return render_template("view_light_profile.html")


# this is triggered when user clicks "Choose File" button
@app.post("/viewer")
def view_profile():

    # check if file is real and in proper form
    if "file" not in request.files:
        return redirect(request.url)
    file = request.files["file"]
    if file.filename == "":
        return redirect(request.url)

    # save the file in 'static/'
    safe_fn = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], safe_fn)
    file.save(filepath)

    # check file format validity
    if check_profile_validity(filepath) == False:
        os.remove(filepath)  # delete the file if it's invalid
        return "Invalid file format. Please upload .xlsx or .csv file with 2 columns: Time and Light Intensity Value."

    # create a profile plot and save it
    plot_excel(filepath)

    # remove excel files to reduce clutter
    for filename in os.listdir(app.config["UPLOAD_FOLDER"]):
        if filename.endswith(".xlsx"):
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            os.remove(file_path)

    # all is well, return .html with the plot
    return render_template("view_light_profile.html", file_uploaded=True)


# this is triggered when user clicks "Send to Lights" button on the 'run' page
@app.post("/run")
def send_light_profile():
    global ACTIVE_CONFIG

    # check if file is real from the HTML request
    if "file" not in request.files:
        return redirect(request.url)

    file = request.files["file"]
    if file.filename == "":
        return redirect(request.url)
    # save the file in 'static/live'
    safe_fn = secure_filename(file.filename)
    filepath = os.path.join(app.config["LIVE_FOLDER"], safe_fn)
    if os.path.exists(filepath):
        if os.path.exists(os.path.join(LIVE_FOLDER, "replaced.xlsx")):
            os.remove(os.path.join(LIVE_FOLDER, "replaced.xlsx"))
        shutil.move(filepath, os.path.join(LIVE_FOLDER, "replaced.xlsx"))
    file.save(filepath)
    # check file format validity
    if check_profile_validity(filepath) == False:
        os.remove(filepath)  # delete the file if it's invalid
        if os.path.exists(os.path.join(LIVE_FOLDER, "replaced.xlsx")):
            shutil.move(os.path.join(LIVE_FOLDER, "replaced.xlsx"), filepath)
        return "Invalid file format. Please upload .xlsx or .csv file with 2 columns: Time and Light Intensity Value."

    # If there is an active config eliminate it.
    if ACTIVE_CONFIG:
        ACTIVE_CONFIG = None
        # Give the garbage collector a moment to do its thing.
        time.sleep(2)
    # delete any other plots or configs in the 'live' folder
    if os.path.exists(os.path.join(LIVE_FOLDER, "replaced.xlsx")):
        os.remove(os.path.join(LIVE_FOLDER, "replaced.xlsx"))
    for pathname in glob(os.path.join(app.config["LIVE_FOLDER"], "*.png")):
        os.remove(pathname)
    for pathname in glob(os.path.join(app.config["LIVE_FOLDER"], "*.json")):
        os.remove(pathname)

    ACTIVE_CONFIG = ClimateConfig(filepath)
    ACTIVE_CONFIG.update()

    # if no issues, then return the 'run' page with the file name
    # return render_template(
    #     "run_light_profile.html", sent_to_lights=os.path.basename(filepath)
    # )
    return render_template("live_light_profile.html")


# this is called by HTML after user clicks 'View Profile' button
# this grabs the plot.png that was created by upload_file() and displays it
@app.get("/display_plot")
def display_plot():
    return redirect(url_for("static", filename="plot.png"))


# Custom error handler for 400 Bad Request
@app.errorhandler(400)
def bad_request(error):
    return "Bad Request: Please check your request and try again.", 400


@app.get("/live/live_plot.png")  # this path doesn't do anything???
def display_live_plot():
    return redirect(
        url_for("static", filename="live/live_plot.png")
    )  # must use subfolder within 'static'


@app.route("/download")
def download():
    path = (
        "/home/pond/ClimateSimulation/rpi/default_profiles/light_profile_template.xlsx"
    )
    return send_file(path, as_attachment=True)


# Main Driver Function
if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000, debug=True)
