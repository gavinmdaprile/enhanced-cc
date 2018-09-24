#This view is actually pretty simple; it just returns a string, to be displayed on the client's web browser. The two route decorators above the function create the mappings from urls / and /index to this function.

from flask import render_template
from flask import request
from flask_audio.sound_id import labeled_audio
from flask_audio import app
import pandas as pd
import psycopg2
import subprocess

@app.route('/')

@app.route('/input')
def audio_input():
    return render_template("input.html")

@app.route('/output')
def audio_output():
    #pull the provided audio link from input field and store it
    audio_link = request.args.get('audio_link_name')
    videoID = audio_link[-11:]
    expected_mp3 = videoID + '.mp3'
    expected_wav = videoID + '.wav'
    expected_csv = videoID + '.csv'
    
    #download audio
    print(subprocess.check_output(["youtube-dl","--extract-audio", "--audio-format", "mp3", "--id", audio_link]))
    
    #convert to 16kHz wav
    print(subprocess.check_output(["ffmpeg","-i", expected_mp3, "-ar", "16000", expected_wav]))
    
    #run it through laughter detection
    prediction, labels, data = labeled_audio(expected_wav, expected_csv)
    

    return render_template("output.html", prediction = prediction, link = videoID, labels = labels, data = data)