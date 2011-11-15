/*=========================================================================

  Program:   Insight Segmentation & Registration Toolkit
  Module:    $RCSfile: itkLabelToRGBImageFilter.h,v $
  Language:  C++
  Date:      $Date: 2009-07-07 12:27:34 $
  Version:   $Revision: 1.10 $

  Copyright (c) Insight Software Consortium. All rights reserved.
  See ITKCopyright.txt or http://www.itk.org/HTML/Copyright.htm for details.

     This software is distributed WITHOUT ANY WARRANTY; without even
     the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
     PURPOSE.  See the above copyright notices for more information.

=========================================================================*/

#ifndef __itkLabelToRGBImageFilter_h
#define __itkLabelToRGBImageFilter_h

#include "itkUnaryFunctorImageFilter.h"
#include "itkLabelToRGBFunctor.h"

namespace itk
{
/** \class LabelToRGBImageFilter
 * \brief Apply a colormap to a label image
 *
 * Apply a colormap to a label image. The set of colors
 * is a good selection of distinct colors. The user can choose to use a background
 * value. In that case, a gray pixel with the same intensity than the background
 * label is produced.
 *
 * \author Gaetan Lehmann. Biologie du Developpement et de la Reproduction, INRA de Jouy-en-Josas, France.
 * \author Richard Beare. Department of Medicine, Monash University, Melbourne, Australia.
 *
 * \sa ScalarToRGBPixelFunctor LabelOverlayImageFilter
 * \ingroup Multithreaded
 *
 */
template <class TLabelImage, typename  TOutputImage>
class ITK_EXPORT LabelToRGBImageFilter :
  public
  UnaryFunctorImageFilter<TLabelImage, TOutputImage,
                          Functor::LabelToRGBFunctor<
                            typename TLabelImage::PixelType,
                            typename TOutputImage::PixelType>   >
{
public:
  /** Standard class typedefs. */
  typedef LabelToRGBImageFilter    Self;
  typedef SmartPointer<Self>       Pointer;
  typedef SmartPointer<const Self> ConstPointer;

  typedef UnaryFunctorImageFilter<TLabelImage, TOutputImage,
                                  Functor::LabelToRGBFunctor<
                                    typename TLabelImage::PixelType,
                                    typename TOutputImage::PixelType>   >  Superclass;

  typedef TOutputImage OutputImageType;
  typedef TLabelImage  LabelImageType;

  typedef typename TOutputImage::PixelType                   OutputPixelType;
  typedef typename TLabelImage::PixelType                    LabelPixelType;
  typedef typename NumericTraits<OutputPixelType>::ValueType OutputPixelValueType;

  /** Runtime information support. */
  itkTypeMacro(LabelToRGBImageFilter, UnaryFunctorImageFilter);

  /** Method for creation through the object factory. */
  itkNewMacro(Self);

  /** Set/Get the background value */
  itkSetMacro(BackgroundValue, LabelPixelType);
  itkGetConstReferenceMacro(BackgroundValue, LabelPixelType);

  /** Set/Get the background color in the output image */
  itkSetMacro(BackgroundColor, OutputPixelType);
  itkGetConstReferenceMacro(BackgroundColor, OutputPixelType);

  /** Empty the color LUT container */
  void ResetColors();

  /** Get number of colors in the LUT container */
  unsigned int GetNumberOfColors() const;

  /** Type of the color component */
  typedef typename OutputPixelType::ComponentType ComponentType;

  /** Add color to the LUT container */
  void AddColor(ComponentType r, ComponentType g, ComponentType b);

protected:
  LabelToRGBImageFilter();
  virtual ~LabelToRGBImageFilter()
  {
  }

  /** Process to execute before entering the multithreaded section */
  void BeforeThreadedGenerateData(void);

  /** Print internal ivars */
  void PrintSelf(std::ostream & os, Indent indent) const;

private:
  LabelToRGBImageFilter(const Self &); // purposely not implemented
  void operator=(const Self &);        // purposely not implemented

  OutputPixelType m_BackgroundColor;
  LabelPixelType  m_BackgroundValue;
};
} // end namespace itk

#ifndef ITK_MANUAL_INSTANTIATION
#include "itkLabelToRGBImageFilter.hxx"
#endif

#endif
