// Contributors: Eun Young (Regina) Kim and Joy Matsui
// Edit binary mask based on given landmark and direction.
//
#include "Slicer3LandmarkIO.h"
#include "itkImageFileReader.h"
#include "itkImageDuplicator.h"
#include "itkImageRegionIterator.h"
#include "itkImageFileWriter.h"
#include "vcl_algorithm.h"

#include "BinaryMaskEditorBasedOnLandmarksCLP.h"

class ThreeLandmarksForPlane
{
  // The definition depends on Slicer3LandmarkIO.
  // Point type is simply itk::Pointe<double, 3> 
  public:
  PointType A;
  PointType B;
  PointType C;

  
  typedef itk::Point<double, 3>    VectorType;

  void SetNormal()
  {
  // Determine AB and AC vector components
  VectorType AB;
  AB[ 0 ] = B[ 0 ] - A[ 0 ];
  AB[ 1 ] = B[ 1 ] - A[ 1 ];
  AB[ 2 ] = B[ 2 ] - A[ 2 ];
  std::cout<<"AB::: [" 
           << AB[0] << ", "
           << AB[1] << ", "
           << AB[2] << " ]"
           <<std::endl;
  
  VectorType AC;
  AC[ 0 ] = C[ 0 ] - A[ 0 ];
  AC[ 1 ] = C[ 1 ] - A[ 1 ]; 
  AC[ 2 ] = C[ 2 ] - A[ 2 ];
  std::cout<<"AC::: [" 
           << AC[0] << ", "
           << AC[1] << ", "
           << AC[2] << " ]"
           <<std::endl;

  // Find cross product components

  normal[ 0 ] = ( AB[ 1 ] * AC[ 2 ] ) - ( AC[ 1 ] * AB[ 2 ] );
  normal[ 1 ] = -1 * ( ( AB[ 0 ] * AC[ 2 ] ) - ( AC[ 0 ] * AB[ 2 ] ) );
  normal[ 2 ] = ( AB[ 0 ] * AC[ 1 ] ) - ( AC[ 0 ] * AB[ 1 ] );

  double magnitude = vcl_sqrt( normal[0] * normal[0] +
                               normal[1] * normal[1] +
                               normal[2] * normal[2] );
    
  std::cout<<"Normal::: Before Norm[" 
           << normal[0] << ", "
           << normal[1] << ", "
           << normal[2] << " ]"
           <<std::endl;
  normal[ 0 ] = normal[ 0 ] / magnitude;
  normal[ 1 ] = normal[ 1 ] / magnitude;
  normal[ 2 ] = normal[ 2 ] / magnitude;

  if( normal[ 0 ] < 0.0F ) //Fix X-axis to the positive for consistency
    {
    normal[ 0 ] = - normal[ 0 ] ;
    normal[ 1 ] = - normal[ 1 ] ;
    normal[ 2 ] = - normal[ 2 ] ;
    }
  std::cout<<"Normal:::  After Norm[" 
           << normal[0] << ", "
           << normal[1] << ", "
           << normal[2] << " ]"
           <<std::endl;
  }

  double 
  GetRelativeLocationToPlane( PointType x )
  {
    double answer =
      normal[0] * ( A[0] - x[0] )
      + normal[1] * ( A[1] - x[1] )
       +  normal[2] * ( A[2] - x[2] ) ;
    return answer;
  }

  VectorType GetNormal()
    {
    return normal;
    }

  private:
  VectorType normal;
  
};

// ------------------------------------------------------------------------ // 
template<class TImageType>
void
CutBinaryVolumeByPlaneWithDirection( typename TImageType::Pointer * _imageVolume,
                                     ThreeLandmarksForPlane * currentPlane, 
                                     const std::string direction )
{
  typedef itk::ImageRegionIterator< TImageType > ImageRegionIteratorType;
  ImageRegionIteratorType it(  *_imageVolume, 
                              (*_imageVolume)->GetRequestedRegion() );
  std::cout<<__LINE__<<"::"<<__FILE__<<std::endl;

  for( it.GoToBegin(); !it.IsAtEnd(); ++it)
    {
    PointType currentPhysicalLocation;
    (*_imageVolume)->TransformIndexToPhysicalPoint( it.GetIndex(), currentPhysicalLocation );

    if( direction == "true" && 
        (*currentPlane).GetRelativeLocationToPlane( currentPhysicalLocation ) > 0.0F )
      { 
      it.Set( 0.0F ); 
      }
    else if( direction =="false" &&
        (*currentPlane).GetRelativeLocationToPlane( currentPhysicalLocation ) < 0.0F ){ it.Set( 0.0F ); }
    }

}
// ------------------------------------------------------------------------ // 
template <class TImageType>
void
CutBinaryVolumeByPointWithDirection( typename TImageType::Pointer * _imageVolume, 
                                     const PointType _landmark,
                                     const std::string _direction )
{
  
  // set directional constant for convenient programming
  //
  enum DIRECTION{
    ANTERIOR, POSTERIOR, LEFT, RIGHT, SUPERIOR, INFERIOR } myDirection;

  if( _direction == "ANTERIOR" ) { myDirection = ANTERIOR; }
  else if( _direction == "POSTERIOR" ) { myDirection = POSTERIOR; }
  else if( _direction == "LEFT" ) { myDirection = LEFT; }
  else if( _direction == "RIGHT" ) { myDirection = RIGHT; }
  else if( _direction == "SUPERIOR" ) { myDirection = SUPERIOR; }
  else if( _direction == "INFERIOR" ) { myDirection = INFERIOR; }

  typedef itk::ImageRegionIterator< TImageType > ImageRegionIteratorType;
  ImageRegionIteratorType it(  *_imageVolume, 
                              (*_imageVolume)->GetRequestedRegion() );
  std::cout<<__LINE__<<"::"<<__FILE__<<std::endl;

  for( it.GoToBegin(); !it.IsAtEnd(); ++it)
    {
    PointType currentPhysicalLocation;
    (*_imageVolume)->TransformIndexToPhysicalPoint( it.GetIndex(), currentPhysicalLocation );
    switch( myDirection )
      {
        case RIGHT:
          if( currentPhysicalLocation[0] > _landmark[0] ){ it.Set( 0.0F ); }; // RIGHT
          break;
        case LEFT:
          if( currentPhysicalLocation[0] < _landmark[0] ){ it.Set( 0.0F ); }; // LEFT
          break;
        case ANTERIOR:
          if( currentPhysicalLocation[1] > _landmark[1] ){ it.Set( 0.0F ); }; // ANTERIOR
          break;
        case POSTERIOR:
          if( currentPhysicalLocation[1] < _landmark[1] ){ it.Set( 0.0F ); }; //POSTERIOR
          break;
        case INFERIOR:
          if( currentPhysicalLocation[2] > _landmark[2] ){ it.Set( 0.0F ); }; // INFERIOR
          break;
        case SUPERIOR:
          if( currentPhysicalLocation[2] < _landmark[2] ){ it.Set( 0.0F ); }; //SUPERIOR
          break;
      }
    }
}

int main( int argc, char * argv[] )
{
  PARSE_ARGS;

  // check input 
  //
  if( inputBinaryVolume.empty() ||
      inputLandmarksFilename.empty()
       )
    {
    std::cout<<"Input Landmarks Filename ( inputLandmarkFilename ) and"
             <<"input binary volume ( inputBinaryVolume ) "
             <<" are necessary."
             <<std::endl;
    exit(EXIT_FAILURE);
    }
  if( inputLandmarkNames.size() != setCutDirectionForLandmark.size() )
    {
    std::cout<<" Size should match between inputLandmarkNames and"
             <<" setCutDirectionForLandmark but "
             << inputLandmarkNames.size() << " != " 
             << setCutDirectionForLandmark.size() <<std::endl;
    }

  // read inputBinaryVolume
  //
  typedef unsigned char PixelType;
  const unsigned int Dimension = 3;

  typedef itk::Image< PixelType, Dimension > ImageType;

  typedef itk::ImageFileReader< ImageType > ImageReaderType;

  ImageReaderType::Pointer imageReader = ImageReaderType::New();
  imageReader->SetFileName( inputBinaryVolume );
  imageReader->Update();

  ImageType::Pointer inputVolume = imageReader->GetOutput();

  // read landmark file in
  //
  std::cout << "Reading: " 
            << inputLandmarksFilename << std::endl;
  LandmarksMapType landmarksSet = ReadSlicer3toITKLmk( inputLandmarksFilename );

  // duplicate image
  //
  typedef itk::ImageDuplicator< ImageType > ImageDuplicatorType;
  ImageDuplicatorType::Pointer duplicator = ImageDuplicatorType::New();
  duplicator->SetInputImage( inputVolume );
  duplicator->Update();

  ImageType::Pointer outputVolume =  duplicator->GetOutput();

  // cut by landmarks
  //
  typedef std::vector<std::string>::const_iterator stringVectorIteratorType;

  for( stringVectorIteratorType ldmkIt = inputLandmarkNames.begin(),
                                dircIt = setCutDirectionForLandmark.begin();
       ldmkIt < inputLandmarkNames.end();
       ldmkIt++, dircIt++ )
    {
    if( landmarksSet.find( *ldmkIt ) == landmarksSet.end() )
      {
      std::cerr << "ERROR: Landmark not found: " << *ldmkIt << std::endl; 
      std::exit( EXIT_FAILURE );
      }

    PointType currentLdmk = landmarksSet.find( *ldmkIt ) -> second;
    std::cout<<"currentLdmk:: "<< *ldmkIt <<"::"
             << currentLdmk[0] <<", "
             << currentLdmk[1] <<", "
             << currentLdmk[2] << std::endl;

    CutBinaryVolumeByPointWithDirection< ImageType >( & outputVolume, currentLdmk , *dircIt );
    }

  // cut by plane defined by three landmarks
  //

  // string vector to read in a vector of three elements.
  // ex) (LE, RE, PC) --> plane for left and right eyes with posterior commissure.
  typedef std::vector< std::string > LandMarkForPlaneType;

  // a set of plane description
  // ex) 1: (LE, RE, PC)
  //     2: (AC, PC, LE)
  //     3: ....
  typedef std::vector< ThreeLandmarksForPlane > PlaneLandmarkSetType;
  typedef PlaneLandmarkSetType::const_iterator PlaneLandmarkSetIteratorType;

  PlaneLandmarkSetType myLandmarkSetForPlanes;

  if( inputLandmarkNamesForObliquePlane.size() % 3 != 0)
    {
    std::cerr << "ERROR: Landmarks set for plane has to given as a multiple of three: " 
              << inputLandmarkNamesForObliquePlane.size() << std::endl;
    std::exit( EXIT_FAILURE );
    }
  stringVectorIteratorType planeDir = setCutDirectionForObliquePlane.begin();

  if( inputLandmarkNamesForObliquePlane.size() != 0 )
  {
    if( inputLandmarkNamesForObliquePlane.size() !=
        3*setCutDirectionForObliquePlane.size() )
      {
      std::cout<<"Directional information for plane has to be match "
               <<"to the number of plane descriptions.("
               <<inputLandmarkNamesForObliquePlane.size() <<"!=" 
               <<setCutDirectionForObliquePlane.size()<< ")"
               <<std::endl;
      return( EXIT_FAILURE );
      }
  }
                
  for( LandMarkForPlaneType::const_iterator  inputLdmrIt= inputLandmarkNamesForObliquePlane.begin();
       inputLdmrIt< inputLandmarkNamesForObliquePlane.end();
       inputLdmrIt++ )
    {
    ThreeLandmarksForPlane currentPlane;

    for( unsigned int it = 0; it < 3; it++  ) // make sure we have only three ldmr per plane
      {
      if( landmarksSet.find( *inputLdmrIt ) ==  landmarksSet.end() )
        {
        std::cerr << "ERROR: Landmark not found: " <<*inputLdmrIt << std::endl;
        std::exit( EXIT_FAILURE );
        }
      PointType currentLandmark = landmarksSet.find( *inputLdmrIt ) -> second;
      std::cout<<"currentLandmark:: "<< *inputLdmrIt<<"::"
               << currentLandmark[0] <<", "
               << currentLandmark[1] <<", "
               << currentLandmark[2] << std::endl;
      if( it == 0 ) { currentPlane.A = currentLandmark; }
      if( it == 1 ) { currentPlane.B = currentLandmark; }
      if( it == 2 ) { currentPlane.C = currentLandmark; }

      inputLdmrIt++;
      }
    currentPlane.SetNormal();
    myLandmarkSetForPlanes.push_back(currentPlane);

    CutBinaryVolumeByPlaneWithDirection<ImageType>( & outputVolume, &currentPlane, *planeDir );
    ++planeDir;
    }

  //write output volume
  //

  typedef itk::ImageFileWriter< ImageType > OutputImageWriterType;
  OutputImageWriterType::Pointer writer = OutputImageWriterType::New();

  writer->SetInput( outputVolume );
  writer->SetFileName( outputBinaryVolume );
  writer->Update();

  return( EXIT_SUCCESS );
}
