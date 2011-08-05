#ifndef _VDemonsRegistrator_txx
#define _VDemonsRegistrator_txx

#include <sstream>
#include <string>
#include <vector>

#include "VDemonsRegistrator.h"
#include "itkCommand.h"
#include "ApplyField.h"
#include "itkStatisticsImageFilter.h"
#include "itkMetaImageIO.h"
#include "itkMetaDataObject.h"
#include "itkIOCommon.h"
#include "itkVectorIndexSelectionCastImageFilter.h"
#include "itkCheckerBoardImageFilter.h"
#include "itkIO.h"

#include "itkImageFileWriter.h"

#include "itkVectorMultiResolutionPDEDeformableRegistration.h"
#include "itkDiffeomorphicDemonsRegistrationFilter.h"
#include "GenericTransformImage.h"
#include "itkVectorLinearInterpolateNearestNeighborExtrapolateImageFunction.h"
#include "itkImageToVectorImageFilter.h"
#include "itkMultiplyByConstantImageFilter.h"

namespace itk
{
/*This function writes the displacement fields of the Deformation.*/
template <
  class TRealImage,
  class TOutputImage,
  class TFieldValue>
void VDemonsRegistrator<TRealImage, TOutputImage,
                        TFieldValue>::WriteDisplacementComponents()
{
  m_DefaultPixelValue = NumericTraits<PixelType>::One;

  // we use the vector index selection filter to break the deformation field
  // into x,y,z components.
  typedef itk::Image<FieldValueType,
                     3>                  ComponentImageType;
  typedef itk::VectorIndexSelectionCastImageFilter<TDeformationField,
                                                   ComponentImageType> ComponentFilterType;

  std::string CurrentComponentFilename;
  try
    {
    char ext[3][14] = { "_xdisp.nii.gz", "_ydisp.nii.gz", "_zdisp.nii.gz" };

    typename ComponentFilterType::Pointer myComponentFilter =
      ComponentFilterType::New();
    myComponentFilter->SetInput(m_DeformationField);
    for( unsigned int extiter = 0; extiter < 3; extiter++ )
      {
      CurrentComponentFilename = m_DisplacementBaseName + ext[extiter];
      if( this->GetOutDebug() )
        {
        std::cout << "Writing Transform Image: "
                  << CurrentComponentFilename << std::endl;
        }

      myComponentFilter->SetIndex(extiter);

      typename ComponentImageType::Pointer DisplacementComponentImagePtr =
        myComponentFilter->GetOutput();

      itkUtil::WriteImage<ComponentImageType>(DisplacementComponentImagePtr,
                                              CurrentComponentFilename);
      }
    }
  catch( itk::ExceptionObject & e )
    {
    std::cerr << "exception in file Displacement File Writer("
              << CurrentComponentFilename << ")" << std::endl;
    std::cerr << e.GetDescription() << std::endl;
    std::cerr << e.GetLocation() << std::endl;
    exit(-1);
    }
}

/*Constructor to initialize the parameters.*/
template <
  class TRealImage,
  class TOutputImage,
  class TFieldValue>
VDemonsRegistrator<TRealImage, TOutputImage, TFieldValue>::VDemonsRegistrator()
{
  // Images need to be set from the outside
  m_VectorFixedImage = VectorImageType::New();
  m_VectorMovingImage = VectorImageType::New();
  m_DeformationField = NULL;

  // Set up internal registrator with default components
  m_FixedImagePyramid = FixedImagePyramidType::New();
  m_FixedImagePyramid->UseShrinkImageFilterOff();
  m_MovingImagePyramid = MovingImagePyramidType::New();
  m_MovingImagePyramid->UseShrinkImageFilterOff();
  m_Registration = RegistrationType::New();
  m_VectorRegistration = VectorRegistrationType::New();

  m_Registration->SetFixedImagePyramid(m_FixedImagePyramid);
  m_Registration->SetMovingImagePyramid(m_MovingImagePyramid);

  m_VectorRegistration->SetFixedImagePyramid(m_FixedImagePyramid);
  m_VectorRegistration->SetMovingImagePyramid(m_MovingImagePyramid);

  m_DefaultPixelValue =  NumericTraits<typename RealImageType::PixelType>::Zero;
  // Setup an registration observer
  typedef SimpleMemberCommand<Self> CommandType;
  typename CommandType::Pointer command = CommandType::New();
  command->SetCallbackFunction(this, &Self::StartNewLevel);

  m_Tag = m_Registration->AddObserver(IterationEvent(), command);
  m_VectorTag = m_VectorRegistration->AddObserver(IterationEvent(), command);

  typedef VectorLinearInterpolateNearestNeighborExtrapolateImageFunction<
    TDeformationField, double> FieldInterpolatorType;

  typename FieldInterpolatorType::Pointer VectorInterpolator =
    FieldInterpolatorType::New();

  m_Registration->GetFieldExpander()->SetInterpolator(VectorInterpolator);
  m_VectorRegistration->GetFieldExpander()->SetInterpolator(VectorInterpolator);

  // Default parameters
  m_NumberOfLevels = 1;

  m_FixedImageShrinkFactors.Fill(1);
  m_MovingImageShrinkFactors.Fill(1);

  m_NumberOfIterations = UnsignedIntArray(1);
  m_NumberOfIterations.Fill(10);
  m_WarpedImageName = "none";
  m_DisplacementBaseName = "none";
  m_CheckerBoardFilename = "none";
  m_DeformationFieldOutputName = "none";
  m_CheckerBoardPattern.Fill(4);
  m_OutNormalized  = "OFF";

  m_UseHistogramMatching = false;
  m_OutDebug = false;

  m_InitialDeformationField = NULL;
  m_InterpolationMode = "Linear";
}

template <
  class TRealImage,
  class TOutputImage,
  class TFieldValue>
VDemonsRegistrator<TRealImage, TOutputImage, TFieldValue>::~VDemonsRegistrator()
{
  if( m_Tag )
    {
    m_Registration->RemoveObserver(m_Tag);
    }
}

/*Perform the registration of preprocessed images.*/
template <
  typename TRealImage,
  class TOutputImage,
  class TFieldValue>
void VDemonsRegistrator<TRealImage, TOutputImage, TFieldValue>::Execute()
{
  // Setup the registrator

  typedef itk::MultiplyByConstantImageFilter<RealImageType, float,
                                             RealImageType> MultiplyByConstantImageType;

  if( m_FixedImage.size() > 1 )
    {
    typedef itk::ImageToVectorImageFilter<RealImageType> ImageToVectorImageType;
    typename ImageToVectorImageType::Pointer fixedVectorImage =
      ImageToVectorImageType::New();
    typename ImageToVectorImageType::Pointer movingVectorImage =
      ImageToVectorImageType::New();
    for( unsigned int i = 0; i < m_FixedImage.size(); ++i )
      {
      typename MultiplyByConstantImageType::Pointer multi_FixedImageConstant =
        MultiplyByConstantImageType::New();
      multi_FixedImageConstant->SetInput(m_FixedImage[i]);
      multi_FixedImageConstant->SetConstant(m_WeightFactors[i]);
      multi_FixedImageConstant->Update();

      typename MultiplyByConstantImageType::Pointer multi_MovingImageConstant =
        MultiplyByConstantImageType::New();
      multi_MovingImageConstant->SetInput(m_MovingImage[i]);
      multi_MovingImageConstant->SetConstant(m_WeightFactors[i]);
      multi_MovingImageConstant->Update();
      fixedVectorImage->SetNthInput( i, multi_FixedImageConstant->GetOutput() );
      movingVectorImage->SetNthInput( i, multi_MovingImageConstant->GetOutput() );
      }

    try
      {
      fixedVectorImage->Update();
      movingVectorImage->Update();
      }
    catch( itk::ExceptionObject & err )
      {
      std::cout << "Caught an exception: " << std::endl;
      std::cout << err << " " << __FILE__ << " " << __LINE__ << std::endl;
      throw err;
      throw err;
      }
    catch( ... )
      {
      std::cout << "Caught a non-ITK exception " << __FILE__ << " "
                << __LINE__ << std::endl;
      }

    m_VectorFixedImage = fixedVectorImage->GetOutput();
    m_VectorMovingImage = movingVectorImage->GetOutput();

    m_VectorRegistration->SetFixedImage(m_VectorFixedImage);
    m_VectorRegistration->SetMovingImage(m_VectorMovingImage);

    m_VectorRegistration->SetNumberOfLevels(m_NumberOfLevels);
    m_VectorRegistration->SetNumberOfIterations(
      m_NumberOfIterations.data_block() );

    // Setup the initial deformation field
    if( this->m_InitialDeformationField.IsNotNull() )
      {
      m_VectorRegistration->SetInitialDeformationField(
        this->m_InitialDeformationField);
      }

    if( this->m_FixedLandmarkFilename != ""
        && this->m_MovingLandmarkFilename != "" )
      {
      std::cerr
      << "Registering Landmarks as an initializer is not yet implemented"
      << std::endl;
      exit(-1);
      }

    // Perform the registration.
    try
      {
      m_VectorRegistration->Update();
      }
    catch( itk::ExceptionObject & err )
      {
      std::cout << "Caught an exception: " << std::endl;
      std::cout << err << " " << __FILE__ << " " << __LINE__ << std::endl;
      throw err;
      throw err;
      }
    catch( ... )
      {
      std::cout << "Caught a non-ITK exception " << __FILE__ << " "
                << __LINE__ << std::endl;
      }
    if( this->GetOutDebug() )
      {
      std::cout
      <<
      "Moving image shrink factors used in each level of MultiResolution Schedule\n"
      << m_MovingImagePyramid->GetSchedule() << std::endl;
      std::cout
      <<
      "Fixed image shrink factors used in each level of MultiResolution Schedule\n"
      << m_FixedImagePyramid->GetSchedule() << std::endl;
      }
    try
      {
      m_DeformationField = m_VectorRegistration->GetOutput();
      if( m_DeformationField->GetDirection() != m_FixedImage[0]->GetDirection() )
        {
        std::cout << "ERROR Directions don't match\n"
                  << m_DeformationField->GetDirection()
                  << "\n"
                  << m_FixedImage[0]->GetDirection()
                  << std::endl;
        exit(-1);
        }
      if( m_VectorTag )
        {
        m_VectorRegistration->RemoveObserver(m_VectorTag);
        m_VectorTag = 0;
        }
      m_VectorRegistration = NULL;
      }
    catch( itk::ExceptionObject & err )
      {
      std::cout << "Caught an exception: " << std::endl;
      std::cout << err << " " << __FILE__ << " " << __LINE__ << std::endl;
      throw err;
      }
    catch( ... )
      {
      std::cout << "Caught a non-ITK exception " << __FILE__ << " "
                << __LINE__ << std::endl;
      }
    }
  else
    {
    m_Registration->SetFixedImage(m_FixedImage[0]);
    m_Registration->SetMovingImage(m_MovingImage[0]);
    m_Registration->SetNumberOfLevels(m_NumberOfLevels);
    m_Registration->SetNumberOfIterations( m_NumberOfIterations.
                                           data_block() );

    // Setup the initial deformation field
    if( this->m_InitialDeformationField.IsNotNull() )
      {
      m_Registration->SetInitialDeformationField(
        this->m_InitialDeformationField);
      }
    if( this->m_FixedLandmarkFilename != ""
        && this->m_MovingLandmarkFilename != "" )
      {
      std::cerr
      << "Registering Landmarks as an initializer is not yet implemented"
      << std::endl;
      exit(-1);
      }
    // Perform the registration.
    try
      {
      m_Registration->Update();
      }
    catch( itk::ExceptionObject & err )
      {
      std::cout << "Caught an exception: " << std::endl;
      std::cout << err << " " << __FILE__ << " " << __LINE__ << std::endl;
      throw err;
      throw err;
      }
    catch( ... )
      {
      std::cout << "Caught a non-ITK exception " << __FILE__ << " "
                << __LINE__ << std::endl;
      }

    if( this->GetOutDebug() )
      {
      std::cout
      <<
      "Moving image shrink factors used in each level of MultiResolution Schedule\n"
      << m_MovingImagePyramid->GetSchedule() << std::endl;
      std::cout
      <<
      "Fixed image shrink factors used in each level of MultiResolution Schedule\n"
      << m_FixedImagePyramid->GetSchedule() << std::endl;
      }
    try
      {
      m_DeformationField = m_Registration->GetOutput();
      if( m_DeformationField->GetDirection() != m_FixedImage[0]->GetDirection() )
        {
        std::cout << "ERROR Directions don't match\n"
                  << m_DeformationField->GetDirection()
                  << "\n"
                  << m_FixedImage[0]->GetDirection()
                  << std::endl;
        exit(-1);
        }
      if( m_Tag )
        {
        m_Registration->RemoveObserver(m_Tag);
        m_Tag = 0;
        }
      m_Registration = NULL;
      }
    catch( itk::ExceptionObject & err )
      {
      std::cout << "Caught an exception: " << std::endl;
      std::cout << err << " " << __FILE__ << " " << __LINE__ << std::endl;
      throw err;
      }
    catch( ... )
      {
      std::
      cout << "Caught a non-ITK exception " << __FILE__ << " " << __LINE__
           << std::endl;
      }
    }

  // Write the output deformation fields if specified by the user.
  if( this->m_DeformationFieldOutputName != std::string("none")
      && this->m_DeformationFieldOutputName != std::string("") )
    {
    itkUtil::WriteImage<TDeformationField>(m_DeformationField,
                                           this->m_DeformationFieldOutputName);
    if( this->GetOutDebug() )
      {
      std::cout << "---Deformation field has been written "
                << this->m_DeformationFieldOutputName << "--" << std::endl;
      }
    }

  //  Write out the displacement fields specified by the user.
  if( this->m_DisplacementBaseName != std::string("none") )
    {
    this->WriteDisplacementComponents();
    }

  if( this->m_WarpedImageName != std::string("none")
      || this->m_CheckerBoardFilename != std::string("none") )
    {
    typename RealImageType::Pointer DeformedMovingImagePtr(0);

      {
      typename RealImageType::Pointer sourceMovingImage = NULL;
      if( this->GetUseHistogramMatching() == true )
        {
        sourceMovingImage = m_MovingImage[0];
        }
      else
        {
        sourceMovingImage = m_UnNormalizedMovingImage[0];
        }
      DeformedMovingImagePtr = TransformWarp<RealImageType, RealImageType, TDeformationField>(
          sourceMovingImage,
          m_FixedImage[0],
          0,
          GetInterpolatorFromString<RealImageType>(this->m_InterpolationMode),
          m_DeformationField);
      }

    if( this->GetOutDebug() )
      {
      std::cout << "-----Direction of output warped image\n"
                << DeformedMovingImagePtr->GetDirection()
                << "\n-----Direction of deformation field\n"
                << this->m_DeformationField->GetDirection() << std::endl;
      }
    /*Write the output image.*/
    if( this->m_WarpedImageName != std::string("none") )
      {
      typename TOutputImage::Pointer CastImageSptr =
        itkUtil::PreserveCast<RealImageType, TOutputImage>(
          DeformedMovingImagePtr);
      itkUtil::WriteImage<TOutputImage>(CastImageSptr,
                                        this->m_WarpedImageName);

      if( this->GetOutDebug() )
        {
        std::cout << "---Deformed Image has been written" << std::endl;
        }
      }

    /*Write the checkerboard image of the fixed image and the output image.*/
    if( this->m_CheckerBoardFilename != std::string("none") )
      {
      typedef itk::CheckerBoardImageFilter<RealImageType> Checkerfilter;
      typename Checkerfilter::Pointer checker = Checkerfilter::New();
      if( this->GetUseHistogramMatching() == true )
        {
        checker->SetInput1(m_FixedImage[0]);
        }
      else
        {
        checker->SetInput1(m_UnNormalizedFixedImage[0]);
        }
      checker->SetInput2(DeformedMovingImagePtr);
      checker->SetCheckerPattern( this->GetCheckerBoardPattern() );
      try
        {
        checker->Update();
        }
      catch( itk::ExceptionObject & err )
        {
        std::cout << "Caught an ITK exception: " << std::endl;
        std::cout << err << " " << __FILE__ << " " << __LINE__ << std::endl;
        throw err;
        }
      typename RealImageType::Pointer CheckerImagePtr = checker->GetOutput();
      itkUtil::WriteImage<RealImageType>(CheckerImagePtr,
                                         this->m_CheckerBoardFilename);
      if( this->GetOutDebug() )
        {
        std::cout << "---Checker Board Image has been written" << std::endl;
        }
      }
    }
}

// Print out the present registration level.
template <
  class TRealImage,
  class TOutputImage,
  class TFieldValue>
void VDemonsRegistrator<TRealImage, TOutputImage, TFieldValue>::StartNewLevel()
{
  if( this->GetOutDebug() )
    {
    //     if(this->m_FixedImage.size() ==1)
    //     std::cout << "--- Starting level " << m_Registration->GetCurrentLevel
    // () << std::endl;

    std::cout << "--- Starting level "
              << m_VectorRegistration->GetCurrentLevel() << std::endl;
    }
}

}  // namespace itk
#endif
