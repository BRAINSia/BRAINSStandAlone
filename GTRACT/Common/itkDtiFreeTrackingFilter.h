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

#ifndef __itkDtiFreeTrackingFilter_h
#define __itkDtiFreeTrackingFilter_h

#include "itkObject.h"
#include "itkImage.h"
#include "itkImageToImageFilter.h"
#include "itkIOCommon.h"
#include "itkLinearInterpolateImageFunction.h"
#include "itkVectorLinearInterpolateImageFunction.h"
#include "itkImageRegionConstIteratorWithIndex.h"
#include "itkPointSet.h"
#include "itkBlobSpatialObject.h"

#include "itkDtiTrackingFilterBase.h"
#include "algo.h"
#include "GtractTypes.h"
#include "gtractCommonWin32.h"

#include <map>
#include <string>

namespace itk
{
/** \class DtiFreeTrackingFilter
 */

template <class TTensorImageType, class TAnisotropyImageType, class TMaskImageType>
class DtiFreeTrackingFilter : public itk::DtiTrackingFilterBase<TTensorImageType,
                                                                                     TAnisotropyImageType,
                                                                                     TMaskImageType>
{
public:
  /** Standard class typedefs. */
  typedef DtiFreeTrackingFilter                                                              Self;
  typedef itk::DtiTrackingFilterBase<TTensorImageType, TAnisotropyImageType, TMaskImageType> Superclass;
  typedef SmartPointer<Self>                                                                 Pointer;
  typedef SmartPointer<const Self>                                                           ConstPointer;

  /** Standard New method. */
  itkNewMacro(Self);

  /** Runtime information support. */
  itkTypeMacro(DtiFreeTrackingFilter, itk::DtiTrackingFilterBase);

  itkSetMacro(CurvatureThreshold, double);
  itkGetMacro(CurvatureThreshold, double);

  // void SetSeeds(SeedListType);
  // void SetTrackingDirections(DirectionListType);

  void Update();

protected:
  DtiFreeTrackingFilter();
  ~DtiFreeTrackingFilter()
  {
  }
private:
  DtiFreeTrackingFilter(const Self &); // purposely not implemented
  void operator=(const Self &);        // purposely not implemented

  double m_CurvatureThreshold;
};  // end of class
} // end namespace itk

#ifndef ITK_MANUAL_INSTANTIATION
#include "itkDtiFreeTrackingFilter.hxx"
#endif

#endif
