#ifndef BRAINSCutCreateVectorModel_h
#define BRAINSCutCreateVectorModel_h

#include "BRAINSCutDataHandler.h"
#include "FeatureInputVector.h"

class BRAINSCutCreateVector 
{
public:
  BRAINSCutCreateVector( BRAINSCutDataHandler dataHandler );

  void SetTrainingDataSet();
  void SetTrainingVectorFilename();

  void CreateVectors();

  int  CreateSubjectVectors( SubjectDataSet& subject, std::ofstream& outputStream);

  void WriteCurrentVectors( InputVectorMapType& pairedInput, 
                            OutputVectorMapType& pairedOutput,
                            std::ofstream& outputStream );

  void WriteHeaderFile( std::string vectorFilename,
                        int inputVectorSize, 
                        int outputVectorSize, 
                        int numberOfInputVector);

private:
  BRAINSCutDataHandler myDataHandler;
  BRAINSCutDataHandler::TrainDataSetListType trainDataSetList;

  int inputVectorSize;
  int outputVectorSize;

  OutputVectorMapType GetPairedOutput( std::map<std::string,
                                                WorkingImagePointer>& deformedROIs, std::string roiName,
                                       std::string subjectROIBinaryFilename,
                                       int roiNumber);

  inline std::string GetROIBinaryFilename( SubjectDataSet& subject, std::string roiName);
  inline scalarType GetBinaryValue( scalarType value);

};
#endif
