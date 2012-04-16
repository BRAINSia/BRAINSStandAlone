#include "BRAINSCutDataHandler.h"
#include "XMLConfigurationFileParser.h"
#include "GenericTransformImage.h"


/** constructors */
BRAINSCutDataHandler
::BRAINSCutDataHandler( std::string modelConfigurationFilenameFilename )
  :BRAINSCutConfiguration()
{
  try
    {
    SetNetConfigurationFilename( modelConfigurationFilenameFilename );
    SetNetConfiguration();
    }
  catch( BRAINSCutExceptionStringHandler& e)
    {
      std::cout<<e.Error()<<std::endl;
      exit(EXIT_FAILURE);
    }
}

void
BRAINSCutDataHandler
::SetNetConfiguration()
{
  try
    {
    std::list<XMLElementContainer *> elementList;

    elementList.push_front( this );

    XMLConfigurationFileParser BRIANSCutXMLConfigurationFileParser = XMLConfigurationFileParser( NetConfigurationFilename );
    BRIANSCutXMLConfigurationFileParser.SetUserData( &elementList );
    BRIANSCutXMLConfigurationFileParser.Parse();
    }
  catch( BRAINSCutExceptionStringHandler& e)
    {
      std::cout<<e.Error()<<std::endl;
      exit(EXIT_FAILURE);
    }
}

void
BRAINSCutDataHandler
::SetAtlasDataSet()
{
  std::cout<<__LINE__<<"::"<<__FILE__<<std::endl;
  atlasDataSet = this->GetAtlasDataSet();
  std::cout<<__LINE__<<"::"<<__FILE__<<std::endl;
  std::cout<<"registrationImageTypeToUse :: "<<registrationImageTypeToUse <<std::endl;

  if( registrationImageTypeToUse.empty() )
  {
    std::cout<<"registrationImageTypeToUse is empty."<<std::endl;
    exit(EXIT_FAILURE);
  }
  atlasFilename=atlasDataSet->GetImageFilenameByType( registrationImageTypeToUse) ;
  std::cout<<__LINE__<<"::"<<__FILE__<<std::endl;
  atlasBinaryFilename=atlasDataSet->GetMaskFilenameByType( "RegistrationROI" );
  std::cout<<__LINE__<<"::"<<__FILE__<<std::endl;
  std::cout<<atlasBinaryFilename<<std::endl;
  std::cout<<__LINE__<<"::"<<__FILE__<<std::endl;
}

void
BRAINSCutDataHandler
::SetAtlasImage()
{
  atlasImage = ReadImageByFilename( atlasFilename );
}

void
BRAINSCutDataHandler
::SetRhoPhiTheta()
{
  rho = ReadImageByFilename( atlasDataSet->GetSpatialLocationFilenameByType("rho") );
  phi = ReadImageByFilename( atlasDataSet->GetSpatialLocationFilenameByType("phi") );
  theta = ReadImageByFilename( atlasDataSet->GetSpatialLocationFilenameByType("theta") );

}

void
BRAINSCutDataHandler
::SetNetConfigurationFilename(const std::string filename)
{
  NetConfigurationFilename = filename;
}

std::string
BRAINSCutDataHandler
::GetNetConfigurationFilename()
{
  return NetConfigurationFilename;
}

int
BRAINSCutDataHandler
::GetTrainIteration()
{
  int trainIteration = this->Get<TrainingParameters>("ANNParameters")
                            ->GetAttribute<IntValue>("Iterations");

  return trainIteration;
}

DataSet::StringVectorType
BRAINSCutDataHandler
::GetROIIDsInOrder()
{
  return roiIDsInOrder;
}

void
BRAINSCutDataHandler
::SetRegionsOfInterest()
{
  roiDataList = this->Get<ProbabilityMapList>("ProbabilityMapList");
  roiIDsInOrder = roiDataList->CollectAttValues<ProbabilityMapParser>("StructureID");

  std::sort( roiIDsInOrder.begin(), roiIDsInOrder.end() ); // get l_caudate, l_globus, .. , r_caudate, r_globus..
  roiCount = roiDataList->size();
}

/** registration related */
void
BRAINSCutDataHandler
::SetRegistrationParameters()
{

  registrationParser =
    this->Get<RegistrationConfigurationParser>("RegistrationConfiguration");

  registrationImageTypeToUse =
    std::string( registrationParser->GetAttribute<StringValue>( "ImageTypeToUse") );

  registrationID = std::string(
    registrationParser->GetAttribute<StringValue>("ID") );

  roiAutoDilateSize = registrationParser->GetAttribute<IntValue>("BRAINSROIAutoDilateSize") ;
}

std::string
BRAINSCutDataHandler
::GetSubjectToAtlasRegistrationFilename( DataSet& subject)
{
  std::string filename = subject.GetRegistrationWithID( registrationID )
    ->GetAttribute<StringValue>("SubjToAtlasRegistrationFilename");
  return filename;
}

std::string
BRAINSCutDataHandler
::GetAtlasToSubjectRegistrationFilename( DataSet& subject)
{
  std::string filename = subject.GetRegistrationWithID( registrationID )
    ->GetAttribute<StringValue>("AtlasToSubjRegistrationFilename");
  return filename;
}

void
BRAINSCutDataHandler
::GetDeformedSpatialLocationImages( std::map<std::string, WorkingImagePointer>& warpedSpatialLocationImages,
                                    DataSet& subject)
{
  std::string atlasSubjectRegistrationFilename = GetAtlasToSubjectRegistrationFilename( subject );

  DisplacementFieldType::Pointer deformation = GetDeformationField( atlasSubjectRegistrationFilename );
  GenericTransformType::Pointer genericTransform = GetGenericTransform( atlasSubjectRegistrationFilename );

  WorkingImagePointer referenceImage =
    ReadImageByFilename( subject.GetImageFilenameByType(registrationImageTypeToUse) );
  const std::string transoformationPixelType = "float";

  warpedSpatialLocationImages.insert( std::pair<std::string, WorkingImagePointer>
                                        ("rho", GenericTransformImage<WorkingImageType,
                                                                      WorkingImageType,
                                                                      DisplacementFieldType>
                                          ( rho, referenceImage, deformation, genericTransform,
                                          0.0, "Linear", transoformationPixelType == "binary") ) );
  warpedSpatialLocationImages.insert( std::pair<std::string, WorkingImagePointer>
                                        ("phi", GenericTransformImage<WorkingImageType,
                                                                      WorkingImageType,
                                                                      DisplacementFieldType>
                                          ( phi, referenceImage, deformation, genericTransform,
                                          0.0, "Linear", transoformationPixelType == "binary") ) );
  warpedSpatialLocationImages.insert( std::pair<std::string, WorkingImagePointer>
                                        ("theta", GenericTransformImage<WorkingImageType,
                                                                        WorkingImageType,
                                                                        DisplacementFieldType>
                                          ( theta, referenceImage, deformation, genericTransform,
                                          0.0, "Linear", transoformationPixelType == "binary") ) );
}

void
BRAINSCutDataHandler
::GetImagesOfSubjectInOrder( WorkingImageVectorType& subjectImageList, DataSet& subject)
{
  DataSet::StringVectorType imageListFromAtlas = atlasDataSet->GetImageTypes(); // T1, T2, SG, ...
  std::sort( imageListFromAtlas.begin(), imageListFromAtlas.end() );            // SG, T1, T2, ... ascending order
  for( DataSet::StringVectorType::iterator imgTyIt = imageListFromAtlas.begin();
       imgTyIt != imageListFromAtlas.end();
       ++imgTyIt ) // imgTyIt = image type iterator
    {
    std::cout<< *imgTyIt <<std::endl;
    WorkingImagePointer currentTypeImage = ReadImageByFilename( subject.GetImageFilenameByType( *imgTyIt ) );
    subjectImageList.push_back( currentTypeImage );
    }
}

void
BRAINSCutDataHandler
::GetDeformedROIs( std::map<std::string, WorkingImagePointer>& warpedROIs,
                   DataSet& subject)
{
  std::string atlasSubjectRegistrationFilename = GetAtlasToSubjectRegistrationFilename( subject );

  /** Get the transformation file
   * Note that only one of transformation type will be used. Either deformation or transformation
   * That determined based on the file name at the GetDeformationField
   */
  DisplacementFieldType::Pointer deformation = GetDeformationField( atlasSubjectRegistrationFilename );
  GenericTransformType::Pointer genericTransform = GetGenericTransform( atlasSubjectRegistrationFilename );

  WorkingImagePointer referenceImage =
    ReadImageByFilename( subject.GetImageFilenameByType(registrationImageTypeToUse) );

  const std::string transformationPixelType = "float";
  for( DataSet::StringVectorType::iterator roiTyIt = roiIDsInOrder.begin();
       roiTyIt != roiIDsInOrder.end();
       ++roiTyIt )
    {
    std::string roiFilename = roiDataList->GetMatching<ProbabilityMapParser>( "StructureID", (*roiTyIt).c_str() )
      ->GetAttribute<StringValue>("Filename");
    WorkingImagePointer currentROI = ReadImageByFilename( roiFilename );

    warpedROIs.insert( std::pair<std::string, WorkingImagePointer>(
                         (*roiTyIt), GenericTransformImage<WorkingImageType,
                                                           WorkingImageType,
                                                           DisplacementFieldType>
                           ( currentROI, referenceImage, deformation,
                           genericTransform, 0.0, "Linear",
                           transformationPixelType == "binary") ) );
    }
}

void
BRAINSCutDataHandler
::SetANNModelConfiguration()
{
  annModelConfiguration = this->Get<NeuralParams>("NeuralNetParams");
}

void
BRAINSCutDataHandler
::SetGradientSize()
{
  gradientSize = annModelConfiguration->GetAttribute<IntValue>("GradientProfileSize");
}

unsigned int
BRAINSCutDataHandler
::GetGradientSize()
{
  return gradientSize ;
}

bool
BRAINSCutDataHandler
::GetNormalization()
{
  std::string normalizationString;
  try
    { 
    normalizationString = annModelConfiguration->GetAttribute<StringValue>("Normalization");
    }catch( BRAINSCutExceptionStringHandler& e)
    {
      std::cout<<e.Error()<<std::endl;
      exit(EXIT_FAILURE);
    }


  if( normalizationString == "true" )
    {
    return true;
    }
  else
    {
    return false;
    }
}

/** model file name */
std::string
BRAINSCutDataHandler
::GetModelBaseName( )
{
  std::string basename;
  try
    {
    basename = annModelConfiguration->GetAttribute<StringValue>("TrainingModelFilename");
    }
  catch( ... )
    {
    throw BRAINSCutExceptionStringHandler("Fail to get the ann model file name");
    exit(EXIT_FAILURE);
    }
  return  basename;
}

std::string
BRAINSCutDataHandler
::GetANNModelFilename( )
{
  return ANNModelFilename;
}

std::string
BRAINSCutDataHandler
::GetANNModelFilenameAtIteration( const int iteration)
{
  SetANNModelFilenameAtIteration( iteration );
  return ANNModelFilename;
}

void
BRAINSCutDataHandler
::SetANNModelFilenameAtIteration( const int iteration)
{
  ANNModelFilename = GetModelBaseName();

  char temp[10];
  sprintf( temp, "%09d", iteration );
  ANNModelFilename += temp;
}

std::string
BRAINSCutDataHandler
::GetRFModelFilename( int depth,
                      int NTrees)
{
  std::string basename = GetModelBaseName();

  char tempDepth[5];
  sprintf( tempDepth, "%04u", depth );

  char tempNTrees[5];
  sprintf( tempNTrees, "%04u", NTrees );

  std::string filename = basename + "D"+tempDepth+"NT"+tempNTrees;

  return filename;
}

std::string
BRAINSCutDataHandler
::GetAtlasFilename()
{
  return atlasFilename;
}

std::string
BRAINSCutDataHandler
::GetAtlasBinaryFilename()
{
  return atlasBinaryFilename;
}

int
BRAINSCutDataHandler
::GetROIAutoDilateSize()
{
  return roiAutoDilateSize;
}

unsigned int
BRAINSCutDataHandler
::GetROICount()
{
  return roiCount;
}

WorkingImagePointer
BRAINSCutDataHandler
::GetAtlasImage()
{
  return atlasImage;
}
ProbabilityMapList *  
BRAINSCutDataHandler
::GetROIDataList()
{
  return roiDataList;
}

DataSet *
BRAINSCutDataHandler
::GetAtlasDataSet()
{
  return atlasDataSet;
}

scalarType
BRAINSCutDataHandler
::GetANNOutputThreshold()
{
  scalarType annOutputThreshold =
    this->Get<ApplyModelType>("ApplyModel")
              ->GetAttribute<FloatValue>("MaskThresh");
  if( annOutputThreshold < 0.0F )
    {
    std::string msg = " ANNOutput Threshold cannot be less than zero. \n";
    throw BRAINSCutExceptionStringHandler( msg );
    }
  return annOutputThreshold;
}

//
// Apply related 
//
void
BRAINSCutDataHandler
::SetRandomForestModelFilename(int depth, int nTree)
{    
  if( depth < 0 && nTree <0 )
    {
    std::cout<<"Read random forest model parameters from xml file"<<std::endl;
    nTree= this->Get<TrainingParameters>("RandomForestParameters")
                            ->GetAttribute<IntValue>("MaxDepth");
    depth= this->Get<TrainingParameters>("RandomForestParameters")
                            ->GetAttribute<IntValue>("MaxTreeCount");
    }
  RandomForestModelFilename =  GetRFModelFilename( depth, nTree );
}

std::string 
BRAINSCutDataHandler
::GetRandomForestModelFilename()
{
  if( RandomForestModelFilename.empty() )
  {
    std::string msg = "Random forest model file is empty \n";
    throw BRAINSCutExceptionStringHandler( msg );
  }
  return RandomForestModelFilename;
}

void
BRAINSCutDataHandler
::SetANNTestingSSEFilename()
{
  ANNTestingSSEFilename = GetModelBaseName();
  ANNTestingSSEFilename += "ValidationSetSSE.txt";
}

std::string 
BRAINSCutDataHandler
::GetANNTestingSSEFilename()
{
  return ANNTestingSSEFilename;
}

void
BRAINSCutDataHandler
::SetTrainVectorFilename()
{
  trainVectorFilename = this->GetAttribute<StringValue>("TrainingVectorFilename");
  trainVectorFilename += "ANN"; // TODO
  std::cout << "+++++++++++++++++++++++++++++++++++++++++++++++++++" << std::endl;
  std::cout << "Write vector file at " << trainVectorFilename << std::endl;
  std::cout << "+++++++++++++++++++++++++++++++++++++++++++++++++++" << std::endl;
}

std::string
BRAINSCutDataHandler
::GetTrainVectorFilename()
{
  if( trainVectorFilename.empty() )
  {
    std::string msg = "The train vector file name is empty.\n";
    throw BRAINSCutExceptionStringHandler( msg );
  }
  return trainVectorFilename;
}

BRAINSCutConfiguration::ApplyDataSetListType
BRAINSCutDataHandler
::GetApplyDataSet()
{
  BRAINSCutConfiguration::ApplyDataSetListType applyDataSetList;
  try
    {
      applyDataSetList = this->GetApplyDataSets();
    }
  catch( BRAINSCutExceptionStringHandler& e )
    {
    std::cout << e.Error() << std::endl;
    exit(EXIT_SUCCESS);
    }
  return applyDataSetList;
}

scalarType
BRAINSCutDataHandler
::GetGaussianSmoothingSigma()
{
  scalarType gaussianSmoothingSigma=
    this->Get<ApplyModelType>("ApplyModel")
              ->GetAttribute<FloatValue>("GaussianSmoothingSigma");
  return gaussianSmoothingSigma;
}

void
BRAINSCutDataHandler
::SetTrainConfiguration( std::string trainParameterName )
{
  TrainConfiguration = this->Get<TrainingParameters>( trainParameterName.c_str() );
}

unsigned int
BRAINSCutDataHandler
::GetEpochIteration()
{
  unsigned int trainEpochIteration = TrainConfiguration->GetAttribute<IntValue>("EpochIterations");
  return trainEpochIteration;
}

float
BRAINSCutDataHandler
::GetDesiredError()
{
  float trainDesiredError = TrainConfiguration->GetAttribute<FloatValue>("DesiredError");
  return trainDesiredError;
}

unsigned int
BRAINSCutDataHandler
::GetMaximumDataSize()
{
  unsigned int trainMaximumDataSize = TrainConfiguration->GetAttribute<IntValue>("MaximumVectorsPerEpoch");
  return trainMaximumDataSize;
}

int
BRAINSCutDataHandler
::GetANNHiddenNodesNumber()
{
  int ANNHiddenNodesNumber = TrainConfiguration->GetAttribute<IntValue>("NumberOfHiddenNodes");
  return ANNHiddenNodesNumber;
}

float
BRAINSCutDataHandler
::GetActivationFunctionSlope()
{
  float activationSlope = TrainConfiguration->GetAttribute<FloatValue>("ActivationSlope");
  return activationSlope;
  
}

float
BRAINSCutDataHandler
::GetActivationFunctionMinMax()
{
  float activationMinMax = TrainConfiguration->GetAttribute<FloatValue>("ActivationMinMax");
  return activationMinMax;
}

/** Get Random Tree */
int 
BRAINSCutDataHandler
::GetMaxDepth()
{
  int trainMaxDepth= TrainConfiguration->GetAttribute<IntValue>("MaxDepth");
  return trainMaxDepth;
}

int
BRAINSCutDataHandler
::GetMinSampleCount()
{
  int trainMinSampleCount= TrainConfiguration->GetAttribute<IntValue>("MinSampleCount");
  return trainMinSampleCount;
}

bool
BRAINSCutDataHandler
::GetUseSurrogates()
{
  bool trainUseSurrogates= TrainConfiguration->GetAttribute<BooleanValue>("UseSurrogates");
  return trainUseSurrogates;
}

bool
BRAINSCutDataHandler
::GetCalcVarImportance()
{
  bool trainCalcVarImportance= TrainConfiguration->GetAttribute<BooleanValue>("CalcVarImportance");
  return trainCalcVarImportance;
}

int
BRAINSCutDataHandler
::GetMaxTreeCount()
{
  int trainMaxTreeCount= TrainConfiguration->GetAttribute<IntValue>("MaxTreeCount");
  return trainMaxTreeCount;
}
