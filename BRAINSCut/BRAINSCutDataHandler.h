#ifndef BRAINSCutDataHandler_h
#define BRAINSCutDataHandler_h

#include "BRAINSCutConfiguration.h"

#include "NeuralParams.h"
#include "itkIO.h"

#include "GenericTransformImage.h"
/** include opencv library */
#include "ml.h"
#include "cxcore.h"
#include "cv.h"

typedef CvANN_MLP_Revision OpenCVMLPType;
#include <stdint.h>

/** Training data set definition */

typedef float   scalarType;
typedef CvMat * matrixType;

struct pairedTrainingSetType
  {
  matrixType pairedInput;
  matrixType pairedOutput;
  matrixType pairedOutputRF;
  unsigned int size;
  };

/*
 * constant
 */
static const float        HundredPercentValue = 1.0F;
static const float        ZeroPercentValue = 0.0F;
static const unsigned int LineGuardSize = 1;
static const scalarType   LineGuard = 1234567.0;
static const float        FLOAT_TOLERANCE = 0.01;

/*
* Image Definitions
*/
const unsigned char DIMENSION = 3;

typedef double                                 ReadInPixelType;
typedef itk::Image<ReadInPixelType, DIMENSION> ReadInImageType;
typedef ReadInImageType::Pointer               ReadInImagePointer;

typedef float                                   WorkingPixelType;
typedef itk::Image<WorkingPixelType, DIMENSION> WorkingImageType;
typedef WorkingImageType::Pointer               WorkingImagePointer;

typedef std::vector<WorkingImagePointer> WorkingImageVectorType;

/* Deformations */
typedef float                                         DeformationScalarType;
typedef itk::Vector<DeformationScalarType, DIMENSION> DeformationPixelType;
typedef itk::Image<DeformationPixelType, DIMENSION>   DisplacementFieldType;

typedef WorkingImageType::IndexType WorkingIndexType;

typedef std::vector<WorkingPixelType> InputVectorType;
typedef std::vector<WorkingPixelType> OutputVectorType;

typedef std::map<int, InputVectorType>  InputVectorMapType; // < index ,feature vector > pair
typedef std::map<int, OutputVectorType> OutputVectorMapType;
typedef std::map<int, scalarType>       PredictValueMapType;

const WorkingImageType::IndexType ConstantHashIndexSize = {{255, 255, 255}};
/*
 * BRAINSCut Primary Class Starts here
 */

class BRAINSCutDataHandler : public BRAINSCutConfiguration
{
public:
  BRAINSCutDataHandler(){};
  BRAINSCutDataHandler(std::string modelConfigurationFilenameFilename);

  void SetNetConfiguration();

  BRAINSCutConfiguration * GetNetConfiguration();

  void SetNetConfigurationFilename(const std::string filename);

  std::string GetNetConfigurationFilename();

  /* Atlas(template) related */
  void SetAtlasDataSet();
  void SetAtlasImage();

  void SetRegionsOfInterestFromNetConfiguration();
  void SetRegistrationParametersFromNetConfiguration();
  void SetRhoPhiThetaFromNetConfiguration();
  void SetANNModelConfiguration();
  void SetGradientSizeFromNetConfiguration();

  /** Model file name **/
  std::string GetModelBaseName();
  void SetANNModelFilenameAtIteration( const int iteration);
  std::string GetANNModelFilenameAtIteration( const int iteration);


  std::string GetRFModelFilename( int depth,int NTrees);

  WorkingImagePointer 
    ReadImageByFilename( const std::string  filename );

  WorkingImagePointer 
    WarpImageByFilenames( const std::string & deformationFilename, 
                          const std::string & inputFilename,
                          const std::string & referenceFilename );

  /** Get Function */
  DataSet::StringVectorType GetROIIDsInOrder();

  void   GetDeformedSpatialLocationImages( 
                  std::map<std::string, WorkingImagePointer>& warpedSpatialLocationImages,
                  DataSet& subject );
  void GetImagesOfSubjectInOrder( WorkingImageVectorType& subjectImageList, DataSet& subject);
  void GetDeformedROIs( std::map<std::string, 
                        WorkingImagePointer>& deformedROIs, DataSet& subject );
  bool GetNormalizationFromNetConfiguration();
  std::string           GetAtlasFilename();
  std::string           GetAtlasBinaryFilename();
  int                   GetROIAutoDilateSize();
  unsigned int          GetROICount();
  WorkingImagePointer   GetAtlasImage();
  ProbabilityMapList *  GetROIDataList();
  DataSet *             GetAtlasDataSet()



  /* Displacement Functions */
  DisplacementFieldType::Pointer GetDeformationField( std::string filename);

  GenericTransformType::Pointer GetGenericTransform( std::string filename);

  std::string GetAtlasToSubjectRegistrationFilename( DataSet& subject);
  std::string GetSubjectToAtlasRegistrationFilename( DataSet& subject);

  /* common functions */
  WorkingImagePointer SmoothImage( const WorkingImagePointer image, const float GaussianValue);

protected:
  NeuralParams *   annModelConfiguration;

  /** atlas data set*/
  DataSet *           atlasDataSet;
  std::string         atlasFilename;
  std::string         atlasBinaryFilename;
  WorkingImagePointer atlasImage;

  /**ProbabilityMaps*/
  ProbabilityMapList *      roiDataList;
  DataSet::StringVectorType roiIDsInOrder;;
  unsigned int              roiCount;

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

  /** model name **/
  std::string ANNModelFilename;
  std::string RandomForestModelFilename;
  
private:
  WorkingImageType GetDeformedImage( WorkingImageType image);

  std::string NetConfigurationFilename;

};
#endif
