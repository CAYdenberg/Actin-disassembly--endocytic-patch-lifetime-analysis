def WriteToFile(Series, Headings, OutFileName):

  NumOfColumns = len(Headings)

  NumOfRows = 0

  #determine the number of rows we need to output

  for Heading in Headings:

    Len = len(Series[Heading])

    if Len > NumOfRows:

      NumOfRows = Len

  print NumOfRows

  OutFile = open(OutFileName, 'w')

  Col = 0

  Row = 0

  Line = ""

  while Col < NumOfColumns:

    Line = Line + Headings[Col] + "\t"

    Col = Col + 1

  print Line

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

    print Line

    OutFile.write(Line + "\n")

    Row = Row + 1 

  OutFile.close()



def Parse(FileName):

  

  #get global variable NumBins

  global NumBins

  

  InFile = open('processed/' + FileName)

  Time = []

  Int488 = []

  Int561 = []

  StartActin = 0

  EndActin = 0

  Max488 = 0

  Max561 = 0

  

  LineNum = -1

  

  for Line in InFile:

    LineNum += 1

    #get data from the input file

    CofilinFiltered = True

    if ':' in Line:

      DataList = Line.split(':')

      if 'Actin association begins' in Line:      

        StartActin = float(DataList[1])

      elif 'Actin association ends' in Line:

        EndActin = float(DataList[1])

      elif 'Cofilin' in Line:

        CofilinFiltered = False

      else:

        continue

    elif LineNum > 0:

      DataList = Line.split('\t')

      Time.append(float(DataList[0]))

      Int488.append(float(DataList[1]))

      Int561.append(float(DataList[2]))

    else:

      continue

      

  InFile.close()

  

  NumData = len(Time)

  

  DataNum = -1

  

  TotalTime = EndActin - StartActin

  

  CroppedTimes = []

  

  CroppedInt488 = []

  

  CroppedInt561 = []

  

  while DataNum < NumData:

    DataNum += 1

    CurrTime = Time[DataNum]

    if CurrTime < StartActin:

      continue

    if CurrTime > EndActin:

      break

    FractionTime = (CurrTime - StartActin) / TotalTime

    Bin = int( math.floor(FractionTime*NumBins) )

    CroppedTimes.append(Bin)

    CroppedInt488.append(Int488[DataNum])

    CroppedInt561.append(Int561[DataNum])

  

  DataNum = 0

  

  BinAvg488 = []

  

  BinAvg561 = []

  

  for x in range(0, NumBins):

    NumInBin = 0

    BinTotal488 = 0

    BinTotal561 = 0

    while CroppedTimes[DataNum] == x:

      BinTotal488 += CroppedInt488[DataNum]

      BinTotal561 += CroppedInt561[DataNum]

      NumInBin += 1

      DataNum += 1

    #if the bin is empty (possible for a few profiles),

    #go onto the next bin

    if NumInBin == 0:

      BinAvg488.append(None)

      BinAvg561.append(None)

      continue

    Avg488 = BinTotal488/NumInBin

    Avg561 = BinTotal561/NumInBin

    BinAvg488.append(Avg488)

    BinAvg561.append(Avg561)

  

  if CofilinFiltered:

    return {'Avg488': BinAvg488}

  else:

    return {'Avg488' : BinAvg488, 'Avg561' : BinAvg561}  



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



class Strain:

  def __init__(self, StrainName):

    global NumBins

    self.name = ''

    self.files = []

    self.binned488 = []

    self.binned561 = []

    self.avg488 = [None] * NumBins

    self.avg561 = [None] * NumBins

    self.sem488 = [None] * NumBins

    self.sem561 = [None] * NumBins

  

  def addFile(self, FileName):

    self.files.append(FileName)

    DataHandle = Parse(FileName)

    self.binned488.append(DataHandle['Avg488'])

    if 'Avg561' in DataHandle:

      self.binned561.append(DataHandle['Avg561'])

  

  def doStats(self):

    #get global variables

    global NumBins

    NumFiles = len(self.files)

    #start outer loop to loop through bins

    for x in range(0, NumBins):    

      #start inner loop to loop through file values within the bin

      self.setBin488(x)

      self.setBin561(x)

  

  def setBin488(self, BinNum):

    BinValues = []

    for y in  range(0, len(self.binned488[BinNum])):

      if not self.binned488[y][BinNum]:

        continue

      else:

        BinValues.append(self.binned488[y][BinNum])

    self.avg488[BinNum] = Average(BinValues)

    self.sem488[BinNum] = StandardDeviation(BinValues) / math.sqrt(len(BinValues))

  

  def setBin561(self, BinNum):

    BinValues = []

    for y in  range(0, len(self.binned561[BinNum])):

      if not self.binned561[y][BinNum]:

        continue

      else:

        BinValues.append(self.binned561[y][BinNum])

    if len(BinValues) > 1:

      self.avg561[BinNum] = Average(BinValues)

      self.sem561[BinNum] = StandardDeviation(BinValues) / math.sqrt(len(BinValues))



import re

import os

import math



#define global variable NumBins

NumBins = 25



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

  

x = range(0, NumBins)



Headings = ['x', 'actin', 'actin sem', 'cofilin', 'cofilin sem']



Output = {'x' : x}



#for StrainName in StrainsDict:



StrainName = 'CY259'

StrainsDict[StrainName].doStats()

Output['actin'] = StrainsDict[StrainName].avg488

Output['actin sem'] = StrainsDict[StrainName].sem488

Output['cofilin'] = StrainsDict[StrainName].avg561

Output['cofilin sem'] = StrainsDict[StrainName].sem561  

WriteToFile(Output, Headings, 'typical/'+StrainName+'.txt')  