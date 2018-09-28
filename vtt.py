#!/usr/bin/python
import sys
import re

#-------------------------------------------------------------------------------------------
# USAGE: python vtt.py confidenceLevel trainingData.csv outputFile.vtt inputFile.vtt
# all arguments required except inputfile.
# confidenceLevel: Setting between 0 and 1 that looks at the training data. 
# trainingData: CSV file showing the time in seconds and results for each sample.
#               the header row is required and will be used for the tag
# outputFile: Name of file to be created
# captionFile(optional): Provide the name of the caption file. If none is provided
#                        then only environmental sounds will be present in the captions.
#------------------------------------------------------------------------------------------

myDict = {}

def addToDict(k,v):
  if k in myDict:
    myDict[k].append(v)
  else:
    myDict[k] = [ v ]

def readVTT(filename):
  fh = open(filename, 'r')
  timestamp = ''
  for line in fh:
    if re.match(r'\d\d:\d\d:\d\d',line):
      timestamp = line
      continue
    else:
      if len(timestamp) > 0:
        addToDict(timestamp.rstrip(),line)
  fh.close()

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

def createVTT(out = './output.vtt'):
  fh = open(out,'w')
  fh.write('WEBVTT \n\n')
  for key in sorted(myDict):
    # convert second to time format
    fh.write(key)
    fh.write('\n')
    vals = myDict[key]
    fh.write(' '.join(map(str, vals)))
    fh.write('\n')
  fh.close

def parseFile(con,fn):
  fh = open(fn,'r')
  header = fh.readline().split(",")
  for line in fh:
    cols = line.split(",")
    t = cols[0].split("-")
    time = convertToTime(float(t[0]))
    for col in cols[1:-1]:
      if float(col) >= float(con):
        addToDict(time, '['+header[cols.index(col)]+']')
  fh.close()

def main(con,fn,out,vtt= ''):
  parseFile(con,fn)
  if len(vtt) > 0:
    readVTT(vtt)
  createVTT(out)
    


if __name__ == "__main__":
  con = sys.argv[1]
  fn = sys.argv[2]
  out = sys.argv[3]
  if len(sys.argv) > 4:
    vtt = sys.argv[4]
    main(con,fn,out,vtt)
  else: 
    main(con,fn,out)
  

