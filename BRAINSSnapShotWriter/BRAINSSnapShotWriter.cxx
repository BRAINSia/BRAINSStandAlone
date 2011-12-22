#include "BRAINSCommonLib.h"

#include "itkImageFileReader.h"
#include "itkImageFileWriter.h"
#include "itkImageRegionIterator.h"
#include "itkTestingExtractSliceImageFilter.h"
#include "itkCastImageFilter.h"
#include "itkRescaleIntensityImageFilter.h"
#include "itkScalarToRGBColormapImageFilter.h"
#include "itkTileImageFilter.h"
#include "itkComposeRGBImageFilter.h"

#include "BRAINSSnapShotWriterCLP.h"
/* 
 * template reading function 
 */
template <class TStringVectorType, // input parameter type
          class TReaderType,       // reader type
          class TImageVectorType > // return type
TImageVectorType ReadImageVolumes( TStringVectorType filenameVector )
{
  typedef typename TReaderType::Pointer                   ReaderPointer;
  typedef typename TReaderType::OutputImageType::Pointer  OutputImagePointerType;

  TImageVectorType imageVector;

  for( unsigned int i = 0; i<filenameVector.size(); i++ )
    {
    std::cout<< "Reading image " << i + 1 << ": " << filenameVector[i] << "...\n";
    
    ReaderPointer reader = TReaderType::New();
    reader->SetFileName( filenameVector[i].c_str() );

    try
      {
      reader->Update();
      }
    catch( ... )
      {
      std::cout<< "ERROR:  Could not read image " << filenameVector[i] << "." << std::endl ;
      exit(EXIT_FAILURE);
      }

    OutputImagePointerType image = reader->GetOutput();

    imageVector.push_back( image );
    }

  return TImageVectorType( imageVector );
}
/*
 * extract slices
 */
template <class TInputImageType,
          class TOutputImageType>
typename TOutputImageType::Pointer 
ExtractSlice( typename TInputImageType::Pointer inputImage, 
              int sliceNumber)
{
  /* extract 2D plain */
  typedef itk::Testing::ExtractSliceImageFilter< TInputImageType, 
                                                 TOutputImageType> ExtractVolumeFilterType;

  typename ExtractVolumeFilterType::Pointer extractVolumeFilter = ExtractVolumeFilterType::New();

  typename TInputImageType::RegionType region=inputImage->GetLargestPossibleRegion();
  
  typename TInputImageType::SizeType size = region.GetSize();
  size[2] = 0;
  
  typename TInputImageType::IndexType start = region.GetIndex();
  start[2]=sliceNumber;

  typename TInputImageType::RegionType outputRegion;
  outputRegion.SetSize( size );
  outputRegion.SetIndex( start );

  extractVolumeFilter->SetExtractionRegion( outputRegion );
  extractVolumeFilter->SetInput( inputImage );
  extractVolumeFilter->Update();

  typename TOutputImageType::Pointer outputImage = extractVolumeFilter->GetOutput();
  return outputImage;
}

/* scaling between 0-255 */
template <class TInputImage, class TOutputImage>
typename TOutputImage::Pointer
Rescale( const typename TInputImage::Pointer inputImage, 
         const int min, 
         const int max)
{
  typedef itk::RescaleIntensityImageFilter< TInputImage, 
                                            TInputImage> RescaleFilterType;

  typename RescaleFilterType::Pointer rescaler = RescaleFilterType::New();

  rescaler->SetInput( inputImage );
  rescaler->SetOutputMinimum( min );
  rescaler->SetOutputMaximum( max );

  typedef typename itk::CastImageFilter< TInputImage, 
                                         TOutputImage> CastingFilterType;

  typename CastingFilterType::Pointer caster = CastingFilterType::New();
  caster->SetInput( rescaler->GetOutput() );
  caster->Update();

  typename TOutputImage::Pointer outputImage = caster->GetOutput();

  return outputImage;
}
/*
 * main
 */

int
main(int argc, char * *argv)
{
  PARSE_ARGS;

  if( inputVolumes.empty() )
    {
    std::cout<<"Input image volume is required "
             <<std::endl;
    exit(EXIT_FAILURE);
    }
  const unsigned int numberOfImgs = inputVolumes.size();
  const unsigned int numberOfBnrs = inputBinaryVolumes.size();

  /* type definition */
  typedef itk::Image< double, 3 >        Image3DVolumeType;
  typedef itk::Image< double, 2 >        Image2DVolumeType;
  typedef itk::Image< unsigned char, 3 > Image3DBinaryType;



  typedef std::vector< std::string >       ImageFilenameVectorType;
  typedef std::vector< Image3DVolumeType::Pointer > Image3DVolumeVectorType;
  typedef std::vector< Image3DBinaryType::Pointer > Image3DBinaryVectorType;

  typedef itk::ImageFileReader< Image3DVolumeType > Image3DVolumeReaderType;
  typedef Image3DVolumeReaderType::Pointer          Image3DVolumeReaderPointer;

  typedef itk::ImageFileReader< Image3DBinaryType > Image3DBinaryReaderType;
  typedef Image3DBinaryReaderType::Pointer          Image3DBinaryReaderPointer;

  typedef itk::Image< unsigned char, 2> OutputGreyImageType;

  typedef itk::RGBPixel< unsigned char> RGBPixelType;
  typedef itk::Image< RGBPixelType, 2> OutputRGBImageType;

  typedef itk::ScalarToRGBColormapImageFilter< OutputGreyImageType,
                                               OutputRGBImageType > RGBFilterType;
  /* read in image volumes */
  Image3DVolumeVectorType image3DVolumes = ReadImageVolumes< ImageFilenameVectorType,
                                                             Image3DVolumeReaderType,
                                                             Image3DVolumeVectorType >
                                                               ( inputVolumes );

  /* read in binary volumes */
  Image3DBinaryVectorType image3DBinaries = ReadImageVolumes< ImageFilenameVectorType,
                                                             Image3DBinaryReaderType,
                                                             Image3DBinaryVectorType >
                                                               ( inputBinaryVolumes );

  /* extract slices */
  typedef std::vector< OutputGreyImageType::Pointer > OutputGreyImageVectorType;

  OutputGreyImageVectorType imageSlices;

  for( unsigned int i=0; i<numberOfImgs; i++)
    {
    Image3DVolumeType::Pointer current3DImage=image3DVolumes.back();
    Image2DVolumeType::Pointer imageSlice=
      ExtractSlice< Image3DVolumeType, Image2DVolumeType > ( current3DImage, 
                                                             inputSliceNumber );

    OutputGreyImageType::Pointer outputGreyImage = 
      Rescale< Image2DVolumeType,OutputGreyImageType>( imageSlice, 0, 255 );

    imageSlices.push_back( outputGreyImage );

    image3DVolumes.pop_back();
    }

  OutputGreyImageVectorType binarySlices;

  for( unsigned int i=0; i<numberOfBnrs; i++)
    {
    Image3DBinaryType::Pointer current3DBinary=image3DBinaries.back();
    Image2DVolumeType::Pointer binarySlice=
      ExtractSlice< Image3DBinaryType, Image2DVolumeType > ( current3DBinary, 
                                                             inputSliceNumber );

    OutputGreyImageType::Pointer outputGreyBinary= 
      Rescale< Image2DVolumeType,OutputGreyImageType>( binarySlice, 0,200); 

    binarySlices.push_back( outputGreyBinary );
    image3DBinaries.pop_back();
    }
  
  /* compose color image */
  typedef itk::ComposeRGBImageFilter< OutputGreyImageType,
                                      OutputRGBImageType > RGBComposeFilter;

  typedef std::vector< OutputRGBImageType::Pointer > OutputRGBImageVectorType;
  OutputRGBImageVectorType rgbSlices;
  for( unsigned int i=0; i<numberOfImgs; i++)
    {
    RGBComposeFilter::Pointer rgbComposer = RGBComposeFilter::New();

    rgbComposer->SetInput1( binarySlices[0] );
    rgbComposer->SetInput3( imageSlices[i] );
    rgbComposer->SetInput2( imageSlices[i] );


    try
      {
      std::cout<<"before update"<<std::endl;
      rgbComposer->Update();
      std::cout<<"after update"<<std::endl;
      }
    catch( itk::ExceptionObject& e  )
      {
      std::cout<< "ERROR:  Could not update image." << std::endl ;
      std::cout<< "ERROR:  "<<e.what()<<std::endl;
      exit(EXIT_FAILURE);
      }

    std::cout<<"before assigning"<<std::endl;
    rgbSlices.push_back( rgbComposer->GetOutput() );
    std::cout<<"after assigning"<<std::endl;

    }

  /* tile the images */
  typedef itk::TileImageFilter< OutputRGBImageType, OutputRGBImageType> TileFilterType;

  TileFilterType::Pointer tileFilter = TileFilterType::New();

  itk::FixedArray< unsigned int, 2 > layout;

  layout[0]=numberOfImgs;
  layout[1]=0;//inputPlaneDirection.size();

  tileFilter->SetLayout( layout );
  tileFilter->SetDefaultPixelValue( 128 );
  for( unsigned int i=0; i<numberOfImgs; i++)
    {
    OutputRGBImageType::Pointer img = rgbSlices[i];
    tileFilter->SetInput( i, img );
    }

  /* write out 2D image */
  typedef itk::ImageFileWriter< OutputRGBImageType > RGBFileWriterType;

  RGBFileWriterType::Pointer rgbFileWriter= RGBFileWriterType::New();

  rgbFileWriter->SetInput( tileFilter->GetOutput() );
  rgbFileWriter->SetFileName( outputFilename );

  try
    {
      std::cout<<"before writer update"<<std::endl;
      rgbFileWriter->Update();
      std::cout<<"after writer update"<<std::endl;
    }
  catch( itk::ExceptionObject& e  )
    {
    std::cout<< "ERROR:  Could not write image." << std::endl ;
    std::cout<< "ERROR:  "<<e.what()<<std::endl;
    exit(EXIT_FAILURE);
    }
  return EXIT_SUCCESS;
}
