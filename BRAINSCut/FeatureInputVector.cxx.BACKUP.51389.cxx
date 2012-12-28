#include "FeatureInputVector.h"
#include "BRAINSCutExceptionStringHandler.h"
#include "itkLabelStatisticsImageFilter.h"

const scalarType FeatureInputVector::MIN = -1.0F;
const scalarType FeatureInputVector::MAX = 1.0F;

const unsigned int MAX_IMAGE_SIZE=1024;
const WorkingImageType::IndexType ConstantHashIndexSize = {{1024, 1024, 1024}};


int
FeatureInputVector
::DoUnitTests(void) const
{
  std::cout << "INTERNAL TEST OF INDEX_KEY INPUTVECTOR" << std::endl;
  int allOK = EXIT_SUCCESS;
  for( WorkingImageType::IndexType::IndexValueType i = 0; i < ConstantHashIndexSize[0]; i++ )
    {
    for( WorkingImageType::IndexType::IndexValueType j = 0; j < ConstantHashIndexSize[1]; j++ )
      {
      for( WorkingImageType::IndexType::IndexValueType k = 0; k < ConstantHashIndexSize[2]; k++ )
        {
        // QuickTest
        WorkingImageType::IndexType index;
        index[0] = i;
        index[1] = j;
        index[2] = k;
        const hashKeyType currKey = HashKeyFromIndex( index );
        const WorkingImageType::IndexType outIndex = HashIndexFromKey(currKey);
        if( index != outIndex )
          {
          std::cout << "HACK: UNIT TEST " << index << " = " << outIndex << " with key " << currKey << std::endl;
          allOK = EXIT_FAILURE;
          }
        }
      }
    }
  if( allOK == EXIT_FAILURE )
    {
    std::cout << "ERROR: Hash lookups are not invertable." << std::endl;
    }
  else
    {
    std::cout << "All hash lookups for images < " << ConstantHashIndexSize << " are validated." << std::endl;
    }
  return allOK;
}

FeatureInputVector
::FeatureInputVector() :
  m_gradientSize(-1),
  m_normalization(false)
{
  m_spatialLocations.clear();
  m_candidateROIs.clear();
  m_gradientOfROI.clear();
  m_imageInterpolator = ImageLinearInterpolatorType::New();
}

FeatureInputVector
::~FeatureInputVector() 
{
<<<<<<< HEAD
  this->m_imagesOfInterestInOrder.clear();
  this->m_spatialLocations.clear();
  this->m_gradientOfROI.clear();
  this->m_minmax.clear();
  this->m_candidateROIs.clear();
=======
  this->imagesOfInterestInOrder.clear();
  this->spatialLocations.clear();
  this->gradientOfROI.clear();
  this->m_minmax.clear();
  this->candidateROIs.clear();
>>>>>>> ac2e6bf... ENH: Normalization Parameter

}
void
FeatureInputVector
::SetGradientSize(unsigned int length)
{
  m_gradientSize = length;
}

void
FeatureInputVector
::SetImagesOfInterestInOrder( WorkingImageVectorType& images)
{
  m_imagesOfInterestInOrder = images;
}

void
FeatureInputVector
::SetImagesOfSpatialLocation( std::map<std::string, WorkingImagePointer>& SpatialLocationImages)
{
  if( SpatialLocationImages.size() != 3 ||
      SpatialLocationImages.find("rho") == SpatialLocationImages.end() ||
      SpatialLocationImages.find("phi") == SpatialLocationImages.end()  ||
      SpatialLocationImages.find("theta") == SpatialLocationImages.end()  )
    {
    itkGenericExceptionMacro(<< "::number of images for spatial location should be 3 not "
                             << SpatialLocationImages.size() );
    }
  //Ensure that images are sufficiently small to process correctly.
  WorkingImageType::SizeType testSize=
    SpatialLocationImages.find("rho")->second->GetLargestPossibleRegion().GetSize();
  for(unsigned int q=0;q<3;q++)
    {
    if(testSize[q] > MAX_IMAGE_SIZE )
      {
      std::cout << "ERROR: Image too large to process correctly" << std::endl;
      std::cout << testSize << " must be less than " << ConstantHashIndexSize << std::endl;
      exit(-1);
      }
    }
  m_spatialLocations = SpatialLocationImages;
}

void
FeatureInputVector
::SetCandidateROIs( std::map<std::string, WorkingImagePointer>& candidateROIMap)
{
  m_candidateROIs = candidateROIMap;
}

void
FeatureInputVector
::SetROIInOrder( DataSet::StringVectorType roiInOrder)
{
  m_roiIDsInOrder = roiInOrder;
}

void
FeatureInputVector
::SetGradientImage( std::string ROIName )
{
  GradientFilterType::Pointer gradientFilter = GradientFilterType::New();

  gradientFilter->SetInput( m_candidateROIs.find( ROIName)->second );
  try
    {
    gradientFilter->Update();
    }
  catch( ... )
    {
    std::string errorMsg = " Fail to generate itk gradient image.";
    throw BRAINSCutExceptionStringHandler( errorMsg );
    }
  m_gradientOfROI.insert( std::pair<std::string, GradientImageType>( ROIName, gradientFilter->GetOutput() ) );
}

void
FeatureInputVector
::SetInputVectorSize()
{
  if( m_candidateROIs.empty() || m_imagesOfInterestInOrder.empty() || m_spatialLocations.empty() )
    {
    std::string errorMsg = " Cannot compute input vector size properly.";
    errorMsg += "Either ROI(probability maps) or feature images has to be set to compute input vector size.";
    throw BRAINSCutExceptionStringHandler( errorMsg );
    }
  m_inputVectorSize = m_candidateROIs.size() + m_imagesOfInterestInOrder.size() * 3 + m_spatialLocations.size();
}

unsigned int
FeatureInputVector
::GetInputVectorSize()
{
  return m_inputVectorSize;
}

void
FeatureInputVector
::SetNormalization( const bool doNormalize)
{
  m_normalization = doNormalize;
};
/*
InputVectorMapType
FeatureInputVector
::ComputeAndGetFeatureInputOfROI( std::string ROIName )
{
  std::map<std::string, InputVectorMapType> featureInputOfROI;
  if( featureInputOfROI.find( ROIName ) == featureInputOfROI.end() )
    {
    ComputeFeatureInputOfROI( ROIName);
    }
  return InputVectorMapType(featureInputOfROI.find( ROIName )->second);
}
*/
InputVectorMapType
FeatureInputVector
::ComputeAndGetFeatureInputOfROI( std::string ROIName)
{
  std::map<std::string, InputVectorMapType> featureInputOfROI;

  std::cout<<"****************************************************"<<std::endl;
  std::cout<<"***********ComputeFEatureInputOfROI*****************"<<std::endl;
  std::cout<<"****************************************************"<<std::endl;
  SetGradientImage( ROIName );

  typedef itk::ImageRegionIterator<WorkingImageType> ImageRegionIteratorType;

  InputVectorMapType currentFeatureVector;

  WorkingImagePointer currentROIImage = m_candidateROIs.find( ROIName)->second;

  /* iterate through each voxel in the probability map */
  ImageRegionIteratorType eachVoxelInROI( currentROIImage, currentROIImage->GetLargestPossibleRegion() );

  eachVoxelInROI.GoToBegin();

  while( !eachVoxelInROI.IsAtEnd() )
    {
    if( (eachVoxelInROI.Value() > (0.0F + FLOAT_TOLERANCE) ) && (eachVoxelInROI.Value() < (1.0F - FLOAT_TOLERANCE) ) )
      {
      InputVectorType           oneRowInputFeature( m_inputVectorSize );
      InputVectorType::iterator featureElementIterator = oneRowInputFeature.begin();

      AddCandidateROIFeature( eachVoxelInROI.GetIndex(), featureElementIterator);
      AddSpatialLocation( eachVoxelInROI.GetIndex(), featureElementIterator);
      AddFeaturesImagesOfInterest(ROIName, eachVoxelInROI.GetIndex(), featureElementIterator);

      const int oneRowKey = FeatureInputVector::HashKeyFromIndex( eachVoxelInROI.GetIndex() );

      currentFeatureVector.insert( std::pair<hashKeyType, InputVectorType>( oneRowKey, oneRowInputFeature) );
      }
    ++eachVoxelInROI;
    }

  /* m_normalization */
  if( m_normalization )
    {
    SetNormalizationParameters( ROIName );
    NormalizationOfVector( currentFeatureVector, ROIName );
    }

  /* insert computed vector */
  featureInputOfROI.insert(std::pair<std::string, InputVectorMapType>( ROIName, currentFeatureVector) );

  return InputVectorMapType(featureInputOfROI.find( ROIName )->second);
}

/* set m_normalization parameters */
void
FeatureInputVector
::SetNormalizationParameters( std::string ROIName )
{
  const unsigned char defaultLabel = 1;
  /* threshold roi */
  typedef itk::BinaryThresholdImageFilter<WorkingImageType,
                                          BinaryImageType> ThresholdType;

  ThresholdType::Pointer thresholder = ThresholdType::New();

  thresholder->SetInput( m_candidateROIs.find( ROIName)->second );
  thresholder->SetLowerThreshold( 0.0F + FLOAT_TOLERANCE );
  thresholder->SetInsideValue( defaultLabel );
  thresholder->Update();

  /* get min and max for each image type*/

<<<<<<< HEAD
  m_minmaxPairVectorType currentMinMaxVector;
  for( WorkingImageVectorType::const_iterator eachTypeOfImage = m_imagesOfInterestInOrder.begin();
       eachTypeOfImage != m_imagesOfInterestInOrder.end();
=======
  minmaxPairVectorType currentMinMaxVector;
  normParamROIMapType currentROIParameter;
  for( WorkingImageVectorType::const_iterator eachTypeOfImage = imagesOfInterestInOrder.begin();
       eachTypeOfImage != imagesOfInterestInOrder.end();
>>>>>>> ac2e6bf... ENH: Normalization Parameter
       ++eachTypeOfImage )
    {
    BinaryImageType::Pointer binaryImage = thresholder->GetOutput();
    m_minmaxPairType           eachMinMax = SetMinMaxOfSubject( binaryImage, *eachTypeOfImage );
    currentMinMaxVector.push_back( eachMinMax );

<<<<<<< HEAD
  m_minmax[ROIName] = currentMinMaxVector;
=======
    // 
    // better do here
    typedef itk::LabelStatisticsImageFilter<WorkingImageType, BinaryImageType> StatisticCalculatorType;
    StatisticCalculatorType::Pointer statisticCalculator = StatisticCalculatorType::New();

    statisticCalculator->SetInput( *eachTypeOfImage );
    statisticCalculator->SetLabelInput( binaryImage );

    statisticCalculator->Update();
    currentROIParameter[ "Minimum" ] =  statisticCalculator->GetMinimum( defaultLabel );
    currentROIParameter[ "Maximum" ] =  statisticCalculator->GetMaximum( defaultLabel );
    currentROIParameter[ "Mean" ] =  statisticCalculator->GetMean( defaultLabel );
    currentROIParameter[ "Median" ] =  statisticCalculator->GetMedian( defaultLabel );

    statisticCalculator->SetUseHistograms( true);
    statisticCalculator->Update();
    StatisticCalculatorType::HistogramPointer histogram = statisticCalculator->GetHistogram( defaultLabel );
    currentROIParameter[ "Q_25" ] = histogram->Quantile( 0, 0.25 ); 
    currentROIParameter[ "Q_75" ] = histogram->Quantile( 0, 0.75 ); 
    currentROIParameter[ "Q_95" ] = histogram->Quantile( 0, 0.95 ); 
    currentROIParameter[ "Q_05" ] = histogram->Quantile( 0, 0.05 ); 
    }
>>>>>>> ac2e6bf... ENH: Normalization Parameter

  m_minmax[ROIName] = currentMinMaxVector;
  m_statistics[ ROIName ] = currentROIParameter ;
}

/** inline functions */
inline void
FeatureInputVector
::AddValueToElement( scalarType value, std::vector<scalarType>::iterator & elementIterator)
{
  try
    {
    *elementIterator = value;
    elementIterator++;
    }
  catch( ... )
    {
    std::string errorMsg = "Fail To Add Value To Element.";
    throw BRAINSCutExceptionStringHandler( errorMsg );
    }
  // std::cout<<value<<" ";
}

inline void
FeatureInputVector
::AddCandidateROIFeature( WorkingImageType::IndexType currentPixelIndex,
                          std::vector<scalarType>::iterator & elementIterator)
{
  for( DataSet::StringVectorType::const_iterator roiStringIt = m_roiIDsInOrder.begin();
       roiStringIt != m_roiIDsInOrder.end();
       ++roiStringIt )  // iterate each ROI candidates in order specified in "roi IDs in order"
    {
    WorkingPixelType currentProbability = m_candidateROIs.find( *roiStringIt )->second->GetPixel( currentPixelIndex );
    if( currentProbability > 0.0F +  FLOAT_TOLERANCE )
      {
      AddValueToElement( MAX, elementIterator );
      }
    else
      {
      AddValueToElement( MIN, elementIterator );
      }
    }
}

inline void
FeatureInputVector
::AddSpatialLocation( WorkingImageType::IndexType currentPixelIndex,
                      std::vector<scalarType>::iterator & elementIterator)
{
  // std::cout<<" (spatial) ";
  AddValueToElement( m_spatialLocations.find("rho")->second->GetPixel( currentPixelIndex ), elementIterator );
  AddValueToElement( m_spatialLocations.find("phi")->second->GetPixel( currentPixelIndex ), elementIterator );
  AddValueToElement( m_spatialLocations.find("theta")->second->GetPixel( currentPixelIndex ), elementIterator );
}

inline void
FeatureInputVector
::AddFeaturesImagesOfInterest(  std::string ROIName,
                                WorkingImageType::IndexType currentPixelIndex,
                                std::vector<scalarType>::iterator & elementIterator )
{
  for( WorkingImageVectorType::const_iterator wit = m_imagesOfInterestInOrder.begin();
       wit != m_imagesOfInterestInOrder.end();
       ++wit )
    {
    // std::cout<<"(IMG) ";
    AddFeaturesAlongGradient( ROIName, (*wit), currentPixelIndex, elementIterator);
    }
}

inline void
FeatureInputVector
::AddFeaturesAlongGradient( std::string ROIName,
                            const WorkingImagePointer& featureImage,
                            WorkingImageType::IndexType currentPixelIndex,
                            std::vector<scalarType>::iterator & elementIterator )
{
  const std::map<std::string, scalarType> delta = CalculateUnitDeltaAlongTheGradient( ROIName,
                                                                                      currentPixelIndex );
  itk::Point<WorkingPixelType, DIMENSION> CenterPhysicalPoint;
  featureImage->TransformIndexToPhysicalPoint( currentPixelIndex, CenterPhysicalPoint );

  m_imageInterpolator->SetInputImage( featureImage );
  for( float i = -m_gradientSize; i <= m_gradientSize; i = i + 1.0F )
    {
    // std::cout<<"(gradient at "<< i<<" )";
    itk::Point<WorkingPixelType, 3> gradientLocation = CenterPhysicalPoint;

    gradientLocation[0] = CenterPhysicalPoint[0] + i * (delta.find("deltaX")->second);
    gradientLocation[1] = CenterPhysicalPoint[1] + i * (delta.find("deltaY")->second);
    gradientLocation[2] = CenterPhysicalPoint[2] + i * (delta.find("deltaZ")->second);

    itk::ContinuousIndex<WorkingPixelType, DIMENSION> ContinuousIndexOfGradientLocation;

    featureImage->TransformPhysicalPointToContinuousIndex( gradientLocation, ContinuousIndexOfGradientLocation );

    AddValueToElement( static_cast<scalarType>( m_imageInterpolator->
                                                EvaluateAtContinuousIndex( ContinuousIndexOfGradientLocation ) ),
                       elementIterator );
    }
}

inline std::map<std::string, scalarType>
FeatureInputVector
::CalculateUnitDeltaAlongTheGradient( std::string ROIName,
                                      WorkingImageType::IndexType currentPixelIndex )
{
  WorkingPixelType deltaX = m_gradientOfROI.find( ROIName )->second->GetPixel( currentPixelIndex )[0];
  WorkingPixelType deltaY = m_gradientOfROI.find( ROIName )->second->GetPixel( currentPixelIndex )[1];
  WorkingPixelType deltaZ = m_gradientOfROI.find( ROIName )->second->GetPixel( currentPixelIndex )[2];

  const scalarType Length = vcl_sqrt(deltaX * deltaX + deltaY * deltaY + deltaZ * deltaZ);
  const scalarType inverseLength =  ( Length > 0.0F ) ? 1.0 / Length : 1;

  std::map<std::string, scalarType> unitGradient;
  unitGradient["deltaX"] = deltaX * inverseLength;
  unitGradient["deltaY"] = deltaY * inverseLength;
  unitGradient["deltaZ"] = deltaZ * inverseLength;

  return unitGradient;
}

/* Hash Generator from index */
hashKeyType
FeatureInputVector
::HashKeyFromIndex( const WorkingImageType::IndexType index )
{
  /*
   * calculating offset
   * hashValue = i[2] + i[1]*s[1] + i[0]*s[0]*s[1]
   */
  hashKeyType hashValue = 0; // TODO HACK REGINA: HashKeys should be unsigned!

  const unsigned int lastDimensionIndex = DIMENSION - 1;
  for( unsigned int i = 0; i < (lastDimensionIndex); i++ )
    {
    hashValue += index[i];
    hashValue *= ConstantHashIndexSize[i];
    }
  hashValue += index[lastDimensionIndex];
  return hashValue;
}

WorkingImageType::IndexType
FeatureInputVector
::HashIndexFromKey(const hashKeyType offSet) // TODO HACK REGINA: HashKeys should be unsigned!
{
  WorkingImageType::IndexType key;
  hashKeyType remainedOffSet = offSet; // TODO HACK REGINA: HashKeys should be unsigned!
  for( int d = DIMENSION - 1; d >= 0; d-- )
    {
    key[d] = remainedOffSet % ConstantHashIndexSize[d];
    remainedOffSet = remainedOffSet / ConstantHashIndexSize[d];
    }
  return key;
}

inline std::pair<scalarType, scalarType>
FeatureInputVector
::SetMinMaxOfSubject( BinaryImageType::Pointer & labelImage, const WorkingImagePointer& Image )
{
  typedef itk::LabelStatisticsImageFilter<WorkingImageType, BinaryImageType> StatisticCalculatorType;
  StatisticCalculatorType::Pointer statisticCalculator = StatisticCalculatorType::New();

  statisticCalculator->SetInput( Image );
  statisticCalculator->SetLabelInput( labelImage);

  statisticCalculator->Update();

  /*std::cout << " * Min : " << statisticCalculator->GetMinimum(1)
            << " * Max : " << statisticCalculator->GetMaximum(1)
            << std::endl; */
  return m_minmaxPairType( std::pair<scalarType, scalarType>( statisticCalculator->GetMinimum(1),
                                                            statisticCalculator->GetMaximum(1) ) );
}

void
FeatureInputVector
::NormalizationOfVector( InputVectorMapType& currentFeatureVector, std::string ROIName )
{
<<<<<<< HEAD
  m_minmaxPairVectorType currentMinmaxPairVector = m_minmax.find(ROIName)->second;
=======
  minmaxPairVectorType currentMinmaxPairVector = m_minmax.find(ROIName)->second;
>>>>>>> ac2e6bf... ENH: Normalization Parameter

  for( InputVectorMapType::iterator eachInputVector = currentFeatureVector.begin();
       eachInputVector != currentFeatureVector.end();
       ++eachInputVector )
    {
    InputVectorType::iterator featureElementIterator = (eachInputVector->second).begin();
    featureElementIterator += (m_roiIDsInOrder.size() + m_spatialLocations.size() );
    for( m_minmaxPairVectorType::const_iterator m_minmaxIt = currentMinmaxPairVector.begin();
         m_minmaxIt != currentMinmaxPairVector.end();
         ++m_minmaxIt )
      {
      for(  float i = -m_gradientSize; i <= m_gradientSize; i = i + 1.0F )
        {
        scalarType normalizedValue = ( *featureElementIterator - m_minmaxIt->first );
        normalizedValue = normalizedValue / ( m_minmaxIt->second - m_minmaxIt->first );
        *featureElementIterator = normalizedValue;
        featureElementIterator++;
        }
      }
    }
}
