########################
#this function removes the stupid spaces
#added in text files by NIS Elements
#These spaces appear to be non-existant characters
#(charcode = 0) but since in practice they can only be letters or
#numbers we match them to a globally-defined pattern.
##########################
def ReadIn(Input):
  Output = ''
  for char in Input:
    if char and Pattern.match(char):
      Output = Output + char
  return Output

def StreakLength(data):
  #Determine the start and stop point of actin/cofilin association
  #This is defined (for now) as the longest sequence of positive
  #values in the relevent channel
  CurrentStreak = {} #len, #start, #stop
  LongestStreak = {}
  LongestStreak['len'] = 0
  Streaking = False
  RowNum = 0
  NumOfData = len(data)
  while RowNum < NumOfData:
    Val = data[RowNum]
    if not Streaking and Val > 0:
      Streaking = True
      CurrentStreak['start'] = RowNum
    elif Streaking and Val < 0:
      Streaking = False
      CurrentStreak['end'] = RowNum - 1
      CurrentStreak['len'] = CurrentStreak['end'] - CurrentStreak['start'] + 1
      if CurrentStreak['len'] > LongestStreak['len']:
        LongestStreak = CurrentStreak
      CurrentStreak = {}
    RowNum = RowNum + 1
  ReturnVal = {}
  ReturnVal['start'] = float(LongestStreak['start']) / 2
  ReturnVal['end'] = float(LongestStreak['end']) / 2
  ReturnVal['len'] = ReturnVal['end'] - ReturnVal['start']
  return ReturnVal

def MaximumIntensity(Channel, Time):
  Start = int(Time['start'] * 2)
  End = int(Time['end'] * 2)
  Streak = Channel[Start:End]
  NumOfData = len(Streak)
  DataPoint = 0
  Max = 0
  while DataPoint < NumOfData:
    if Streak[DataPoint] > Max:
      Max = Streak[DataPoint]
    DataPoint = DataPoint + 1
  return Max
  
def MakeChart(FileName, GreenSeries, RedSeries):
  DataPoint = 0
  NumOfData = len(GreenSeries)
  GreenPairs = []
  RedPairs = []
  while DataPoint < NumOfData:  
    GreenPt = DataPoint, GreenSeries[DataPoint]
    RedPt = DataPoint, RedSeries[DataPoint]
    GreenPairs.append(GreenPt)
    RedPairs.append(RedPt)
    DataPoint = DataPoint + 1
  chart = Line( 800, 600, 
    [
        GreenPairs, 
        RedPairs
    ],
    'css/linechart.css',
    label_intervals = 10,
    x_padding = 40,
    units = True,
    currency = False     
  )
  chart.output('svg/' + FileName)
  
def FilterChannel(Data):
  Min = min(Data)
  Max = max(Data)
  if Max > Min * -3:
    return True
  else:
    return False      

def ParseFile(Path):
  PathParts = Path.split('/')
  InFileName = PathParts[-1]
  FileParts = InFileName.split('.')
  Patch = FileParts[0] + '_' + PathParts[-2] 
  InFile = open(Path, 'r')
  print 'Processing: ' + Patch + '...'
  
  RedFirst = False
  LineNum = 0
  raw488 = []
  raw561 = []
  back488 = []
  back561 = []
  act488 = []
  act561 = []
  
  for Line in InFile:
    DataList = Line.split('\t')
    NumOfColumns = len(DataList)
    if LineNum == 1 and NumOfColumns >= 2:
      Col1 = ReadIn(DataList[1])
      if Col1 == 'Red' or '561' in Col1:
        RedFirst = True
      elif Col1 == 'Green' or '488' in Col1:
        RedFirst = False
      else:
        print "Data structure not recognized!"
        return False   
    elif LineNum > 1 and NumOfColumns >= 3:    
      Col1 = ReadIn(DataList[1])
      Col2 = ReadIn(DataList[2])
      Col1 = float(Col1)
      Col2 = float(Col2)
      if RedFirst:
        #adjust for bleedthru
        Col2 = Col2 - 154.24 - 0.2564 * Col1
        raw561.append(Col1)
        raw488.append(Col2)
      else:
        #adjust for bleedthru
        Col1 = Col1 - 154.24 - 0.2564 * Col2
        raw488.append(Col1)
        raw561.append(Col2)
    LineNum = LineNum + 1
  InFile.close()
  
  NumOfData = len(raw488)
  
  RowNum = 0
  
  #calculate background
  SumMax488 = 0
  SumMin488 = 0
  SumMax561 = 0
  SumMin561 = 0
  #Calculate the initial background by averaging the 1st 5 datapoints
  while RowNum < 5:
    SumMax488 = SumMax488 + raw488[RowNum]
    SumMax561 = SumMax561 + raw561[RowNum]
    RowNum = RowNum + 1
  AvgMax488 = SumMax488 / 5
  AvgMax561 = SumMax561 / 5
  #Calculate the final background by averaging the last 5 data points
  RowNum = NumOfData - 5
  while RowNum < NumOfData:
    SumMin488 = SumMin488 + raw488[RowNum]
    SumMin561 = SumMin561 + raw561[RowNum]
    RowNum = RowNum + 1
  AvgMin488 = SumMin488 / 5
  AvgMin561 = SumMin561 / 5
  #The background is assumed to change linearly over time as photobleaching
  #occurs. Calculate the slope of this line.
  Slope488 = (AvgMax488 - AvgMin488) / NumOfData
  Slope561 = (AvgMax561 - AvgMin561) / NumOfData
  
  #Assign background and corrected values into arrays
  RowNum = 0
  while RowNum < NumOfData:
    back488.append( AvgMax488 - (Slope488 * RowNum) )
    act488.append( raw488[RowNum] - back488[RowNum] )
    back561.append( AvgMax561 - (Slope561 * RowNum) )
    act561.append( raw561[RowNum] - back561[RowNum] )
    RowNum = RowNum + 1  
  
  #determine length of coat and actin association
  ActinTime = StreakLength(act488)
  CofilinTime = StreakLength(act561)
  Delay = CofilinTime['start'] - ActinTime['start']
  
  #Calculate maximum channel intensities (within the streak)
  #for each channel
  CofMaxInt = MaximumIntensity(act561, CofilinTime)
  ActMaxInt = MaximumIntensity(act488, ActinTime)
  
  OutFile = open('processed/' + Patch + '.txt', 'w')
  
  OutFile.write('Time\t Int488\t Int561\t Back488\t Back561\t Raw488\t Raw561\n')
  
  RowNum = 0
  
  while RowNum < NumOfData:
    Time_f = float(RowNum) / 2
    Time = str(Time_f)
    Int488 = str(act488[RowNum])
    Int561 = str(act561[RowNum])
    Back488 = str(back488[RowNum])
    Back561 = str(back561[RowNum])
    Raw488 = str(raw488[RowNum])
    Raw561 = str(raw561[RowNum])
    OutputStr = Time + '\t ' + Int488 + '\t ' + Int561 + '\t ' + Back488 + '\t ' + Back561 + '\t' + Raw488 + '\t ' + Raw561
    OutFile.write(OutputStr + '\n')
    RowNum = RowNum + 1
  
  OutFile.write('Actin association begins: ' + str(ActinTime['start']) + '\n')
  OutFile.write('Actin association ends: ' + str(ActinTime['end']) + '\n')
  OutFile.write('Length of actin association: ' + str(ActinTime['len']) + '\n')
  OutFile.write('Cofilin association begins: ' + str(CofilinTime['start']) + '\n')
  OutFile.write('Cofilin association ends: ' + str(CofilinTime['end']) + '\n')
  OutFile.write('Length of cofilin association: ' + str(CofilinTime['len']) + '\n')
  OutFile.write('Delay between actin and cofilin association: ' + str(Delay) + '\n')
  OutFile.write('Maximum normalized actin intensity: ' + str(ActMaxInt) + '\n')
  OutFile.write('Maximum normalized cofilin intensity: ' + str(CofMaxInt))
  OutFile.close()
  
  MakeChart(Patch + '.svg', act488, act561)
  
  #Make sure Cofilin intensity is high enough for the streak values to be reliable
  CofFilter = FilterChannel(act561)

  if CofFilter:
    SummaryFile.write(Patch + '\t' + str(ActinTime['len']) + '\t' + str(CofilinTime['len'])
    + '\t' + str(Delay) + '\t' + str(ActMaxInt) + '\t' + str(CofMaxInt) + '\n')
  else:
     SummaryFile.write(Patch + '\t' + str(ActinTime['len']) + '\t\t\t' + str(ActMaxInt) 
     + '\t' + str(CofMaxInt) + '\n')
  return True

def dirloop(Dir):
  Files = os.listdir(Dir)
  for File in Files:
    if os.path.isfile(Dir + File):
      ParseFile(Dir + File)
    else:
      SubDir = Dir + File + '/'
      print SubDir
      SubFiles = os.listdir(SubDir)
      for SubFile in SubFiles:
        ParseFile(SubDir + SubFile)

#main script
import re
import os
from charty import Line  

#Pattern (global) is the char allowed from input files
Pattern = re.compile(r'[A-Za-z0-9.,]')  

SummaryFile = open('process_patch.txt', 'w')
SummaryFile.write('Patch name \tActin Time \tCofilin Time \tDelay \t' +
'Actin Maximum Intensity \tCofilin Maximum Intensity\n')

dirloop('raw/')

SummaryFile.close()