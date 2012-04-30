/*=========================================================================

  Program:   Insight Segmentation & Registration Toolkit
  Module:    $RCSfile: itkMeanSquaresMeshToMeshMetric.h,v $
  Language:  C++
  Date:      $Date:  $
  Version:   $Revision:  $

  Copyright (c) Insight Software Consortium. All rights reserved.
  See ITKCopyright.txt or http://www.itk.org/HTML/Copyright.htm for details.

     This software is distributed WITHOUT ANY WARRANTY; without even 
     the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
     PURPOSE.  See the above copyright notices for more information.

=========================================================================*/
#ifndef __itkMeanSquaresMeshToMeshMetric_h
#define __itkMeanSquaresMeshToMeshMetric_h

// First make sure that the configuration is available.
// This line can be removed once the optimized versions
// gets integrated into the main directories.
#include "itkConfigure.h"
#include "itkMeshToMeshMetric.h"
#include "itkCovariantVector.h"
#include "itkPoint.h"


namespace itk
{
/** \class MeanSquaresMeshToMeshMetric
 * \brief Computes similarity between two meshes to be registered
 *
 * This Class is templated over the type of the fixed and moving
 * meshes to be compared.
 *
 * This metric computes the sum of squared differences between point values 
 * in the moving mesh and point values in the fixed mesh. The spatial 
 * correspondance between both images is established through a Transform. 
 * Point values are taken from the Moving mesh. Their positions are mapped to 
 * the Fixed mesh and result in general in non-vertex position on it. Values 
 * at these non-vertex positions of the Fixed mesh are interpolated using a 
 * user-selected Interpolator.
 *
 * \ingroup RegistrationMetrics
 */
template < class TFixedMesh, class TMovingMesh > 
class ITK_EXPORT MeanSquaresMeshToMeshMetric : 
    public MeshToMeshMetric< TFixedMesh, TMovingMesh>
{
public:

  /** Standard class typedefs. */
  typedef MeanSquaresMeshToMeshMetric                    Self;
  typedef MeshToMeshMetric<TFixedMesh, TMovingMesh >     Superclass;
  typedef SmartPointer<Self>                             Pointer;
  typedef SmartPointer<const Self>                       ConstPointer;

  /** Method for creation through the object factory. */
  itkNewMacro(Self);
 
  /** Run-time type information (and related methods). */
  itkTypeMacro(MeanSquaresMeshToMeshMetric, MeshToMeshMetric);

 
  /** Types transferred from the base class */
  typedef typename Superclass::TransformType            TransformType;
  typedef typename Superclass::TransformPointer         TransformPointer;
  typedef typename Superclass::TransformParametersType  TransformParametersType;
  typedef typename Superclass::TransformJacobianType    TransformJacobianType;
  typedef typename Superclass::InputPointType           InputPointType;
  typedef typename Superclass::OutputPointType          OutputPointType;

  typedef typename Superclass::MeasureType              MeasureType;
  typedef typename Superclass::DerivativeType           DerivativeType;
  typedef typename Superclass::FixedMeshType            FixedMeshType;
  typedef typename Superclass::MovingMeshType           MovingMeshType;
  typedef typename Superclass::FixedMeshConstPointer    FixedMeshConstPointer;
  typedef typename Superclass::MovingMeshConstPointer   MovingMeshConstPointer;
  typedef typename Superclass::PointIterator            PointIterator;
  typedef typename Superclass::PointDataIterator        PointDataIterator;

  typedef typename Superclass::InterpolatorType         InterpolatorType;
 
  typedef typename Superclass::RealDataType             RealDataType;
  typedef typename Superclass::DerivativeDataType       DerivativeDataType;
  
  /** Constants for the pointset dimensions */
  itkStaticConstMacro(MovingMeshDimension, unsigned int,
                      Superclass::MovingMeshDimension);
  itkStaticConstMacro(FixedMeshDimension, unsigned int,
                      Superclass::FixedMeshDimension);
 
  /** Get the derivatives of the match measure. */
  void GetDerivative( const TransformParametersType & parameters,
                      DerivativeType & derivative ) const;

  /**  Get the value for single valued optimizers. */
  MeasureType GetValue( const TransformParametersType & parameters ) const;

  /**  Get value and derivatives for multiple valued optimizers. */
  void GetValueAndDerivative( const TransformParametersType & parameters,
                              MeasureType& Value, DerivativeType& Derivative ) const;

protected:
  MeanSquaresMeshToMeshMetric();
  virtual ~MeanSquaresMeshToMeshMetric() {};

private:
  MeanSquaresMeshToMeshMetric(const Self&); //purposely not implemented
  void operator=(const Self&); //purposely not implemented

  mutable unsigned int   m_NumberOfPixelsCounted;
};

} // end namespace itk

#ifndef ITK_MANUAL_INSTANTIATION
# include "itkMeanSquaresMeshToMeshMetric.txx"
#endif

#endif
