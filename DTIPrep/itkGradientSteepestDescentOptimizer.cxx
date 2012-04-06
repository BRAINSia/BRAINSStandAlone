/*=========================================================================

  Program:   Insight Segmentation & Registration Toolkit
  Module:    $RCSfile: itkGradientSteepestDescentOptimizer.cxx,v $
  Language:  C++
  Date:      $Date: 2009-11-24 12:27:56 $
  Version:   $Revision: 1.3 $

  Copyright (c) Insight Software Consortium. All rights reserved.
  See ITKCopyright.txt or http://www.itk.org/HTML/Copyright.htm for details.

     This software is distributed WITHOUT ANY WARRANTY; without even
     the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
     PURPOSE.  See the above copyright notices for more information.

=========================================================================*/
#ifndef _itkGradientSteepestDescentOptimizer_txx
#define _itkGradientSteepestDescentOptimizer_txx

#include "itkGradientSteepestDescentOptimizer.h"
#include "itkCommand.h"
#include "itkEventObject.h"

namespace itk
{
/**
 * Advance one Step following the gradient direction
 * This method will be overrided in non-vector spaces
 */
void
GradientSteepestDescentOptimizer
  ::StepAlongGradient( double factor,
  const DerivativeType & transformedGradient )
{
  itkDebugMacro(
   << "factor = " << factor << "  transformedGradient= " << transformedGradient );

  const unsigned int spaceDimension
    = m_CostFunction->GetNumberOfParameters();

  ParametersType newPosition( spaceDimension );
  ParametersType currentPosition = this->GetCurrentPosition();

  for ( unsigned int j = 0; j < spaceDimension; j++ )
    {
    newPosition[j] = currentPosition[j] + transformedGradient[j] * factor;
    }

  itkDebugMacro(<< "new position = " << newPosition );

  this->SetCurrentPosition( newPosition );
}
} // end namespace itk

#endif
