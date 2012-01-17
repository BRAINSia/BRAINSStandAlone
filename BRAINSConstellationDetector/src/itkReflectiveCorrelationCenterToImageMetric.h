/*
 * Author: Hans J. Johnson, Wei Lu
 * at Psychiatry Imaging Lab,
 * University of Iowa Health Care 2010
 */

/*=========================================================================

 Program:   Insight Segmentation & Registration Toolkit
 Module:    $RCSfile: itkReflectiveCorrelationCenterToImageMetric.h,v $
 Language:  C++
 Date:      $Date: 2008-02-03 04:05:28 $
 Version:   $Revision: 1.31 $

 Copyright (c) Insight Software Consortium. All rights reserved.
 See ITKCopyright.txt or http://www.itk.org/HTML/Copyright.htm for details.

 This software is distributed WITHOUT ANY WARRANTY; without even
 the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
 PURPOSE.  See the above copyright notices for more information.

 =========================================================================*/
#ifndef __itkReflectiveCorrelationCenterToImageMetric_h
#define __itkReflectiveCorrelationCenterToImageMetric_h

#include "itkPoint.h"
#include "itkIdentityTransform.h"
#include <vnl/vnl_cost_function.h>

#include "vnl/algo/vnl_powell.h"
#include "landmarksConstellationCommon.h"
#include "GenericTransformImage.h"
#include "itkStatisticsImageFilter.h"

// Optimize the A,B,C vector
class Rigid3DCenterReflectorFunctor : public vnl_cost_function
{
public:
  static const int UNKNOWNS_TO_ESTIMATE = 3;

  void SetCenterOfHeadMass(SImageType::PointType centerOfHeadMass)
  {
    m_CenterOfHeadMass = centerOfHeadMass;
  }

  void QuickSampleParameterSpace(void)
  {
    vnl_vector<double> params;
    params.set_size(3);

    params[0] = 0;
    params[1] = 0;
    params[2] = 0;
    // Initialize with current guess;
    double max_cc = this->f(params);
    this->m_params = params;
    const double HARange = 25.0;
    const double BARange = 15.0;
    // rough search in neighborhood.
    const double one_degree = 1.0F * vnl_math::pi / 180.0F;
    const double HAStepSize = HARange * one_degree * .1;
    const double BAStepSize = BARange * one_degree * .1;
    // Let the powell optimizer do all the work for determining the proper
    // offset
    // Quick search just needs to get an approximate angle correct.
    // const double OffsetRange=8.0;
    // const double OffsetStepSize=2.0;
    const double Offset = 0.0;
    // for(double Offset=-OffsetRange;Offset<=OffsetRange;
    // Offset+=OffsetStepSize)
      {
      for( double HA = -HARange * one_degree; HA <= HARange * one_degree; HA += HAStepSize )
        {
        for( double BA = -BARange * one_degree; BA <= BARange * one_degree; BA += BAStepSize )
          {
          params[0] = HA;
          params[1] = BA;
          params[2] = Offset;
          const double current_cc = this->f(params);
          if( current_cc < max_cc )
            {
            this->m_params = params;
            max_cc = current_cc;
            }
          }
        }
      }
    // DEBUGGING INFORMATION
    if( LMC::globalverboseFlag == true )
      {
      std::cout << "quick search 15 deg "
                << " HA= " << this->m_params[0] * 180.0 / vnl_math::pi
                << " BA= " << this->m_params[1] * 180.0 / vnl_math::pi
                << " XO= " << this->m_params[2]
                << " cc="  <<  this->f(this->m_params)
                << " iterations=" << this->GetIterations()
                << std::endl;
      }
  }

  Rigid3DCenterReflectorFunctor() : vnl_cost_function(UNKNOWNS_TO_ESTIMATE), m_Iterations(0), m_Optimizer( &( *this ) )
  {
    this->m_params.set_size(UNKNOWNS_TO_ESTIMATE);
    this->m_params.fill(0.0);

    static const double default_tolerance = 1e-4;
    static const double InitialStepSize = 7.0 * vnl_math::pi / 180.0;
    this->m_Optimizer.set_initial_step(InitialStepSize);
    this->m_Optimizer.set_f_tolerance(default_tolerance); // TODO:  This should
                                                          // be optimized for
                                                          // speed.
    this->m_Optimizer.set_x_tolerance(default_tolerance); // TODO:  Need to do
                                                          // extensive testing
                                                          // of the speed
                                                          // effects of changing
                                                          // this value with
                                                          // respect to quality
                                                          // of result.

    this->m_imInterp = LinearInterpolatorType::New();
  }

  double f(vnl_vector<double> const & params)
  {
    const double        MaxUnpenalizedAllowedDistance = 8.0;
    const double        DistanceFromCenterOfMass = vcl_abs(params[2]);
    static const double FortyFiveDegreesAsRadians = 45.0 * vnl_math::pi / 180.0;
    const double        cost_of_HeadingAngle = ( vcl_abs(params[0]) < FortyFiveDegreesAsRadians ) ? 0 :
      ( ( vcl_abs(params[0]) - FortyFiveDegreesAsRadians ) * 2 );
    const double cost_of_BankAngle = ( vcl_abs(params[1]) < FortyFiveDegreesAsRadians ) ? 0 :
      ( ( vcl_abs(params[1]) - FortyFiveDegreesAsRadians ) * 2 );

    if( ( vcl_abs(params[0]) > FortyFiveDegreesAsRadians ) || ( vcl_abs(params[1]) > FortyFiveDegreesAsRadians ) )
      {
      std::cout << "WARNING: ESTIMATED ROTATIONS ARE WAY TOO BIG SO GIVING A HIGH COST" << std::endl;
      return 1;
      }
    const double cc = -CenterImageReflection_crossCorrelation(params);
    m_Iterations++;

    const double cost_of_motion = ( vcl_abs(DistanceFromCenterOfMass) < MaxUnpenalizedAllowedDistance ) ? 0 :
      ( vcl_abs(DistanceFromCenterOfMass - MaxUnpenalizedAllowedDistance) * .1 );
    const double raw_finalcos_gamma = cc + cost_of_motion + cost_of_BankAngle + cost_of_HeadingAngle;

#ifdef __USE_EXTENSIVE_DEBUGGING__
    if( !vnl_math_isfinite(raw_finalcos_gamma) )
      {
      std::cout << __FILE__ << " " << __LINE__ << " "
                << params << " : " << cc << " " << cost_of_HeadingAngle << " " << cost_of_BankAngle << " "
                << cost_of_motion << std::endl;
      return EXIT_FAILURE;
      }
#endif
    return raw_finalcos_gamma;
  }

  RigidTransformType::Pointer GetTransformToMSP(void) const
  {
    // Compute and store the new output image origin
    m_ResampleFilter->SetTransform( this->GetTransformFromParams(this->m_params) );
    m_ResampleFilter->Update();
    SImageType::Pointer image = m_ResampleFilter->GetOutput();

    // it is also the msp location
    SImageType::PointType physCenter = GetImageCenterPhysicalPoint(image);

    // Move the physical origin to the center of the image
    RigidTransformType::Pointer tempEulerAngles3DT = RigidTransformType::New();
    tempEulerAngles3DT->Compose( this->GetTransformFromParams(this->m_params) );
    RigidTransformType::TranslationType tnsl = tempEulerAngles3DT->GetTranslation();

    tempEulerAngles3DT->Translate(physCenter.GetVectorFromOrigin() - tnsl);
    return tempEulerAngles3DT;
  }

  void Initialize(SImageType::Pointer & RefImage)
  {
      {
      SImageType::PixelType dummy;
      // Find threshold below which image is considered background.
      m_BackgroundValue = setLowHigh<SImageType>(RefImage, dummy, dummy, 0.1F);
      }

    this->m_CenterOfImagePoint = GetImageCenterPhysicalPoint(RefImage);

#ifdef USE_DEBUGGIN_IMAGES
      {
      itk::ImageFileWriter<SImageType>::Pointer dbgWriter = itk::ImageFileWriter<SImageType>::New();
      dbgWriter->UseCompressionOn();
      dbgWriter->SetFileName("itkReflectiveCorrelationCenterToImageMetric149.nii.gz");
      dbgWriter->SetInput(RefImage);
      dbgWriter->Update();
      }
#endif

    this->m_OriginalImage = RefImage;
    this->m_Translation = this->m_CenterOfHeadMass.GetVectorFromOrigin() - m_CenterOfImagePoint.GetVectorFromOrigin();
    if( LMC::globalverboseFlag == true )
      {
      std::cout << "Center Of Physical Point: " << this->m_CenterOfImagePoint << std::endl;
      std::cout << "Center Of Mass Point:" << this->m_CenterOfHeadMass << std::endl;
      std::cout << "IntialTranslation: " << this->m_Translation << std::endl;
      }
  }

  /* -- */
  void SetDownSampledReferenceImage(SImageType::Pointer & NewImage)
  {
    m_OriginalImage = NewImage;
  }

  /* -- */
  unsigned int GetIterations(void) const
  {
    return m_Iterations;
  }

  /* -- */
  SImageType::PixelType GetBackgroundValue(void) const
  {
    return this->m_BackgroundValue;
  }

  /* -- */
  RigidTransformType::Pointer GetTransformFromParams(vnl_vector<double> const & params) const
  {
    RigidTransformType::Pointer tempEulerAngles3DT = RigidTransformType::New();

    tempEulerAngles3DT->SetCenter(this->m_CenterOfImagePoint);
    tempEulerAngles3DT->SetRotation(0, params[1], params[0]);
    SImageType::PointType::VectorType tnsl = this->m_Translation;
    tnsl[0] += params[2];
    tempEulerAngles3DT->SetTranslation(tnsl);
    return tempEulerAngles3DT;
  }

  /* -- */
  double CenterImageReflection_crossCorrelation(vnl_vector<double> const & params)
  {
    // TODO WEI: the following block of code only need to be computed once for
    // one image.
    // Tried to move them to the Initialize function but it then went into a
    // infinite loop at level 0.
    // Very strange but has no priority
      {
      // Define the output image direction identical
      m_OutputImageDirection.SetIdentity();

      // Get output spacing
      SImageType::DirectionType inputImageDirection = m_OriginalImage->GetDirection();
      SImageType::SpacingType   inputImageSpacing = m_OriginalImage->GetSpacing();
      m_OutputImageSpacing = inputImageDirection * inputImageSpacing;
      for( unsigned int i = 0; i < 3; ++i )
        {
        if( m_OutputImageSpacing[i] < 0 )
          {
          m_OutputImageSpacing[i] *= -1;
          }
        }

      // Define start index
      m_OutputImageStartIndex.Fill(0);

      // Desire a 95*2 x 130*2 x 160x2 mm voxel lattice that will fit a brain
      m_OutputImageSize[0] = static_cast<unsigned long int>( 2.0 * vcl_ceil(95.0  / m_OutputImageSpacing[0]) );
      m_OutputImageSize[1] = static_cast<unsigned long int>( 2.0 * vcl_ceil(130.0 / m_OutputImageSpacing[1]) );
      m_OutputImageSize[2] = static_cast<unsigned long int>( 2.0 * vcl_ceil(160.0 / m_OutputImageSpacing[2]) );

      // The physical center of MSP plane is not determined yet. At the
      // optimizing stage we take COM as physical center
      m_OutputImageOrigin[0] = m_CenterOfHeadMass[0] - .5 * ( m_OutputImageSize[0] - 1 ) * m_OutputImageSpacing[0];
      m_OutputImageOrigin[1] = m_CenterOfHeadMass[1] - .5 * ( m_OutputImageSize[1] - 1 ) * m_OutputImageSpacing[1];
      m_OutputImageOrigin[2] = m_CenterOfHeadMass[2] - .5 * ( m_OutputImageSize[2] - 1 ) * m_OutputImageSpacing[2];
      }
    /*
        std::cout << "CenterImageReflection_crossCorrelation:" << std::endl;
        std::cout << "m_OutputImageOrigin = " << m_OutputImageOrigin << std::endl;
        std::cout << "m_OutputImageSize = " << m_OutputImageSize << std::endl;
        std::cout << "m_OutputImageStartIndex = " << m_OutputImageStartIndex << std::endl;
        std::cout << "m_OutputImageSpacing = " << m_OutputImageSpacing << std::endl;
        std::cout << "m_OutputImageDirection = " << m_OutputImageDirection << std::endl;
    */
    /*
     * Resample the image
     */
    m_ResampleFilter = FilterType::New();
    LinearInterpolatorType::Pointer interpolator = LinearInterpolatorType::New();
    m_ResampleFilter->SetInterpolator(interpolator);
    m_ResampleFilter->SetDefaultPixelValue(0);
    m_ResampleFilter->SetOutputSpacing(m_OutputImageSpacing);
    m_ResampleFilter->SetOutputOrigin(m_OutputImageOrigin);
    m_ResampleFilter->SetSize(m_OutputImageSize);
    m_ResampleFilter->SetOutputDirection(m_OutputImageDirection);
    m_ResampleFilter->SetOutputStartIndex(m_OutputImageStartIndex);
    m_ResampleFilter->SetInput(this->m_OriginalImage);
    m_ResampleFilter->SetTransform( this->GetTransformFromParams(params) );
    m_ResampleFilter->Update();
    m_InternalResampledForReflectiveComputationImage = m_ResampleFilter->GetOutput();

    /*
     * Compute the reflective correlation
     */
    double               sumVoxelValues = 0.0F;
    double               sumSquaredVoxelValues = 0.0F;
    double               sumVoxelValuesQR = 0.0F;
    double               sumVoxelValuesReflected = 0.0F;
    double               sumSquaredVoxelValuesReflected = 0.0F;
    int                  N = 0;
    SImageType::SizeType rasterResampleSize =
      m_InternalResampledForReflectiveComputationImage->GetLargestPossibleRegion().GetSize();
    const SImageType::SizeType::SizeValueType xMaxIndexResampleSize = rasterResampleSize[0] - 1;
    rasterResampleSize[0] /= 2; // Only need to do 1/2 in the x direction;
    SImageType::RegionType rasterRegion;
    rasterRegion.SetSize(rasterResampleSize);
    rasterRegion.SetIndex( m_InternalResampledForReflectiveComputationImage->GetLargestPossibleRegion().GetIndex() );
    itk::ImageRegionConstIteratorWithIndex<SImageType> halfIt(m_InternalResampledForReflectiveComputationImage,
                                                              rasterRegion);
    for( halfIt.GoToBegin(); !halfIt.IsAtEnd(); ++halfIt )
      {
      // NOTE:  Only need to compute left half of space because of reflection.
      const double _f = halfIt.Get();
      if( _f < this->m_BackgroundValue )  // don't worry about background
                                          // voxels.
        {
        continue;
        }
      SImageType::IndexType ReflectedIndex = halfIt.GetIndex();
      ReflectedIndex[0] = xMaxIndexResampleSize - ReflectedIndex[0];
      const double g = m_InternalResampledForReflectiveComputationImage->GetPixel(ReflectedIndex);
      if( g < this->m_BackgroundValue )  // don't worry about background voxels.
        {
        continue;
        }
      sumVoxelValuesQR += _f * g;
      sumSquaredVoxelValuesReflected += g * g;
      sumVoxelValuesReflected += g;
      sumSquaredVoxelValues += _f * _f;
      sumVoxelValues += _f;
      N++;
      }

    // ///////////////////////////////////////////////
    if( N == 0
        || ( ( sumSquaredVoxelValues - sumVoxelValues * sumVoxelValues
               / N ) * ( sumSquaredVoxelValuesReflected - sumVoxelValuesReflected * sumVoxelValuesReflected / N ) ) ==
        0.0 )
      {
      return 0.0;
      }
    const double cc =
      ( ( sumVoxelValuesQR - sumVoxelValuesReflected * sumVoxelValues
          / N )
        / vcl_sqrt( ( sumSquaredVoxelValues - sumVoxelValues * sumVoxelValues
                      / N )
                    * ( sumSquaredVoxelValuesReflected - sumVoxelValuesReflected * sumVoxelValuesReflected / N ) ) );
    return cc;
  }

  SImageType::Pointer GetMSPCenteredImage(void)
  {
    // Note GetTransformToMSP() aligns physical origin to the center of MSP.
    // SimpleResampleImage() further aligns physical center of image to physical
    // origin.

    // RigidTransformType::Pointer tempEulerAngles3DT = GetTransformToMSP();
    // return SimpleResampleImage( this->m_OriginalImage, tempEulerAngles3DT );

    // create a colormap lookup table
    typedef itk::StatisticsImageFilter<SImageType> StatisticsFilterType;
    StatisticsFilterType::Pointer statisticsFilter = StatisticsFilterType::New();
    statisticsFilter->SetInput(this->m_OriginalImage);
    statisticsFilter->Update();
    SImageType::PixelType minPixelValue = statisticsFilter->GetMinimum();

    return TransformResample<SImageType, SImageType>
             ( this->m_OriginalImage,
             MakeIsoTropicReferenceImage(),
             minPixelValue,
             GetInterpolatorFromString<SImageType>("Linear"),
             GetTransformToMSP().GetPointer() );
  }

  void Update(void)
  {
    this->m_Optimizer.minimize(this->m_params);
    std::cout << this->m_params[0] * 180.0 / vnl_math::pi << " " << this->m_params[1] * 180.0 / vnl_math::pi << " "
              << this->m_params[2] << " cc= " << this->f(this->m_params) << " iters= " << this->GetIterations()
              << std::endl;
  }

private:

  SImageType::Pointer SimpleResampleImage(SImageType::Pointer image, RigidTransformType::Pointer EulerAngles3DT)
  {
    m_ResampleFilter = FilterType::New();
    LinearInterpolatorType::Pointer interpolator = LinearInterpolatorType::New();
    m_ResampleFilter->SetInterpolator(interpolator);
    m_ResampleFilter->SetDefaultPixelValue(0);
    m_ResampleFilter->SetOutputSpacing(m_OutputImageSpacing);
    m_ResampleFilter->SetSize(m_OutputImageSize);
    m_ResampleFilter->SetOutputDirection(m_OutputImageDirection);
    m_ResampleFilter->SetOutputStartIndex(m_OutputImageStartIndex);
    m_ResampleFilter->SetInput(image);
    m_ResampleFilter->SetTransform(EulerAngles3DT);

    // Move the physical center of image to the physical origin
    m_OutputImageOrigin[0] = -0.5 * ( m_OutputImageSize[0] - 1 ) * m_OutputImageSpacing[0];
    m_OutputImageOrigin[1] = -0.5 * ( m_OutputImageSize[1] - 1 ) * m_OutputImageSpacing[1];
    m_OutputImageOrigin[2] = -0.5 * ( m_OutputImageSize[2] - 1 ) * m_OutputImageSpacing[2];
    m_ResampleFilter->SetOutputOrigin(m_OutputImageOrigin);

    m_ResampleFilter->Update();

    SImageType::Pointer returnImage = m_ResampleFilter->GetOutput();
    returnImage->DisconnectPipeline();
    return returnImage;
  }

  typedef vnl_powell                                       OptimizerType;
  typedef itk::ResampleImageFilter<SImageType, SImageType> FilterType;

  vnl_vector<double>                m_params;
  SImageType::Pointer               m_OriginalImage;
  SImageType::SpacingType           m_OutputImageSpacing;
  SImageType::DirectionType         m_OutputImageDirection;
  SImageType::IndexType             m_OutputImageStartIndex;
  SImageType::SizeType              m_OutputImageSize;
  SImageType::PointType             m_OutputImageOrigin;
  SImageType::PointType             m_CenterOfHeadMass;
  SImageType::Pointer               m_InternalResampledForReflectiveComputationImage;
  FilterType::Pointer               m_ResampleFilter;
  SImageType::PixelType             m_BackgroundValue;
  SImageType::PointType             m_CenterOfImagePoint;
  SImageType::PointType::VectorType m_Translation;
  int                               m_Iterations;
  OptimizerType                     m_Optimizer;
  LinearInterpolatorType::Pointer   m_imInterp;
};

namespace itk
    {} // end namespace itk

#ifndef ITK_MANUAL_INSTANTIATION
#include "itkReflectiveCorrelationCenterToImageMetric.hxx"
#endif

#endif
