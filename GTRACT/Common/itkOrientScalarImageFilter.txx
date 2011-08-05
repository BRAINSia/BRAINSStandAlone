/*=========================================================================

 Program:   GTRACT (Guided Tensor Restore Anatomical Connectivity Tractography)
 Module:    $RCSfile: $
 Language:  C++
 Date:      $Date: 2006/03/29 14:53:40 $
 Version:   $Revision: 1.9 $

   Copyright (c) University of Iowa Department of Radiology. All rights reserved.
   See GTRACT-Copyright.txt or http://mri.radiology.uiowa.edu/copyright/GTRACT-Copyright.txt
   for details.

      This software is distributed WITHOUT ANY WARRANTY; without even
      the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
      PURPOSE.  See the above copyright notices for more information.

=========================================================================*/

#ifndef __itkOrientScalarImageFilter_txx
#define __itkOrientScalarImageFilter_txx

#include "itkImageRegionIterator.h"
#include "itkImageRegionConstIterator.h"
#include "itkOrientScalarImageFilter.h"
#include <itkIOCommon.h>
#include <itkCastImageFilter.h>
#include <itkConstantPadScalarImageFilter.h>
#include <itkExtractImageFilter.h>
#include "itkMetaDataObject.h"
#include "itkProgressAccumulator.h"

namespace itk
{
template <class TInputImage, class TOutputImage>
OrientScalarImageFilter<TInputImage, TOutputImage>
::OrientScalarImageFilter() :
  m_GivenCoordinateOrientation( SpatialOrientation::ITK_COORDINATE_ORIENTATION_RIP ),
  m_DesiredCoordinateOrientation( SpatialOrientation::ITK_COORDINATE_ORIENTATION_RIP )

{
}

template <class TInputImage, class TOutputImage>
void
OrientScalarImageFilter<TInputImage, TOutputImage>
::GenerateInputRequestedRegion()
{
  // call the superclass' implementation of this method
  Superclass::GenerateInputRequestedRegion();

  // get pointers to the input and output
  InputImagePointer  inputPtr = const_cast<TInputImage *>( this->GetInput() );
  OutputImagePointer outputPtr = this->GetOutput();

  if( !inputPtr || !outputPtr )
    {
    return;
    }

  // we need to compute the input requested region (size and start index)
  unsigned int i;
  const typename TOutputImage::SizeType  & outputRequestedRegionSize         = outputPtr->GetRequestedRegion().GetSize();
  const typename TOutputImage::IndexType & outputRequestedRegionStartIndex  = outputPtr->GetRequestedRegion().GetIndex();

  typename TInputImage::SizeType  inputRequestedRegionSize;
  typename TInputImage::IndexType inputRequestedRegionStartIndex;
  for( i = 0; i < TInputImage::ImageDimension; i++ )
    {
    inputRequestedRegionSize[i]       =       outputRequestedRegionSize[m_PermuteOrder[i]];
    inputRequestedRegionStartIndex[i] = outputRequestedRegionStartIndex[m_PermuteOrder[i]];
    }

  typename TInputImage::RegionType inputRequestedRegion;
  inputRequestedRegion.SetSize( inputRequestedRegionSize );
  inputRequestedRegion.SetIndex( inputRequestedRegionStartIndex );

  inputPtr->SetRequestedRegion( inputRequestedRegion );
}

template <class TInputImage, class TOutputImage>
void
OrientScalarImageFilter<TInputImage, TOutputImage>
::EnlargeOutputRequestedRegion(DataObject *)
{
  this->GetOutput()
  ->SetRequestedRegion( this->GetOutput()->GetLargestPossibleRegion() );
}

template <class TInputImage, class TOutputImage>
void
OrientScalarImageFilter<TInputImage, TOutputImage>
::DeterminePermutationsAndFlips(const SpatialOrientation::ValidCoordinateOrientationFlags fixed_orient,
                                const SpatialOrientation::ValidCoordinateOrientationFlags moving_orient)
{
  // std::cout <<"DEBUG Received Codes " <<fixed_orient <<"  and  "
  // <<moving_orient <<std::endl;
  // 3-dimensional version of code system only.  The 3-axis testing is unrolled.
  const unsigned int NumDims = 3;                  // InputImageDimension is
                                                   // regarded as 3.
  const unsigned int CodeField = 15;               // 4 bits wide
  const unsigned int CodeAxisField = 14;           // 3 bits wide, above the
                                                   // 0-place bit.
  const unsigned int CodeAxisIncreasingField = 1;
  unsigned int       fixed_codes[NumDims];
  unsigned int       moving_codes[NumDims];

  fixed_codes[0]  = ( fixed_orient  >> SpatialOrientation::ITK_COORDINATE_PrimaryMinor ) & CodeField;
  fixed_codes[1]  = ( fixed_orient  >> SpatialOrientation::ITK_COORDINATE_SecondaryMinor ) & CodeField;
  fixed_codes[2]  = ( fixed_orient  >> SpatialOrientation::ITK_COORDINATE_TertiaryMinor ) & CodeField;
  moving_codes[0] = ( moving_orient >> SpatialOrientation::ITK_COORDINATE_PrimaryMinor ) & CodeField;
  moving_codes[1] = ( moving_orient >> SpatialOrientation::ITK_COORDINATE_SecondaryMinor ) & CodeField;
  moving_codes[2] = ( moving_orient >> SpatialOrientation::ITK_COORDINATE_TertiaryMinor ) & CodeField;
  // std::cout <<"DEBUG Fixed Codes " <<fixed_codes[0]  <<",  " <<fixed_codes[1]
  //  <<"  and  " <<fixed_codes[2]  <<std::endl;
  // std::cout <<"DEBUG Moving Codes " <<moving_codes[0]  <<",  "
  // <<moving_codes[1]  <<"  and  " <<moving_codes[2]  <<std::endl;

  // i, j, k will be the indexes in the Majorness code of the axes to flip;
  // they encode the axes as the reader will find them, 0 is the lowest order
  // axis of whatever spatial interpretation, and 2 is the highest order axis.
  //  Perhaps rename them moving_image_reader_axis_i, etc.
  for( unsigned int i = 0; i < NumDims - 1; i++ )
    {
    if( ( fixed_codes[i] & CodeAxisField ) != ( moving_codes[i] & CodeAxisField ) )
      {
      for( unsigned int j = 0; j < NumDims; j++ )
        {
        if( ( moving_codes[i] & CodeAxisField ) == ( fixed_codes[j] & CodeAxisField ) )
          {
          if( i == j )
            { // Axis i is already in place.
            continue;
            }
          else if( ( moving_codes[j] & CodeAxisField ) == ( fixed_codes[i] & CodeAxisField ) )
            { // The cyclic permutation (i j) applies.  Therefore the remainder
              // is (k), i.e., stationary.
            m_PermuteOrder[i] = j;
            m_PermuteOrder[j] = i;
            // std::cout <<"DEBUG DeterminePermutationsAndFlips: coded the swap
            // of axes " <<i <<" and " <<j <<std::endl;
            }
          else
            { // Need to work out an (i j k) cyclic permutation:
            for( unsigned int k = 0; k < NumDims; k++ )
              {
              if( ( moving_codes[j] & CodeAxisField ) == ( fixed_codes[k] & CodeAxisField ) )
                {
                // At this point, we can pick off (i j k).
                m_PermuteOrder[i] = j;
                m_PermuteOrder[j] = k;
                m_PermuteOrder[k] = i;
                // std::cout <<"DEBUG DeterminePermutationsAndFlips: coded the
                // swap of axes " <<i <<", " <<j <<" and " <<k <<std::endl;
                break;
                }
              }
            // Effectively, if (k==3) continue;
            }
          break;
          }
        }
      // Effectively, if (j==3) continue;
      }
    }
  for( unsigned int i = 0; i < NumDims; i++ )
    {
    const unsigned int j = m_PermuteOrder[i];
    // std::cout <<"DEBUG comparing fixed code " <<fixed_codes[i] <<" with
    // moving code " <<moving_codes[j] <<std::endl;
    if( ( moving_codes[j] & CodeAxisIncreasingField ) != ( fixed_codes[i] & CodeAxisIncreasingField ) )
      {
      m_FlipAxes[i] = true;
      // std::cout <<"DEBUG DeterminePermutationsAndFlips: coded the flip of
      // axis " <<i <<std::endl;
      }
    }
  // /////////////////////////////////////////////////////////
  // Modified By Peng Cheng
  if( InputImageDimension > 3 )
    {
    for( int i = 3; i < InputImageDimension; i++ )
      {
      m_PermuteOrder[i] = i;
      m_FlipAxes[i] = false;
      }
    }
  // /////////////////////////////////////////////////////////
}

/**
 *
 */
template <class TInputImage, class TOutputImage>
void
OrientScalarImageFilter<TInputImage, TOutputImage>
::SetGivenCoordinateOrientation(CoordinateOrientationCode newCode)
{
  m_GivenCoordinateOrientation = newCode;
  for( unsigned int j = 0; j < InputImageDimension; j++ )
    {
    m_PermuteOrder[j] = j;
    }

  m_FlipAxes.Fill( false );

  this->DeterminePermutationsAndFlips(m_DesiredCoordinateOrientation, m_GivenCoordinateOrientation);
}

/**
 *
 */
template <class TInputImage, class TOutputImage>
void
OrientScalarImageFilter<TInputImage, TOutputImage>
::SetDesiredCoordinateOrientation(CoordinateOrientationCode newCode)
{
  m_DesiredCoordinateOrientation = newCode;
  for( unsigned int j = 0; j < InputImageDimension; j++ )
    {
    m_PermuteOrder[j] = j;
    }

  m_FlipAxes.Fill( false );

  this->DeterminePermutationsAndFlips(m_DesiredCoordinateOrientation, m_GivenCoordinateOrientation);
}

/** Returns true if a permute is required. Return false otherwise */
template <class TInputImage, class TOutputImage>
bool
OrientScalarImageFilter<TInputImage, TOutputImage>
::NeedToPermute()
{
  for( unsigned int j = 0; j < InputImageDimension; j++ )
    {
    if( m_PermuteOrder[j] != j )
      {
      return true;
      }
    }
  return false;
}

/** Returns true if flipping is required. Return false otherwise */
template <class TInputImage, class TOutputImage>
bool
OrientScalarImageFilter<TInputImage, TOutputImage>
::NeedToFlip()
{
  for( unsigned int j = 0; j < InputImageDimension; j++ )
    {
    if( m_FlipAxes[j] )
      {
      return true;
      }
    }
  return false;
}

template <class TInputImage, class TOutputImage>
void
OrientScalarImageFilter<TInputImage, TOutputImage>
::GenerateData()
{
  // Create a process accumulator for tracking the progress of this minipipeline
  typename ProgressAccumulator::Pointer progress = ProgressAccumulator::New();

  progress->SetMiniPipelineFilter(this);

  // Allocate the output
  this->AllocateOutputs();

  // The indented stuff here is from bkItkPermuteAxes.txx (brains2)

  // /////////////////////////////////////////////////////////
  // Modified by Peng Cheng
  // const unsigned int Dimension = 3;
  const unsigned int Dimension = InputImageDimension;
  // /////////////////////////////////////////////////////////

  typedef typename InputImageType::PixelType InputPixelType;
  typedef Image<InputPixelType, Dimension>   CubeImageType;

  typename InputImageType::SizeType originalSize;
  originalSize = this->GetInput()->GetLargestPossibleRegion().GetSize();
  int dims[Dimension];
  for( unsigned int i = 0; i < Dimension; i++ )
    {
    dims[i] = originalSize[i];
    }

  /* Now we are going to build up the ITK pipeline for processing */

  // Convenient typedefs
  typedef ConstantPadScalarImageFilter<InputImageType, CubeImageType> PadInputFilterType;
  typedef ExtractImageFilter<CubeImageType, CubeImageType>            ExtractFilterType;
  typedef FlipImageFilter<CubeImageType>                              FlipFilterType;
  typedef CastImageFilter<CubeImageType, OutputImageType>             CastToOutputFilterType;

  // Create the casting filters
  typename PadInputFilterType::Pointer     to_cube_padded = PadInputFilterType::New();
  typename ExtractFilterType::Pointer      from_cube = ExtractFilterType::New();
  typename CastToOutputFilterType::Pointer to_output = CastToOutputFilterType::New();

  // ///////////////////////////////////////////////////////////
  // Modified By Peng Cheng
  int maxDim = dims[0];
  for( int i = 1; i < Dimension; i++ )
    {
    if( maxDim < (int)dims[i] )
      {
      maxDim = dims[i];
      }
    }
  unsigned long sizeData[Dimension];
  for( int i = 0; i < Dimension; i++ )
    {
    sizeData[i] = ( maxDim - dims[i] );
    }
  // //////////////////////////////////////////////////////

  // to_cube_padded->SetPadLowerBound( sizeData );
  to_cube_padded->SetPadUpperBound( sizeData );

  // //////////////////////////////////////////////////////
  // Modified By Peng Cheng
  InputPixelType p = 0;
  /*
  if(InputPixelType::GetNumberOfComponents()>1){
    p.Fill(0);
  }
  else{
    p=0;//NumericTraits<InputPixelType>::Zero;
  }
  */
  to_cube_padded->SetConstant( p );
  // //////////////////////////////////////////////////////

  typedef PermuteAxesImageFilter<CubeImageType> PermuteFilterType;

  typename PermuteFilterType::Pointer permuteAxesFilter = PermuteFilterType::New();
  typename FlipFilterType::Pointer    flipAxesFilter  = FlipFilterType::New();

  permuteAxesFilter->SetOrder( m_PermuteOrder );
  permuteAxesFilter->ReleaseDataFlagOn();

  /* Set the ITK image size based on the size of the BRAINS2 image */
  typename InputImageType::SizeType xsize;
  // /////////////////////////////////////////////////////////////////
  // Modified By Peng Cheng
  for( int i = 0; i < Dimension; i++ )
    {
    xsize[i]  = (int)dims[m_PermuteOrder[i]];   // size along X
    }
  // /////////////////////////////////////////////////////////////////

  typename InputImageType::IndexType xstart;
  xstart.Fill(0);

  typename InputImageType::RegionType xregion;
  xregion.SetIndex( xstart );
  xregion.SetSize( xsize );

  from_cube->SetExtractionRegion( xregion );
  from_cube->ReleaseDataFlagOn();

  flipAxesFilter->SetFlipAxes( m_FlipAxes );
  flipAxesFilter->ReleaseDataFlagOn();
  // std::cout <<"DEBUG: FlipAxes are " <<flipAxesFilter->GetFlipAxes()
  // <<std::endl;

  // Connect the pipeline
  to_cube_padded->SetInput( this->GetInput() );
  permuteAxesFilter->SetInput( to_cube_padded->GetOutput() );
  from_cube->SetInput( permuteAxesFilter->GetOutput() );
  flipAxesFilter->SetInput( from_cube->GetOutput() );
  to_output->SetInput( flipAxesFilter->GetOutput() );
  to_output->ReleaseDataFlagOn();

  // std::cout <<"DEBUG: before to_output->GraftOutput( this->GetOutput() );"
  // <<std::endl;
  // graft our output to the subtract filter to force the proper regions
  // to be generated
  to_output->GraftOutput( this->GetOutput() );

  // run the algorithm
  // March down the pipeline to show what the problem is.
  progress->RegisterInternalFilter(to_output, 1.0f);

  flipAxesFilter->Update();

    {
    float flipOrigin[Dimension];
    for( unsigned int i = 0; i < Dimension; i++ )
      {
      flipOrigin[i] = 0.0;
      }
    flipAxesFilter->GetOutput()->SetOrigin(flipOrigin);
    }

  // std::cout <<"DEBUG: before to_output->Update();" <<std::endl;
  to_output->Update();

  // graft the output of the subtract filter back onto this filter's
  // output. this is needed to get the appropriate regions passed
  // back.
  // std::cout <<"DEBUG: before this->GraftOutput( to_output->GetOutput() );"
  // <<std::endl;
    {
    typename CastToOutputFilterType::OutputImageType::Pointer tempImage = to_output->GetOutput();
    //  std::cout <<(tempImage) <<std::endl;
    }
  this->GraftOutput( to_output->GetOutput() );
  this->GetOutput()->SetMetaDataDictionary( this->GetInput()->GetMetaDataDictionary() );
  itk::EncapsulateMetaData<SpatialOrientation::ValidCoordinateOrientationFlags>(
    this->GetOutput()->GetMetaDataDictionary(), ITK_CoordinateOrientation, m_DesiredCoordinateOrientation );
}

/**
 *
 */
template <class TInputImage, class TOutputImage>
void
OrientScalarImageFilter<TInputImage, TOutputImage>
::GenerateOutputInformation()
{
  // call the superclass' implementation of this method
  Superclass::GenerateOutputInformation();

  // get pointers to the input and output
  InputImageConstPointer inputPtr  = this->GetInput();
  OutputImagePointer     outputPtr = this->GetOutput();

  if( !inputPtr || !outputPtr )
    {
    return;
    }

  // We need to compute the output spacing, the output image size, and the
  // output image start index.
  unsigned int i;
  const typename TInputImage::SpacingType inputSpacing     = inputPtr->GetSpacing();
  const typename TInputImage::SizeType    & inputSize        = inputPtr->GetLargestPossibleRegion().GetSize();
  const typename TInputImage::IndexType   & inputStartIndex  = inputPtr->GetLargestPossibleRegion().GetIndex();

  float outputSpacing[TOutputImage::ImageDimension];
  typename TOutputImage::SizeType  outputSize;
  typename TOutputImage::IndexType outputStartIndex;
  for( i = 0; i < TOutputImage::ImageDimension; i++ )
    {
    outputSpacing[i]    =    inputSpacing[m_PermuteOrder[i]];
    outputSize[i]       =       inputSize[m_PermuteOrder[i]];
    outputStartIndex[i] = inputStartIndex[m_PermuteOrder[i]];
    }

  outputPtr->SetSpacing( outputSpacing );

  typename TOutputImage::RegionType outputLargestPossibleRegion;
  outputLargestPossibleRegion.SetSize( outputSize );
  outputLargestPossibleRegion.SetIndex( outputStartIndex );

  outputPtr->SetLargestPossibleRegion( outputLargestPossibleRegion );
}

template <class TInputImage, class TOutputImage>
void
OrientScalarImageFilter<TInputImage, TOutputImage>
::PrintSelf(std::ostream & os, Indent indent) const
{
  Superclass::PrintSelf(os, indent);

  os << indent << "Desired Orientation Code: "
     << m_DesiredCoordinateOrientation
     << std::endl;
  os << indent << "Given Orientation Code: "
     << m_GivenCoordinateOrientation
     << std::endl;
  os << indent << "Permute Axes: "
     << m_PermuteOrder
     << std::endl;
  os << indent << "Flip Axes: "
     << m_FlipAxes
     << std::endl;
}

} // end namespace itk
#endif
