#This view is actually pretty simple; it just returns a string, to be displayed on the client's web browser. The two route decorators above the function create the mappings from urls / and /index to this function.

from flask import render_template
from flask import request
from flask_audio.sound_id import labeled_audio
from flask_audio import app
import pandas as pd
import psycopg2
import subprocess
import sys
import re
from flask_audio.vtt import parseFile, createVTT, convertToTime, readVTT, addToDict, returnVTT
import os

@app.route('/')

@app.route('/input')
def audio_input():
    return render_template("input.html")
    
@app.route('/about')
def about_input():
    return render_template("about.html")


@app.route('/output')
def audio_output():
    #pull the provided audio link from input field and store it
    audio_link = request.args.get('audio_link_name')
    videoID = audio_link[-11:]
    expected_mp3 = videoID + '.mp3'
    moved_mp3 = "flask_audio/files/" + videoID + '.mp3'
    expected_wav = "flask_audio/files/" + videoID + '.wav'
    expected_csv = "flask_audio/files/" + videoID + '.csv'
    expected_cap = "flask_audio/files/" + videoID + '.en.vtt'
    final_cap_file_csv = "flask_audio/files/" + videoID + '_cap_f.vtt' #works with csv
    
    con = .8
    myDict = {}
    
    #data download and transfer
    #attempt to download captions
    print(subprocess.check_output(["youtube-dl-2018","--skip-download","--write-sub","--no-playlist",audio_link,"-o","flask_audio/files/%(id)s.%(ext)s"]))
    #download audio
    print(subprocess.check_output(["youtube-dl-2016","--extract-audio", "--audio-format", "mp3", "--id", audio_link]))
    #move mp3 file
    print(subprocess.check_output(["mv", expected_mp3, moved_mp3]))
    
    #convert to 16kHz wav
    print(subprocess.check_output(["ffmpeg", "-y", "-i", moved_mp3, "-ar", "16000", expected_wav]))
    
    #run it through laughter detection
    labeled_audio(expected_wav, expected_csv)
    
    #make caption file if need be
    myDict = parseFile(con,expected_csv, myDict)
    
    #have text from vtt for printing to output
    vttfile_newonly = [];
    vttfile_newonly = returnVTT(vttfile_newonly, myDict)
    
    #checking if vtt file is there
    exists = os.path.isfile(expected_cap)
    vttfile_total = [];
    
    if exists:
        myDict = readVTT(expected_cap, myDict)
        vttfile_total = returnVTT(vttfile_total, myDict)
        createVTT(final_cap_file_csv, myDict)
    else: # make a new VTT file
        createVTT(final_cap_file_csv, myDict)
    
    
    #adding in some logic if the file is empty
    if len(vttfile_newonly) == 1 and not exists: #no new sounds identified
        toptext = "Sorry, no sounds were identified, and no existing caption file was detected. Please try another video!"
        midtext = ""
        vttfile_newonly = []
    elif len(vttfile_newonly) > 1 and not exists:
        toptext = "Non-speech sounds identified:"
        midtext = ""
    elif len(vttfile_newonly) > 1 and exists:
        toptext = "Non-speech sounds identified:"
        midtext = "Existing captions with new captions inserted:"        
    elif len(vttfile_newonly) == 1 and exists:
        toptext = "Sorry, no sounds were identified. Please try another video!"
        midtext = ""
        vttfile_total = []
        vttfile_newonly = []
              
        
    return render_template("output.html", video_link = audio_link, vttfile_newonly = vttfile_newonly, vttfile_total = vttfile_total, toptext = toptext, midtext = midtext)
    
    
    
    
