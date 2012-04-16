#ifndef BRAINSCutDataHandler_h
#define BRAINSCutDataHandler_h

#include "BRAINSCutPrimary.h"

/*
 * BRAINSCut Primary Class Starts here
 */

class BRAINSCutDataHandler : public BRAINSCutConfiguration
{
public:
  BRAINSCutDataHandler(){};
  BRAINSCutDataHandler(std::string modelConfigurationFilenameFilename);

  void                     SetNetConfiguration();
  BRAINSCutConfiguration * GetNetConfiguration();

  void        SetNetConfigurationFilename(const std::string filename);
  std::string GetNetConfigurationFilename();

  void SetAtlasDataSet();
  void SetAtlasImage();
  void SetRegionsOfInterest();
  void SetRegistrationParameters();
  void SetRhoPhiTheta();
  void         SetGradientSize();
  unsigned int GetGradientSize();

  void SetANNModelConfiguration();

  std::string GetModelBaseName();

  void        SetANNModelFilenameAtIteration( const int iteration);
  void        SetANNTestingSSEFilename();
  std::string GetANNTestingSSEFilename();
  std::string GetANNModelFilenameAtIteration( const int iteration);
  std::string GetANNModelFilename( );

  void        SetRandomForestModelFilename(int depth, int nTree);
  std::string GetRandomForestModelFilename();
  std::string GetRFModelFilename( int depth,int NTrees);

  DataSet::StringVectorType GetROIIDsInOrder();

  void        SetTrainVectorFilename();
  std::string GetTrainVectorFilename();

  void                  GetDeformedSpatialLocationImages( 
                                         std::map<std::string, WorkingImagePointer>& warpedSpatialLocationImages,
                                         DataSet& subject );
  void                  GetImagesOfSubjectInOrder( WorkingImageVectorType& subjectImageList, DataSet& subject);
  void                  GetDeformedROIs( std::map<std::string, 
                                         WorkingImagePointer>& deformedROIs, DataSet& subject );
  bool                  GetNormalization();
  void                  SetNormalization();

  std::string           GetAtlasFilename();
  std::string           GetAtlasBinaryFilename();
  int                   GetROIAutoDilateSize();
  unsigned int          GetROICount();
  WorkingImagePointer   GetAtlasImage();
  ProbabilityMapList *  GetROIDataList();
  DataSet *      GetAtlasDataSet();

  BRAINSCutConfiguration::ApplyDataSetListType GetApplyDataSet();

  int                   GetTrainIteration();
  scalarType            GetANNOutputThreshold();
  scalarType            GetGaussianSmoothingSigma();

  std::string           GetSubjectToAtlasRegistrationFilename( DataSet& subject);
  std::string           GetAtlasToSubjectRegistrationFilename( DataSet& subject);

  void         SetTrainConfiguration( std::string trainParamterName );
  unsigned int GetEpochIteration();
  float        GetDesiredError();
  unsigned int GetMaximumDataSize();
  int          GetANNHiddenNodesNumber();
  float        GetActivationFunctionSlope();
  float        GetActivationFunctionMinMax();
  int          GetMaxDepth();
  int          GetMinSampleCount();
  bool         GetUseSurrogates();
  bool         GetCalcVarImportance();
  int          GetMaxTreeCount();


protected:
  NeuralParams *   annModelConfiguration;

  /* train parameters */
  TrainingParameters *TrainConfiguration;

  /** atlas data set*/
  DataSet *    atlasDataSet;
  std::string         atlasFilename;
  std::string         atlasBinaryFilename;
  WorkingImagePointer atlasImage;

  /**ProbabilityMaps*/
  ProbabilityMapList *             roiDataList;
  DataSet::StringVectorType roiIDsInOrder;;
  unsigned int                     roiCount;

  /** registration data set */
  RegistrationConfigurationParser * registrationParser;
  std::string                       registrationImageTypeToUse;
  std::string                       registrationID;
  int                               roiAutoDilateSize;

  /** Spatial Coordinate System Images*/
  WorkingImagePointer rho;
  WorkingImagePointer phi;
  WorkingImagePointer theta;

  unsigned int gradientSize;

  /** vector file name */
  std::string trainVectorFilename;
  bool        normalization;

  /** model name **/
  std::string ANNModelFilename;
  std::string RandomForestModelFilename;
  std::string ANNTestingSSEFilename;

private:
  WorkingImageType GetDeformedImage( WorkingImageType image);
  std::string NetConfigurationFilename;

};
#endif
