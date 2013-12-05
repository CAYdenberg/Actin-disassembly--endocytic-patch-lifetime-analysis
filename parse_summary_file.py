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
  while Row < NumOfRows:
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
    
#main script
InFileName = 'process_patch.txt'
InFile = open(InFileName, 'r')
Strains = []
ActinLifetimes = {}
CofilinLifetimes = {}
Delays = {}
CofInt = {}
LineNum = 0
for Line in InFile:
  if LineNum == 0:
    LineNum = LineNum + 1
    continue
  DataList = Line.split('\t')
  PatchName = DataList[0]
  PatchNameList = PatchName.split('_')
  Strain = PatchNameList[0]
  if not (Strain in Strains):
    Strains.append(Strain)
    ActinLifetimes[Strain] = []
    CofilinLifetimes[Strain] = []
    Delays[Strain] = []
    CofInt[Strain] = []
  ActinLifetimes[Strain].append(DataList[1])
  if DataList[2]:
    CofPercent_flt = float( DataList[2] ) #/ float( DataList[1] )
    CofPercent_str = str(CofPercent_flt)
    CofilinLifetimes[Strain].append(CofPercent_str)
  if DataList[3]:
    DelayPercent_flt = float( DataList[3] ) #/ float( DataList[1] )
    DelayPercent_str = str(DelayPercent_flt)
    Delays[Strain].append(DelayPercent_str)
  CofInt[Strain].append( DataList[5] )
  LineNum = LineNum + 1
for Strain in Strains:
  ActinLifetimes[Strain].sort()
  CofilinLifetimes[Strain].sort()
  Delays[Strain].sort()
  CofInt[Strain].sort()
InFile.close()

print len(ActinLifetimes['CY280'])

Strains.sort()
WriteToFile(ActinLifetimes, Strains, 'actin_lifetimes.txt')
WriteToFile(CofilinLifetimes, Strains, 'cofilin_absolute.txt')
WriteToFile(Delays, Strains, 'delay_absolute.txt')