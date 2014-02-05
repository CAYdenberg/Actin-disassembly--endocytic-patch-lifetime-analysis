def WriteToFile(Series, Headings, OutFileName):
  NumOfColumns = len(Headings)
  NumOfRows = 0
  #determine the number of rows we need to output
  for Heading in Headings:
    Len = len(Series[Heading])
    if Len > NumOfRows:
      NumOfRows = Len
  OutFile = open(OutFileName, 'w')
  Col = 0
  Row = 0
  Line = ""
  while Col < NumOfColumns:
    Line = Line + Headings[Col] + "\t"
    Col = Col + 1
  OutFile.write(Line + '\n')
  while Row <= NumOfRows:
    Col = 0
    Line = ""
    while Col < NumOfColumns:
      Heading = Headings[Col]
      Data = Series[Heading]
      try:
        DataPoint = float(Data[Row])
      except:
        DataPoint = ""
      Line = Line + str(DataPoint) + "\t"
      Col = Col + 1
    OutFile.write(Line + "\n")
    Row = Row + 1 
  OutFile.close()  

def Average(ListOfNumbers):
  if len(ListOfNumbers) == 0:
    raise Exception('Cannot calculate average of empty list')
  Avg = sum(ListOfNumbers) / len(ListOfNumbers)
  return Avg

def StandardDeviation(ListOfNumbers):
  if len(ListOfNumbers) < 2:
    raise Exception('Standard deviation requires at least two values')
  Avg = Average(ListOfNumbers)
  SumOfSquares = 0
  for x in range(0, len(ListOfNumbers)):
    SumOfSquares += (ListOfNumbers[x] - Avg) ** 2
  SD = (SumOfSquares / (len(ListOfNumbers) - 1)) ** 0.5
  return SD

class Strain(object):
  def __init__(self, StrainName):
    self.name = StrainName
    self.files = []
    self.times = []
    self.corr488avg = []
    self.corr561avg = []
    self.corr488sem = []
    self.corr561sem = []
  def addFile(self, FileName):
    File = FileData(FileName)
    self.files.append(File)
  def doStats(self):
    NumDataPoints = 0
    for File in self.files:  
      if len(File.times) > NumDataPoints:
        NumDataPoints = len(File.times)
    for x in range(0, NumDataPoints):
      #change to -2 to align at end
      self.times.append(float(x) / -2)
      Data488 = []
      Data561 = []
      for File in self.files:
        try:
          #change to [-x] to align at end
          Data488.append(File.corr488[-x])
        except:
          continue
        if File.containsCofData == True:
          #change to [-x] to align at end
          Data561.append(File.corr561[-x])
      if len(Data488) > 2:
        self.corr488avg.append(Average(Data488))
        self.corr488sem.append(StandardDeviation(Data488)/ math.sqrt(len(Data488)))
        if len(Data561) > 2:
          self.corr561avg.append(Average(Data561))
          self.corr561sem.append(StandardDeviation(Data561)/ math.sqrt(len(Data561)))
        else:
          self.corr561avg.append(None)
          self.corr561sem.append(None)
      else:
        continue
  def write(self):
    Headings = ['x', 'actin', 'actin sem', 'cofilin', 'cofilin sem']
    Output = {'x' : self.times}
    Output['actin'] = self.corr488avg
    Output['actin sem'] = self.corr488sem
    Output['cofilin'] = self.corr561avg
    Output['cofilin sem'] = self.corr561sem
    WriteToFile(Output, Headings, 'aligned_at_end/' + self.name + '.txt')     
      


class FileData(object):
  def __init__(self, FileName):
    #the entire timecourse of x data points
    Times = []
    #the cropped timeseries
    self.times = []
    #all the actin data
    Corr488 = []
    #cropped actin data
    self.corr488 = []
    #all the cofilin data
    Corr561 = []
    #cropped (final) cofilin data
    self.corr561 = []
    #if the patch disassembly script decided the Cof1 data was worth looking at
    self.containsCofData = False
    InFile = open('processed/' + FileName, 'r')
    LineNum = 0
    Begin = 0
    End = 0
    for Line in InFile:
      DataList = Line.split('\t')
      if LineNum > 0 and ':' not in Line:
        Times.append(float(DataList[0]))
        Corr488.append(float(DataList[1]))
        Corr561.append(float(DataList[2]))
      elif LineNum > 0:
        DataList = Line.split(':')
        Key = DataList[0]
        Value = float(DataList[1])
        if Key == "Actin association begins":
          Begin = int(Value * 2)
        elif Key == "Actin association ends":
          End = int(Value * 2)
        elif Key == "Cofilin association begins":
          self.containsCofData = True
      LineNum += 1  
    self.corr488 = Corr488[Begin:End]
    self.corr561 = Corr561[Begin:End]
    self.times = Times[Begin:End]
    InFile.close()      

import re
import os
import math

Files = os.listdir('processed/')

StrainsDict = {}

for File in Files:
  DataList = File.split('_')
  StrainName = DataList[0]
  #filter out the CY4 control, which has no 488 signal
  if StrainName == 'CY4':
    continue
  if not StrainName in StrainsDict:
    #create a new strain object
    StrainsDict[StrainName] = Strain(StrainName)  
  StrainsDict[StrainName].addFile(File)


for StrainName in StrainsDict:
  StrainsDict[StrainName].doStats()
  StrainsDict[StrainName].write()  