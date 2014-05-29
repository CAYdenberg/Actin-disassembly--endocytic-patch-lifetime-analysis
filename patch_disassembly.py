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

#Determine the longest sequence of positive values in a list
def StreakLength(data):
  CurrentStreak = {} #len, #start, #stop, #sum
  LongestStreak = {} #len, #start, #stop, #sum
  LongestStreak['len'] = 0
  #boolean Streaking represents whether we are in 
  Streaking = False
  RowNum = 0
  NumOfData = len(data)
  while RowNum < NumOfData:
    Val = data[RowNum]
    if not Streaking and Val > 0:
      #STARTING a streak
      Streaking = True
      CurrentStreak['start'] = RowNum
      CurrentStreak['sum'] = Val     
    elif Streaking and Val < 0:
      # ENDING a streak
      Streaking = False
      #RowNum - 1 is the last positive value in the streak
      CurrentStreak['end'] = RowNum - 1
      CurrentStreak['len'] = CurrentStreak['end'] - CurrentStreak['start'] + 1
      #check if this is now the longest streak
      if CurrentStreak['len'] > LongestStreak['len']:
        LongestStreak = CurrentStreak
      #reinstantiate CurrentStreak for the next loop
      CurrentStreak = {}
    elif Streaking:
      #CONTINUING THE CURRENT STREAK
      CurrentStreak['sum'] += data[RowNum]
    RowNum = RowNum + 1
  ReturnVal = {}
  ReturnVal['start'] = float(LongestStreak['start']) / 2
  ReturnVal['end'] = float(LongestStreak['end']) / 2
  ReturnVal['len'] = ReturnVal['end'] - ReturnVal['start']
  ReturnVal['sum'] = LongestStreak['sum']
  return ReturnVal
  
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

####
#The intensity score is defined as the
#difference between the sum of in the actin 
#and cofilin channels. (during the actin lifetime
#itself).
def GetIntensityScore(ActinTime, Int488, Int561):
  ActinStart = int(ActinTime['start'] * 2)
  ActinEnd = int(ActinTime['end'] * 2)
  CroppedInt488 = Int488[ActinStart : ActinEnd]
  CroppedInt561 = Int561[ActinStart : ActinEnd]
  SumInt488 = sum(CroppedInt488)
  SumInt561 = sum(CroppedInt561)
  return (SumInt488 - SumInt561) / len(CroppedInt488)
  

def ParseFile(Path):
  PathParts = Path.split('/')
  InFileName = PathParts[-1]
  FileParts = InFileName.split('.')
  Patch = FileParts[0] + '_' + PathParts[-2] 
  InFile = open(Path, 'r')
  print 'Processing: ' + Patch + '...'
  
  #instantiate what we need from the file
  RedFirst = False
  LineNum = 0
  raw488 = []
  raw561 = []
  back488 = []
  back561 = []
  act488 = []
  act561 = []
  
  #this represents the datapoint at which the 488 hits its peak
  peak488 = 0
  
  for Line in InFile:
    DataList = Line.split('\t')
    NumOfColumns = len(DataList)
    if LineNum == 1 and NumOfColumns >= 2:
      Col1 = ReadIn(DataList[1])
      #check the order in which the data are stored in the input file
      if Col1 == 'Red' or '561' in Col1:
        RedFirst = True
      elif Col1 == 'Green' or '488' in Col1:
        RedFirst = False
      else:
        print "Data structure not recognized!"
        return False   
    #get the raw data
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
        #check if Col2 is > than the current peak value,
        #if it is, then store it
        if Col2 > raw488[peak488]:
          peak488 = len(raw488) - 1          
      else:
        #adjust for bleedthru
        Col1 = Col1 - 154.24 - 0.2564 * Col2
        raw488.append(Col1)
        raw561.append(Col2)
        #check if Col1 is > than the current peak value,
        #if it is, then store it
        if Col1 > raw488[peak488]:
          peak488 = len(raw488) - 1 
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
  
  #Assign background values into arrays
  RowNum = 0
  while RowNum < NumOfData:
    back488.append( AvgMax488 - (Slope488 * RowNum) )
    back561.append( AvgMax561 - (Slope561 * RowNum) )
    RowNum = RowNum + 1  
  
  #Assign corrected (actual) values in arrays
  RowNum = 0
  MaxInt488 = raw488[peak488] - back488[peak488]
  while RowNum < NumOfData:
    CorrInt488 = ( raw488[RowNum] - back488[RowNum] ) / MaxInt488 * 600
    CorrInt561 = ( raw561[RowNum] - back561[RowNum] ) / MaxInt488 * 600
    act488.append( CorrInt488 )
    act561.append( CorrInt561 )
    RowNum += 1
  
  #determine length of coat and actin association
  ActinTime = StreakLength(act488)
  CofilinTime = StreakLength(act561)
  Delay = CofilinTime['start'] - ActinTime['start']
  
  IntensityScore = GetIntensityScore(ActinTime, act488, act561)
  
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
  
  #Make sure Cofilin intensity is high enough for the streak values to be reliable
  CofFilter = FilterChannel(act561)
  
  OutFile.write('Actin association begins: ' + str(ActinTime['start']) + '\n')
  OutFile.write('Actin association ends: ' + str(ActinTime['end']) + '\n')
  OutFile.write('Length of actin association: ' + str(ActinTime['len']) + '\n')
  OutFile.write('Area under actin curve during patch life: '+ str(ActinTime['sum']) + '\n')
  if CofFilter:
    OutFile.write('Cofilin association begins: ' + str(CofilinTime['start']) + '\n')
    OutFile.write('Cofilin association ends: ' + str(CofilinTime['end']) + '\n')
    OutFile.write('Length of cofilin association: ' + str(CofilinTime['len']) + '\n')
    OutFile.write('Delay between actin and cofilin association: ' + str(Delay) + '\n')
    OutFile.write('Area under cofilin curve during patch life: '+ str(CofilinTime['sum']) + '\n')
  OutFile.write('Cofilin intensity score: '+ str(IntensityScore))
  OutFile.close()
  
  MakeChart(Patch + '.svg', act488, act561)

  if CofFilter:
    SummaryFile.write(Patch + '\t' + str(ActinTime['len']) + '\t' + str(CofilinTime['len'])
    + '\t' + str(Delay) + '\t' + str(IntensityScore) + '\n')
  else:
    SummaryFile.write(Patch + '\t' + str(ActinTime['len']) + '\t\t\t' + str(IntensityScore) + '\n')
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
'Cumulative Intensity Ratio\n')

dirloop('raw/')

SummaryFile.close()