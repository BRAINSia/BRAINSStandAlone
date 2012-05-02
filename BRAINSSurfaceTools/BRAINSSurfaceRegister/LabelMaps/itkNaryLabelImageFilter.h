/*=========================================================================

  Program:   Insight Segmentation & Registration Toolkit
  Module:    $RCSfile: itkNaryLabelImageFilter.h,v $
  Language:  C++
  Date:      $Date: 2006/10/25 12:12:56 $
  Version:   $Revision: 1.33 $

  Copyright (c) Insight Software Consortium. All rights reserved.
  See ITKCopyright.txt or http://www.itk.org/HTML/Copyright.htm for details.

     This software is distributed WITHOUT ANY WARRANTY; without even 
     the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
     PURPOSE.  See the above copyright notices for more information.

=========================================================================*/
#ifndef __itkNaryLabelImageFilter_h
#define __itkNaryLabelImageFilter_h

#include "itkNaryFunctorImageFilter.h"
#include "itkNumericTraits.h"

namespace itk
{
  
/** \class NaryLabelImageFilter
 * \brief Label combination from several images
 *
 * This filter take all the labels which are not background pixels in all the input images, and
 * put them in the output image. The labels may be shifted on a per image basis, by calling
 * SetShift(OutputPixelType) with a value different of 0. By default, the labels are not shifted.
 * This filter take one or more images as input, and produce a
 * single output image.
 * The SetIgnoreCollision(bool) method let the user choose to ignore the
 * labeled region collision or not. By default, they are ignored.
 * The SetBackgroundValue(OutputPixelType) let the user set the
 * value of the background label.
 * 
 * \ingroup  Multithreaded
 */

namespace Functor {  
  
template< class TInput, class TOutput >
class NaryLabel
{
public:
  NaryLabel() {}
  ~NaryLabel() {}
  inline TOutput operator()( const std::vector< TInput > & B)
  {
  	TOutput ret = static_cast<TOutput>(m_BackgroundValue);
  	bool labelFound = false;
  	
    for( int i=0; i<B.size(); i++ )
      {
      if( B[i] != m_BackgroundValue )
        {
        if( !m_IgnoreCollision && labelFound )
          {
          itkGenericExceptionMacro( << "Label collision detected." );
          }

        ret = static_cast<TOutput>(B[i] + m_Shift * i);
        labelFound = true;
        }
      }
    return ret;
  }

  bool operator!= (const NaryLabel& n) const
  {
    return n.m_BackgroundValue != m_BackgroundValue || n.m_Shift != m_Shift;
  }

  TInput m_BackgroundValue;
  TOutput m_Shift;
  bool m_IgnoreCollision;
}; 
}

template <class TInputImage, class TOutputImage>
class ITK_EXPORT NaryLabelImageFilter :
    public
NaryFunctorImageFilter<TInputImage, TOutputImage, 
                       Functor::NaryLabel<typename TInputImage::PixelType, typename TOutputImage::PixelType > > 
{
public:
  /** Standard class typedefs. */
  typedef NaryLabelImageFilter  Self;
  typedef NaryFunctorImageFilter<TInputImage, TOutputImage, 
                       Functor::NaryLabel<typename TInputImage::PixelType, typename TOutputImage::PixelType > >   Superclass;
  typedef SmartPointer<Self>   Pointer;
  typedef SmartPointer<const Self>  ConstPointer;

  /** Some convenient typedefs. */
  typedef TInputImage InputImageType;
  typedef typename InputImageType::Pointer         InputImagePointer;
  typedef typename InputImageType::ConstPointer    InputImageConstPointer;
  typedef typename InputImageType::RegionType      InputImageRegionType;
  typedef typename InputImageType::PixelType       InputImagePixelType;

  typedef TOutputImage OutputImageType;
  typedef typename OutputImageType::Pointer         OutputImagePointer;
  typedef typename OutputImageType::ConstPointer    OutputImageConstPointer;
  typedef typename OutputImageType::RegionType      OutputImageRegionType;
  typedef typename OutputImageType::PixelType       OutputImagePixelType;

  /** Method for creation through the object factory. */
  itkNewMacro(Self);

#ifdef ITK_USE_CONCEPT_CHECKING
  /** Begin concept checking */
  itkConceptMacro(InputHasZeroCheck,
    (Concept::HasZero<typename TInputImage::PixelType>));
  /** End concept checking */
#endif

  /**
   * Set/Get the value used as "background" in the images.
   * Defaults to NumericTraits<PixelType>::Zero.
   */
  itkSetMacro(BackgroundValue, InputImagePixelType);
  itkGetConstMacro(BackgroundValue, InputImagePixelType);

  itkSetMacro(Shift, InputImagePixelType);
  itkGetConstMacro(Shift, InputImagePixelType);

  itkSetMacro(IgnoreCollision, bool);
  itkGetConstMacro(IgnoreCollision, bool);
  itkBooleanMacro(IgnoreCollision);


protected:
  NaryLabelImageFilter()
    {
    m_BackgroundValue = NumericTraits< InputImagePixelType >::Zero;
    m_Shift = NumericTraits< OutputImagePixelType >::Zero;
    m_IgnoreCollision = true;
    }

  virtual ~NaryLabelImageFilter() {}

  void GenerateData()
    {
    this->GetFunctor().m_BackgroundValue = m_BackgroundValue;
    this->GetFunctor().m_Shift = m_Shift;
    this->GetFunctor().m_IgnoreCollision = m_IgnoreCollision;
    Superclass::GenerateData();
    }

  void PrintSelf( std::ostream& os, Indent indent) const
    {
    Superclass::PrintSelf( os, indent );
    os << indent << "Background Value: " << static_cast<typename NumericTraits<InputImagePixelType>::PrintType>(m_BackgroundValue) << std::endl;
    os << indent << "Shift: " << static_cast<typename NumericTraits<OutputImagePixelType>::PrintType>(m_Shift) << std::endl;
    os << indent << "Ignore Collision: " << static_cast<typename NumericTraits<bool>::PrintType>(m_IgnoreCollision) << std::endl;
    }


private:
  NaryLabelImageFilter(const Self&); //purposely not implemented
  void operator=(const Self&); //purposely not implemented

  InputImagePixelType m_BackgroundValue;
  OutputImagePixelType m_Shift;
  bool m_IgnoreCollision;
};

} // end namespace itk


#endif
