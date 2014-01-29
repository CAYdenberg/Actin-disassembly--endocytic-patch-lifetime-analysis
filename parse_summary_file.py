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
#each dictionary will be indexed by Strain and will contain
#lists containing all the data
ActinLifetimes = {}
CofilinLifetimes = {}
Delays = {}
CumulInt = {}
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
    CumulInt[Strain] = []
  ActinLifetimes[Strain].append(DataList[1])
  if DataList[2]:
    CofilinLifetimes[Strain].append(DataList[2])
  if DataList[3]:
    Delays[Strain].append(DataList[3])
  if DataList[4]:
    CumulInt[Strain].append(DataList[4])
  LineNum = LineNum + 1

InFile.close()

#sort all the lists
for Strain in Strains:
  ActinLifetimes[Strain].sort()
  CofilinLifetimes[Strain].sort()
  Delays[Strain].sort()
  CumulInt[Strain].sort()

Strains.sort()
WriteToFile(ActinLifetimes, Strains, 'actin_lifetimes.txt')
WriteToFile(CofilinLifetimes, Strains, 'cofilin_absolute.txt')
WriteToFile(Delays, Strains, 'delay_absolute.txt')
WriteToFile(CumulInt, Strains, 'cofilin_intensity_score.txt')