import argparse

def xmlGenerator( outputFilename ):
  outputStream = open( outputFilename, 'w')

  outputStream.write( "<AutoSegProcessDescription>\n" )
  outputStream.write( "</AutoSegProcessDescription>\n" )

  outputStream.close()


##
brainscutParser = argparse.ArgumentParser( description ='BRAINSCut command line argument parser')

#
# input arguments
#
brainscutParser.add_argument('--inputSubjectT1Filename', help='T1 subject filename' )
brainscutParser.add_argument('--inputSubjectT2Filename', help='T2 subject filename' )
brainscutParser.add_argument('--inputSubjectSGFilename', help='SG subject filename' )

brainscutParser.add_argument('--templateT1', help='template T1-weighted filename' )

brainscutParser.add_argument('--probabilityMaps', help='model probability maps for regions of interest',
                             action='append')

brainscutParser.add_argument('--randomForestModelFilename', help='random forest model file name')
brainscutParser.add_argument('--deformationToSubjectFromTemplate', help="deformationToSubjectFromTemplate")

#
# output arguments
#
brainscutParser.add_argument('--outputBinaryFilenames', help='output binary file names paired to the probability maps',
                             action='append')
brainscutParser.add_argument('--xmlFilename',help='BRAINSCut xml configuration filename', default="output.xml")

args=brainscutParser.parse_args()

print( args )
if args.xmlFilename != "":
  xmlGenerator( args.xmlFilename )
else:
  print("no xml filename is given to process")
