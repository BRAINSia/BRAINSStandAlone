
#ifndef __itkICCIterativeInverseDeformationFieldImageFilter_h
#define __itkICCIterativeInverseDeformationFieldImageFilter_h


#include "itkImageToImageFilter.h"

#include "itkWarpVectorImageFilter.h"
#include "itkVectorLinearInterpolateImageFunction.h"
#include "itkImageRegionIterator.h"
#include "itkTimeProbe.h"

namespace itk
{
 
/** \class ICCIterativeInverseDeformationFieldImageFilter
 * \brief Computes the inverse of a deformation field.
 *
 * ICCIterativeInverseDeformationFieldImageFilter takes a deformation field as input and
 * computes the deformation field that is its inverse. If the input deformation
 * field was mapping coordinates from a space A into a space B, the output of
 * this filter will map coordinates from the space B into the space A.
 * 
 * The algorithm implemented in this filter uses an iterative method for
 * progresively refining the values of the inverse field. Starting from the
 * direct field, at every pixel the direct mapping of this point is found, and
 * a the nevative of the current deformation is stored in the inverse field at
 * the nearest pixel. Then, subsequent iterations verify if any of the neigbor pixels
 * provide a better return to the current pixel, in which case its value is taken for
 * updating the vector in the inverse field.
 *
 * This method was discussed in the users-list during February 2004.
 *
 * \author  Corinne Mattmann
 *
 */

template < class TInputImage, class TOutputImage >
class ITK_EXPORT ICCIterativeInverseDeformationFieldImageFilter :
    public ImageToImageFilter<TInputImage,TOutputImage> 
{
public:
  /** Standard class typedefs. */
  typedef ICCIterativeInverseDeformationFieldImageFilter   Self;
  typedef ImageToImageFilter<TInputImage,TOutputImage>  Superclass;
  typedef SmartPointer<Self>                            Pointer;
  typedef SmartPointer<const Self>                      ConstPointer;

  /** Method for creation through the object factory. */
  itkNewMacro(Self);

  /** Run-time type information (and related methods). */
  itkTypeMacro(ICCIterativeInverseDeformationFieldImageFilter, ImageToImageFilter);

  /** Some typedefs. */
  typedef TInputImage                              InputImageType;
  typedef typename InputImageType::ConstPointer    InputImageConstPointer;
  typedef typename InputImageType::Pointer         InputImagePointer;
  typedef typename InputImageType::PointType       InputImagePointType; 
  typedef typename InputImageType::RegionType      InputImageRegionType; 
  typedef typename InputImageType::SizeType        InputImageSizeType;
  typedef typename InputImageType::SpacingType     InputImageSpacingType; 
  typedef typename InputImageType::IndexType       InputImageIndexType;
  typedef typename InputImageType::PixelType       PixelType;
  typedef TOutputImage                             OutputImageType;
  typedef typename OutputImageType::Pointer        OutputImagePointer;
  typedef typename OutputImageType::PixelType      OutputImagePixelType;
  typedef typename OutputImageType::PointType      OutputImagePointType;
  typedef typename OutputImageType::IndexType      OutputImageIndexType;
  typedef typename OutputImagePixelType::ValueType OutputImageValueType;

  typedef TimeProbe TimeType;
  
  typedef ImageRegionConstIterator<InputImageType> InputConstIterator;
  typedef ImageRegionIterator<InputImageType>      InputIterator;
  typedef ImageRegionIterator<OutputImageType>     OutputIterator;

  typedef WarpVectorImageFilter<TOutputImage,TInputImage,TOutputImage> VectorWarperType;

  typedef VectorLinearInterpolateImageFunction<TInputImage,double> FieldInterpolatorType;
  typedef typename FieldInterpolatorType::Pointer                  FieldInterpolatorPointer;
  typedef typename FieldInterpolatorType::OutputType               FieldInterpolatorOutputType;

  itkSetMacro(NumberOfIterations, unsigned int);
  itkGetConstMacro(NumberOfIterations, unsigned int);
  typedef typename OutputImageType::RegionType ThreadRegionType;
  
  // If the error (in mm) between forward and backward mapping is smaller than the StopValue,
  // the algorithm stops.
  // This value can be used to speed up the calculation.
  itkSetMacro(StopValue, double);
  itkGetConstMacro(StopValue, double);

  char* GetReport() {return this->m_Report;}
  OutputImagePixelType TrilinearInterpolationFast(float& fDesiredX, float& fDesiredY, float& fDesiredZ, InputImageSizeType size);

#ifdef ITK_USE_CONCEPT_CHECKING
  /** Begin concept checking */
  itkConceptMacro(OutputHasNumericTraitsCheck,
                  (Concept::HasNumericTraits<OutputImageValueType>));
  /** End concept checking */
#endif

protected:
  ICCIterativeInverseDeformationFieldImageFilter();
  ~ICCIterativeInverseDeformationFieldImageFilter() {}

  void PrintSelf(std::ostream& os, Indent indent) const;
  void MakeReport();

  void GenerateData( );
  void ComputeInverse(InputImageConstPointer&,OutputImagePointer&);
  void ThreadedComputeInverse(InputImageConstPointer&, OutputImagePointer&, const ThreadRegionType &regionToProcess, int);
  InputImageIndexType  BoundaryIndexing(int, int,int, const int,const int,const int);

  unsigned int m_NumberOfIterations;
  double       m_StopValue;
  double       m_Time;

   struct ThreadStruct
   {
     ICCIterativeInverseDeformationFieldImageFilter *Filter;
	 InputImageConstPointer inputPtr;
	 OutputImagePointer outputPtr;
   };

private:
  ICCIterativeInverseDeformationFieldImageFilter(const Self&); //purposely not implemented
  void operator=(const Self&); //purposely not implemented
  
   static ITK_THREAD_RETURN_TYPE ComputeInverseThreaderCallback(void * arg);
};

} // end namespace itk

#include "itkICCIterativeInverseDeformationFieldImageFilter.txx"

#endif

