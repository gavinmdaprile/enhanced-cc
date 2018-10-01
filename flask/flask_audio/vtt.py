#!/usr/bin/python
import sys
import re

def addToDict(k,v,dictionary):
    if k in dictionary:
        dictionary[k].append(v)
    else:
        dictionary[k] = [ v ]
    return dictionary
    

def readVTT(filename,dictionary):
    fh = open(filename, 'r')
    timestamp = ''
    for line in fh:
        if re.match(r'\d\d:\d\d:\d\d',line):
            timestamp = line
            continue
        else:
            if len(timestamp) > 0:
                dictionary = addToDict(timestamp.rstrip(),line, dictionary)
    fh.close()
    return dictionary

#converting into desired format for .vtt file
def convertToTime(sec):
    mm = int(sec) // 60
    hh = mm // 60
    mm = mm % 60
    ss = int(sec) % 60
    if sec == ss:
        mill = 0
    else:
        mill = str(sec - ss)

    start = "{0:0>2}".format(hh) + ":{0:0>2}".format(mm) + ":{0:0>2}".format(ss) + ".{0:0>3}".format(mill)
    ss += 2
    if ss > 59:
        mm = sec // 60
        hh = mm // 60
        mm = mm % 60
        ss = sec % 60
    end = "{0:0>2}".format(hh) + ":{0:0>2}".format(mm) + ":{0:0>2}".format(ss) + ".{0:0>3}".format(mill)
    return start + "-->" + end  

#final command to produce vtt file. called output.vtt if not specified otherwise
def createVTT(out,dictionary):
    fh = open(out,'w')
    fh.write('WEBVTT \n\n')
    for key in sorted(dictionary):
        # convert second to time format
        fh.write(key)
        fh.write('\n')
        vals = dictionary[key]
        fh.write(' '.join(map(str, vals)))
        fh.write('\n')
    fh.close
    
#final command to produce vtt format in returnable text
def returnVTT(txt, dictionary):
    txt.append('WEBVTT')
    for key in sorted(dictionary):
        # convert second to time format
        txt.append(key)
        vals = dictionary[key]
        txt.append(' '.join(map(str, vals)))
    return txt

#executed first, read fn (prediction file) and take in confidence intervals
#store for each time the prediction values in a dictionary
def parseFile(con,fn,dictionary):
    fh = open(fn,'r')
    header = fh.readline().split(",")
    for line in fh:
        cols = line.split(",")
        t = cols[0].split("-")
        time = convertToTime(float(t[0]))
        for col in cols[1:4]:
            if float(col) >= float(con):
                dictionary = addToDict(time, '['+header[cols.index(col)]+']',dictionary)
        for col in cols[6:7]:
            if float(col) >= float(con):
                dictionary = addToDict(time, '['+header[cols.index(col)]+']',dictionary)
        
    fh.close()
    return dictionary

