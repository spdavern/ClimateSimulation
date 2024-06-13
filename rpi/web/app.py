import pandas
from flask import Flask, render_template, request


# Root endpoint
@app.get('/')
def upload():
    return render_template('upload-excel.html')