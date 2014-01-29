def ParseFile(InFileName): 
  global Headings
  global Series
  InFile = open(InFileName, 'r')
  LineNum = 0
  ColNum = 0
  raw561 = []
  raw488 = [] 
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
        raw561.append(Col1)
        raw488.append(Col2)
      else:
        raw488.append(Col1)
        raw561.append(Col2)
    LineNum = LineNum + 1
  Headings.append(File + ' X')
  Headings.append(File + ' Y')
  Series[File + ' X'] = raw561
  Series[File + ' Y'] = raw488
  Series['AllY'] = Series['AllY'] + raw488
  Series['AllX'] = Series['AllX'] + raw561  
  InFile.close()
  return True

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
  #write the heading row
  Line = ""
  while Col < NumOfColumns:
    Line = Line + Headings[Col] + "\t"
    Col = Col + 1
  OutFile.write(Line + '\n')
  #write the data rows
  while Row < NumOfRows:
    Col = 0
    Line = ""
    while Col < NumOfColumns:
      Heading = Headings[Col]
      Data = Series[Heading]
      try:
        DataPoint = Data[Row]
      except:
        DataPoint = ""
      Line = Line + str(DataPoint) + "\t"
      Col = Col + 1
    OutFile.write(Line + "\n")
    Row = Row + 1 
  OutFile.close()
 
import os
import re

#Pattern (global) is the char allowed from input files
Pattern = re.compile(r'[A-Za-z0-9.,]')

Headings = ['AllX', 'AllY']

Series = {}
Series['AllX'] = []
Series['AllY'] = []

Dir = 'raw/2013_09_13/'

Files = os.listdir(Dir)

for File in Files:
  if File.find('CY4_pCE206') != -1:
    ParseFile(Dir + File)

WriteToFile(Series, Headings, 'raw_xy.txt' )



