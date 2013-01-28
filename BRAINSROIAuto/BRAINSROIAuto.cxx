/*=========================================================================
 *
 *  Program:   Insight Segmentation & Registration Toolkit
 *  Module:    $RCSfile$
 *  Language:  C++
 *  Date:      $Date: 2007-08-31 11:20:20 -0500 (Fri, 31 Aug 2007) $
 *  Version:   $Revision: 10358 $
 *
 *  Copyright (c) Insight Software Consortium. All rights reserved.
 *  See ITKCopyright.txt or http://www.itk.org/HTML/Copyright.htm for details.
 *
 *  This software is distributed WITHOUT ANY WARRANTY; without even
 *  the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
 *  PURPOSE.  See the above copyright notices for more information.
 *
 *  =========================================================================*/

/**
  * Hans J. Johnson @ The University of Iowa
  * This program is a standalone version of a program for masking and clipping
  *images
  * using the ROIAUTO method that seems to work well for brain images.
  */

#include <itkMultiplyImageFilter.h>
#include <itkImageMaskSpatialObject.h>
#include <itkImageRegionIteratorWithIndex.h>
#include <itkImageRegionConstIteratorWithIndex.h>
#include <itkExtractImageFilter.h>
#include <vcl_algorithm.h>

#include "itkIO.h"
#include "itkLargestForegroundFilledMaskImageFilter.h"
#include "itkBRAINSROIAutoImageFilter.h"
#include "BRAINSROIAutoCLP.h"
#include "BRAINSThreadControl.h"
typedef itk::Image<signed int, 3>    VolumeImageType;
typedef itk::Image<unsigned char, 3> VolumeMaskType;
typedef itk::SpatialObject<3>        SOImageMaskType;

/**
  * This file contains utility functions that are common to a few of the
  *BRAINSFit Programs.
  */

template <typename PixelType>
void
BRAINSROIAUTOWriteOutputVolume(VolumeImageType::Pointer image,
                               VolumeMaskType::Pointer mask,
                               std::string & fileName,
                               const bool MaskImage,
                               const bool CropImage)
{
  typedef typename itk::Image<PixelType, VolumeImageType::ImageDimension> WriteOutImageType;
  typename WriteOutImageType::Pointer finalOutput;
    {
    typedef itk::CastImageFilter<VolumeImageType, WriteOutImageType> CasterType;
    typename CasterType::Pointer myCaster=CasterType::New();
    myCaster->SetInput(image);
    myCaster->Update();
    finalOutput=myCaster->GetOutput();
    }
  if(MaskImage)
    {
    typedef typename itk::MultiplyImageFilter<VolumeMaskType, WriteOutImageType, WriteOutImageType> MultiplierType;

    typename MultiplierType::Pointer clipper = MultiplierType::New();
    clipper->SetInput1(mask);
    clipper->SetInput2(finalOutput);
    clipper->Update();
    finalOutput = clipper->GetOutput();
    }
  if(CropImage)
    {
    typename VolumeMaskType::IndexType minIndex;
    typename VolumeMaskType::IndexType maxIndex;
    for( VolumeMaskType::IndexType::IndexValueType i=0; i < VolumeMaskType::ImageDimension; ++i)
      {
      minIndex[i]=vcl_numeric_limits<VolumeMaskType::IndexType::IndexValueType>::max();
      maxIndex[i]=vcl_numeric_limits<VolumeMaskType::IndexType::IndexValueType>::min();
      }
    itk::ImageRegionConstIteratorWithIndex<VolumeMaskType> maskIt(mask,mask->GetLargestPossibleRegion());
    while(!maskIt.IsAtEnd())
      {
      if( maskIt.Get() > 0 )
        {
        const typename VolumeMaskType::IndexType &currIndex = maskIt.GetIndex();
        for( VolumeMaskType::IndexType::IndexValueType i=0; i < VolumeMaskType::ImageDimension; ++i)
          {
          minIndex[i]=vcl_min(minIndex[i],currIndex[i]);
          maxIndex[i]=vcl_max(maxIndex[i],currIndex[i]);
          }
        }
      ++maskIt;
      }
    VolumeMaskType::SizeType desiredSize;
    for( VolumeMaskType::IndexType::IndexValueType i=0; i < VolumeMaskType::ImageDimension; ++i)
      {
      desiredSize[i]= maxIndex[i]-minIndex[i]-1;
      }
    VolumeMaskType::RegionType desiredRegion(minIndex, desiredSize);

    typedef itk::ExtractImageFilter< WriteOutImageType, WriteOutImageType > ExtractorType;
    typename ExtractorType::Pointer myExtractor = ExtractorType::New();
    myExtractor->SetExtractionRegion(desiredRegion);
    myExtractor->SetInput(finalOutput);
#if ITK_VERSION_MAJOR >= 4
    myExtractor->SetDirectionCollapseToIdentity(); // This is required.
#endif
    myExtractor->Update();
    finalOutput=myExtractor->GetOutput();
    }
  itkUtil::WriteImage<WriteOutImageType>(finalOutput, fileName);
}

int main(int argc, char *argv[])
{
  PARSE_ARGS;
  const BRAINSUtils::StackPushITKDefaultNumberOfThreads TempDefaultNumberOfThreadsHolder(numberOfThreads);
  if( inputVolume == "" )
    {
    std::cerr << argv[0] << ": Missing required --inputVolume parameter"
              << std::endl;
    return EXIT_FAILURE;
    }
  VolumeImageType::Pointer ImageInput =
    itkUtil::ReadImage<VolumeImageType>(inputVolume);

  typedef itk::BRAINSROIAutoImageFilter<VolumeImageType, VolumeMaskType> ROIAutoType;
  ROIAutoType::Pointer ROIFilter = ROIAutoType::New();
  ROIFilter->SetInput(ImageInput);
  ROIFilter->SetOtsuPercentileThreshold(otsuPercentileThreshold);
  ROIFilter->SetClosingSize(closingSize);
  ROIFilter->SetThresholdCorrectionFactor(thresholdCorrectionFactor);
  ROIFilter->SetDilateSize(ROIAutoDilateSize);
  ROIFilter->Update();
  // const SOImageMaskType::Pointer maskWrapper = ROIFilter->GetSpatialObjectROI();
  VolumeMaskType::Pointer  MaskImage = ROIFilter->GetOutput();

  if( outputROIMaskVolume != "" )
    {
    itkUtil::WriteImage<VolumeMaskType>(MaskImage, outputROIMaskVolume);
    }

  if( outputVolume != "" )
    {
    //      std::cout << "=========== resampledImage :\n" <<
    // resampledImage->GetDirection() << std::endl;
    // Set in PARSEARGS const bool scaleOutputValues=false;//TODO: Make this a
    // command line parameter
    if( outputVolumePixelType == "float" )
      {
      BRAINSROIAUTOWriteOutputVolume<float>(ImageInput, MaskImage, outputVolume, maskOutput, cropOutput);
      }
    else if( outputVolumePixelType == "short" )
      {
      BRAINSROIAUTOWriteOutputVolume<signed short>(ImageInput, MaskImage, outputVolume, maskOutput, cropOutput);
      }
    else if( outputVolumePixelType == "ushort" )
      {
      BRAINSROIAUTOWriteOutputVolume<unsigned short>(ImageInput, MaskImage, outputVolume, maskOutput, cropOutput);
      }
    else if( outputVolumePixelType == "int" )
      {
      BRAINSROIAUTOWriteOutputVolume<signed int>(ImageInput, MaskImage, outputVolume, maskOutput, cropOutput);
      }
    else if( outputVolumePixelType == "uint" )
      {
      BRAINSROIAUTOWriteOutputVolume<unsigned int>(ImageInput, MaskImage, outputVolume, maskOutput, cropOutput);
      }
    else if( outputVolumePixelType == "uchar" )
      {
      BRAINSROIAUTOWriteOutputVolume<unsigned char>(ImageInput, MaskImage, outputVolume, maskOutput, cropOutput);
      }
    }
  return EXIT_SUCCESS;
}
