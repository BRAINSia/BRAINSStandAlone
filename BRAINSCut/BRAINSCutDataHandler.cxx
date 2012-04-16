#include "BRAINSCutDataHandler.h"
#include "XMLConfigurationFileParser.h"
#include "GenericTransformImage.h"

#include <itkSmoothingRecursiveGaussianImageFilter.h>
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
  atlasDataSet = this->GetAtlasDataSet();

  atlasFilename=atlasDataSet->GetImageFilenameByType( registrationImageTypeToUse) ;
  atlasBinaryFilename=atlasDataSet->GetMaskFilenameByType( "RegistrationROI" );
  std::cout<<atlasBinaryFilename<<std::endl;
}

void
BRAINSCutDataHandler
::SetAtlasImage()
{
  atlasImage = ReadImageByFilename( atlasFilename );
}

void
BRAINSCutDataHandler
::SetRhoPhiThetaFromNetConfiguration()
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

DataSet::StringVectorType
BRAINSCutDataHandler
::GetROIIDsInOrder()
{
  return roiIDsInOrder;
}

void
BRAINSCutDataHandler
::SetRegionsOfInterestFromNetConfiguration()
{
  roiDataList = this->Get<ProbabilityMapList>("ProbabilityMapList");
  roiIDsInOrder = roiDataList->CollectAttValues<ProbabilityMapParser>("StructureID");

  std::sort( roiIDsInOrder.begin(), roiIDsInOrder.end() ); // get l_caudate, l_globus, .. , r_caudate, r_globus..
  roiCount = roiDataList->size();
}

/** registration related */
void
BRAINSCutDataHandler
::SetRegistrationParametersFromNetConfiguration()
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
::SetGradientSizeFromNetConfiguration()
{
  gradientSize = annModelConfiguration->GetAttribute<IntValue>("GradientProfileSize");
}

WorkingImagePointer
BRAINSCutDataHandler
::ReadImageByFilename( const std::string  filename )
{
  WorkingImagePointer readInImage;

  ReadInImagePointer inputImage = itkUtil::ReadImage<ReadInImageType>(filename.c_str() );
  readInImage = itkUtil::ScaleAndCast<ReadInImageType,
                                      WorkingImageType>(inputImage,
                                                        ZeroPercentValue,
                                                        HundredPercentValue);
  return readInImage;
}

/* inline functions */

inline
DisplacementFieldType::Pointer
BRAINSCutDataHandler
::GetDeformationField( std::string filename)
{
  const bool useTransform( filename.find(".mat") != std::string::npos );
  if( useTransform )
    {
    return NULL;
    }
  typedef itk::ImageFileReader<DisplacementFieldType> DeformationReaderType;
  DeformationReaderType::Pointer deformationReader = DeformationReaderType::New();
  deformationReader->SetFileName( filename );
  deformationReader->Update();

  return deformationReader->GetOutput();
}

inline
GenericTransformType::Pointer
BRAINSCutDataHandler
::GetGenericTransform( std::string filename)
{
  const bool useDeformation( filename.find(".mat") == std::string::npos );
  if( useDeformation )
    {
    std::cout<<"return null deformation"<<std::endl;
    return NULL;
    }
  return itk::ReadTransformFromDisk( filename );
}

bool
BRAINSCutDataHandler
::GetNormalizationFromNetConfiguration()
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

WorkingImagePointer
BRAINSCutDataHandler
::SmoothImage( const WorkingImagePointer image, const float GaussianValue)
{
  if( GaussianValue < 0 + FLOAT_TOLERANCE )
    {
    std::cout << "Gaussian value is less than tolerance. "
              << "No smoothing occurs at this time"
              << std::endl;
    return image;
    }
  std::cout<<"Smooth Image with Gaussian value of :: "
           << GaussianValue
           <<std::endl;
  typedef itk::SmoothingRecursiveGaussianImageFilter<WorkingImageType, WorkingImageType> SmoothingFilterType;
  SmoothingFilterType::Pointer smoothingFilter = SmoothingFilterType::New();

  smoothingFilter->SetInput( image);
  smoothingFilter->SetSigma( GaussianValue );

  smoothingFilter->Update();

  return smoothingFilter->GetOutput();
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

  std::string filename = basename + "D"+tempDepth+"NF"+tempNTrees;

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
