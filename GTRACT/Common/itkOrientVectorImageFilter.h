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

#ifndef __itkOrientVectorImageFilter_h
#define __itkOrientVectorImageFilter_h

#include "itkImageToImageFilter.h"
#include "itkIOCommon.h"
#include "itkPermuteAxesImageFilter.h"
#include "itkFlipImageFilter.h"
#include "itkSpatialOrientation.h"
// #include "itkNumericTraits.h"

namespace itk
{
/** \class OrientVectorImageFilter
 * \brief Permute axes and then flip images as needed to obtain
 *  agreement in coordinateOrientation codes.
 *
 * This class satisfies a common requirement in medical imaging, which
 * is to properly orient a 3 dimensional image with respect to anatomical
 * features.  Due to the wide variety of hardware used to generate 3D images
 * of human anatomy, and the even wider variety of image processing software,
 * it is often necessary to re-orient image volume data.
 *
 * OrientVectorImageFilter depends on a set of constants that describe all possible
 * permutations of Axes. These reside in itkSpatialOrientation.h. These are
 * labeled according to the following scheme:
 * Directions are labeled in terms of following pairs:
 *   - Left and Right (Subject's left and right)
 *   - Anterior and Posterior (Subject's front and back)
 *   - Inferior and Superior (Subject's bottom and top, i.e. feet and head)
 *
 * The initials of these directions are used in a 3 letter code in the
 * enumerated type itk::SpatialOrientation::ValidCoordinateOrientationFlags.
 * The initials are given fastest moving index first, second fastest second,
 * third fastest third.
 * Examples:
 *  - ITK_COORDINATE_ORIENTATION_RIP
 *    -#Right to Left varies fastest (0th pixel on Subject's right)
 *    -#Inferior to Superior varies second fastest
 *    -#Posterior to Anterior varies slowest.
 *  - ITK_COORDINATE_ORIENTATION_LSA
 *    -#Left to Right varies fastest (0th pixel on Subject's left)
 *    -#Superior to Inferior varies second fastest
 *    -#Anterior to Posterior varies slower
 *
 * In order to use this filter, you need to supply an input
 * image, the current orientation of the input image (set with
 * SetGivenCoordinateOrientation) and the desired orientation
 * (set with SetDesiredCoordinateOrientation).
 *
 * When reading image files that define the coordinate orientation
 * of the image, the current orientation is stored in the MetadataDictionary
 * for the itk::Image object created from the file.
 *
 * As an example, if you wished to keep all images within your program in the
 * orientation corresponding to the Analyze file format's 'CORONAL' orientation
 * you could do something like the following
 *
 * \code
 * #include "itkAnalyzeImageIO.h"
 * #include "itkMetaDataObject.h"
 * #include "itkImage.h"
 * #include "itkSpatialOrientation.h"
 * #include "itkOrientVectorImageFilter.h"
 * #include "itkIOCommon.h"
 * typedef itk::Image<unsigned char,3> ImageType;
 * typedef itk::ImageFileReader< TstImageType > ImageReaderType ;
 * ImageType::Pointer ReadAnalyzeFile(const char *path)
 * {
 *   itk::AnalyzeImageIO::Pointer io = itk::AnalyzeImageIO::New();
 *   ImageReaderType::Pointer fileReader = ImageReaderType::New();
 *   fileReader->SetImageIO(io);
 *   fileReader->SetFileName(path);
 *   fileReader->Update();
 *   ImageType::Pointer rval = fileReader->GetOutput();
 *
 *   itk::SpatialOrientation::ValidCoordinateOrientationFlags fileOrientation;
 *   itk::ExposeMetaData<itk::SpatialOrientation::ValidCoordinateOrientationFlags>
 *     (rval->GetMetaDataDictionary(),itk::ITK_CoordinateOrientation,fileOrientation);
 *   itk::OrientVectorImageFilter<ImageType,ImageType>::Pointer orienter =
 *     itk::OrientVectorImageFilter<ImageType,ImageType>::New();
 *   orienter->SetGivenCoordinateOrientation(fileOrientation);
 *   orienter->SetDesiredCoordinateOrientation(itk::SpatialOrientation::ITK_COORDINATE_ORIENTATION_RIP);
 *   orienter->SetInput(rval);
 *   orienter->Update();
 *   rval = orienter->GetOutput();
 *   return rval;
 * }
 * \endcode
 */
template <class TInputImage, class TOutputImage>
class ITK_EXPORT OrientVectorImageFilter :
  public ImageToImageFilter<TInputImage, TOutputImage>
{
public:
  /** Standard class typedefs. */
  typedef OrientVectorImageFilter Self;
  typedef ImageToImageFilter<TInputImage, TOutputImage>
  Superclass;
  typedef SmartPointer<Self>       Pointer;
  typedef SmartPointer<const Self> ConstPointer;

  /** Some convenient typedefs. */
  typedef TInputImage                            InputImageType;
  typedef TOutputImage                           OutputImageType;
  typedef typename InputImageType::Pointer       InputImagePointer;
  typedef typename InputImageType::ConstPointer  InputImageConstPointer;
  typedef typename InputImageType::RegionType    InputImageRegionType;
  typedef typename InputImageType::PixelType     InputImagePixelType;
  typedef typename OutputImageType::Pointer      OutputImagePointer;
  typedef typename OutputImageType::ConstPointer OutputImageConstPointer;
  typedef typename OutputImageType::RegionType   OutputImageRegionType;
  typedef typename OutputImageType::PixelType    OutputImagePixelType;
  typedef SpatialOrientation::ValidCoordinateOrientationFlags
  CoordinateOrientationCode;
  /** Axes permuter type. */
  typedef PermuteAxesImageFilter<TInputImage>          PermuterType;
  typedef typename PermuterType::PermuteOrderArrayType PermuteOrderArrayType;

  /** Axes flipper type. */
  typedef FlipImageFilter<TInputImage>            FlipperType;
  typedef typename FlipperType::FlipAxesArrayType FlipAxesArrayType;

  /** ImageDimension constants */
  itkStaticConstMacro(InputImageDimension, unsigned int,
                      TInputImage::ImageDimension);
  itkStaticConstMacro(OutputImageDimension, unsigned int,
                      TOutputImage::ImageDimension);

  /** Standard New method. */
  itkNewMacro(Self);

  /** Runtime information support. */
  itkTypeMacro(OrientVectorImageFilter, ImageToImageFilter);

  /** Set/Get the orienttion codes to define the coordinate transform. */
  itkGetMacro(GivenCoordinateOrientation, CoordinateOrientationCode);
  void SetGivenCoordinateOrientation(CoordinateOrientationCode newCode);

  itkGetMacro(DesiredCoordinateOrientation, CoordinateOrientationCode);
  void SetDesiredCoordinateOrientation(CoordinateOrientationCode newCode);

  /** Get axes permute order. */
  itkGetConstReferenceMacro( PermuteOrder, PermuteOrderArrayType );

  /** Get flip axes. */
  itkGetConstReferenceMacro( FlipAxes, FlipAxesArrayType );

  /** OrientVectorImageFilter produces an image which is a different
   * dimensionality than its input image, in general.
   *As such, OrientVectorImageFilter needs to provide an
   * implementation for GenerateOutputInformation() in order to inform
   * the pipeline execution model.  The original documentation of this
   * method is below.
   * \sa ProcessObject::GenerateOutputInformaton() */
  virtual void GenerateOutputInformation();

protected:
  OrientVectorImageFilter();
  ~OrientVectorImageFilter()
  {
  }
  void PrintSelf(std::ostream & os, Indent indent) const;

  /** OrientVectorImageFilter needs the entire input be
   * available. Thus, it needs to provide an implementation of
   * GenerateInputRequestedRegion(). */
  void GenerateInputRequestedRegion();

  /** OrientVectorImageFilter will produce the entire output. */
  void EnlargeOutputRequestedRegion( DataObject * itkNotUsed(output) );

  /*** Member functions used by GenerateData: */
  void DeterminePermutationsAndFlips(const SpatialOrientation::ValidCoordinateOrientationFlags fixed_orient,
                                     const SpatialOrientation::ValidCoordinateOrientationFlags moving_orient);

  bool NeedToPermute();

  bool NeedToFlip();

  /** Single-threaded version of GenerateData.  This filter delegates
   * to PermuteAxesImageFilter and FlipImageFilter. */
  void GenerateData();

private:
  OrientVectorImageFilter(const Self &); // purposely not implemented
  void operator=(const Self &);          // purposely not implemented

  CoordinateOrientationCode m_GivenCoordinateOrientation;
  CoordinateOrientationCode m_DesiredCoordinateOrientation;

  PermuteOrderArrayType m_PermuteOrder;
  FlipAxesArrayType     m_FlipAxes;
};  // end of class
} // end namespace itk

#ifndef ITK_MANUAL_INSTANTIATION
#include "itkOrientVectorImageFilter.hxx"
#endif

#endif
