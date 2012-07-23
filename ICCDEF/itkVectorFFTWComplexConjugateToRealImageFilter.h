/*
 *  itkVectorFFTComplexConjugateToRealImageFilter.h
 *  iccdefRegistrationNew
 *
 *  Created by Yongqiang Zhao on 5/6/09.
 *  Copyright 2009 UI. All rights reserved.
 *
 */

#ifndef __itkVectorFFTWComplexConjugateToRealImageFilter_h
#define __itkVectorFFTWComplexConjugateToRealImageFilter_h

#include <itkImageToImageFilter.h>
#include <itkImage.h>
#include <complex>

//
// FFTWCommon defines proxy classes based on data types
#if defined(USE_FFTWF) || defined(USE_FFTWD)
#include "fftw3.h"
#endif

namespace itk
{

template <typename TPixel, unsigned int VDimension = 3>
class VectorFFTWComplexConjugateToRealImageFilter :
  public ImageToImageFilter<Image<Vector<std::complex<typename TPixel::ValueType>, 3>, VDimension>,
                            Image<TPixel, VDimension> >
{
public:
  /** Standard class typedefs.*/
  typedef Image<Vector<std::complex<typename TPixel::ValueType>, 3>, VDimension> TInputImageType;
  typedef Image<TPixel, VDimension>                                              TOutputImageType;

  typedef VectorFFTWComplexConjugateToRealImageFilter           Self;
  typedef ImageToImageFilter<TInputImageType, TOutputImageType> Superclass;
  typedef SmartPointer<Self>                                    Pointer;
  typedef SmartPointer<const Self>                              ConstPointer;
  //

  /** Method for creation through the object factory. */
  itkNewMacro(Self);

  /** Run-time type information (and related methods). */
  itkTypeMacro(VectorFFTWComplexConjugateToRealImageFilter,
               ImageToImageFilter);

  /** Image type typedef support. */
  typedef TInputImageType              ImageType;
  typedef typename ImageType::SizeType ImageSizeType;
  virtual void GenerateOutputInformation(); // figure out allocation for output image

  virtual void GenerateInputRequestedRegion();

  //
  // these should be defined in every FFT filter class
  virtual void GenerateData();  // generates output from input

  virtual bool FullMatrix();

  void SetActualXDimensionIsOdd(bool isodd)
  {
    m_ActualXDimensionIsOdd = isodd;
  }

  void SetActualXDimensionIsOddOn()
  {
    this->SetActualXDimensionIsOdd(true);
  }

  void SetActualXDimensionIsOddOff()
  {
    this->SetActualXDimensionIsOdd(false);
  }

  bool ActualXDimensionIsOdd()
  {
    return m_ActualXDimensionIsOdd;
  }

protected:
  VectorFFTWComplexConjugateToRealImageFilter() : m_PlanComputed(false),
    m_LastImageSize(0),
    m_InputBuffer(0),
    m_OutputBuffer(0),
    m_ActualXDimensionIsOdd(false)
  {
  }

  virtual ~VectorFFTWComplexConjugateToRealImageFilter()
  {
    if( m_PlanComputed )
      {
      fftwf_destroy_plan(this->m_Plan);
      delete [] m_InputBuffer;
      delete [] m_OutputBuffer;
      }
  }

private:
  VectorFFTWComplexConjugateToRealImageFilter(const Self &); // purposely not implemented
  void operator=(const Self &);                              // purposely not implemented

  bool         m_PlanComputed;
  fftwf_plan   m_Plan;
  unsigned int m_LastImageSize;
  // local storage needed to keep fftw from scribbling on
  fftwf_complex * m_InputBuffer;
  float *         m_OutputBuffer;
  bool            m_ActualXDimensionIsOdd;
};

} // namespace itk

#ifndef ITK_MANUAL_INSTANTIATION
#include "itkVectorFFTWComplexConjugateToRealImageFilter.txx"
#endif

#endif // __itkVectorFFTWComplexConjugateToRealImageFilter_h
