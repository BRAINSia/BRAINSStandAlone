/*=========================================================================

  Program:   Insight Segmentation & Registration Toolkit
  Module:    itkQuadEdgeMeshDelaunayConformingFilter.h
  Language:  C++
  Date:      $Date$
  Version:   $Revision$

  Copyright (c) Insight Software Consortium. All rights reserved.
  See ITKCopyright.txt or http://www.itk.org/HTML/Copyright.htm for details.

     This software is distributed WITHOUT ANY WARRANTY; without even
     the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
     PURPOSE.  See the above copyright notices for more information.

=========================================================================*/

#ifndef __itkQuadEdgeMeshDelaunayConformingFilter_h
#define __itkQuadEdgeMeshDelaunayConformingFilter_h

#include "itkPriorityQueueContainer.h"
#include <itkQuadEdgeMeshToQuadEdgeMeshFilter.h>
#include <itkQuadEdgeMeshEulerOperatorFlipEdgeFunction.h>

namespace itk
{
/**
 *  \class QuadEdgeMeshDelaunayConformingFilter
 *
 *  \brief FIXME Add documentation
 *
 */
template< class TInputMesh, class TOutputMesh >
class QuadEdgeMeshDelaunayConformingFilter :
  public QuadEdgeMeshToQuadEdgeMeshFilter< TInputMesh, TOutputMesh >
{
public:
  /** Basic types. */
  typedef QuadEdgeMeshDelaunayConformingFilter              Self;
  typedef QuadEdgeMeshToQuadEdgeMeshFilter< TInputMesh,
    TOutputMesh >                                           Superclass;
  typedef SmartPointer< Self >                              Pointer;
  typedef SmartPointer< const Self >                        ConstPointer;

  /** Input types. */
  typedef TInputMesh                                        InputMeshType;
  typedef typename InputMeshType::Pointer                   InputMeshPointer;
  typedef typename InputMeshType::CoordRepType              InputCoordRepType;
  typedef typename InputMeshType::PointType                 InputPointType;
  typedef typename InputPointType::VectorType               InputPointVectorType;
  typedef typename InputMeshType::PointIdentifier           InputPointIdentifier;
  typedef typename InputMeshType::QEType                    InputQEType;
  typedef typename InputMeshType::VectorType                InputVectorType;
  typedef typename InputMeshType::EdgeListType              InputEdgeListType;
  typedef typename InputMeshType::PixelType                 InputPixelType;
  typedef typename InputMeshType::Traits                    InputTraits;

  itkStaticConstMacro( InputVDimension, unsigned int, InputMeshType::PointDimension );

  typedef typename InputMeshType::PointsContainer               InputPointsContainer;
  typedef typename InputMeshType::PointsContainerConstIterator  InputPointsContainerConstIterator;
  typedef typename InputMeshType::CellsContainerConstIterator   InputCellsContainerConstIterator;
  typedef typename InputMeshType::EdgeCellType                  InputEdgeCellType;
  typedef typename InputMeshType::PolygonCellType               InputPolygonCellType;
  typedef typename InputMeshType::PointIdList                   InputPointIdList;

  typedef typename InputQEType::IteratorGeom                  InputQEIterator;

  /** Output types. */
  typedef TOutputMesh                                         OutputMeshType;
  typedef typename OutputMeshType::Pointer                    OutputMeshPointer;
  typedef typename OutputMeshType::CoordRepType               OutputCoordRepType;
  typedef typename OutputMeshType::PointType                  OutputPointType;
  typedef typename OutputMeshType::PointIdentifier            OutputPointIdentifier;
  typedef typename OutputMeshType::CellType                   OutputCellType;
  typedef typename OutputMeshType::CellIdentifier             OutputCellIdentifier;
  typedef typename OutputMeshType::EdgeCellType               OutputEdgeCellType;
  typedef typename OutputMeshType::QEType                     OutputQEType;
  typedef typename OutputQEType::LineCellIdentifier           OutputLineCellIdentifier;
  typedef typename OutputMeshType::VectorType                 OutputVectorType;
  typedef typename OutputQEType::IteratorGeom                 OutputQEIterator;
  typedef typename OutputMeshType::PointsContainerPointer     OutputPointsContainerPointer;
  typedef typename OutputMeshType::PointsContainerIterator    OutputPointsContainerIterator;
  typedef typename OutputMeshType::CellsContainer             OutputCellsContainer;
  typedef typename OutputMeshType::CellsContainerIterator     OutputCellsContainerIterator;

  itkStaticConstMacro( OutputVDimension, unsigned int, OutputMeshType::PointDimension );

  itkNewMacro( Self );
  itkTypeMacro( QuadEdgeMeshDelaunayConformingFilter, QuadEdgeMeshToQuadEdgeMeshFilter );

  itkGetConstMacro( NumberOfEdgeFlips, unsigned long );

public:
  typedef std::list< OutputEdgeCellType* >               OutputEdgeCellListType;
  typedef typename OutputEdgeCellListType::iterator      OutputEdgeCellListIterator;

  typedef double                                         CriterionValueType;
  typedef std::pair< bool, CriterionValueType >          PriorityType;

  typedef MaxPriorityQueueElementWrapper< 
    OutputEdgeCellType*, PriorityType, long >            PriorityQueueItemType;

  typedef PriorityQueueContainer< PriorityQueueItemType*,
    ElementWrapperPointerInterface< PriorityQueueItemType* >,
    PriorityType,
    long >   PriorityQueueType;

  typedef typename PriorityQueueType::Pointer                       PriorityQueuePointer;
  typedef std::map< OutputEdgeCellType*, PriorityQueueItemType* >   QueueMapType;
  typedef typename QueueMapType::iterator                           QueueMapIterator;

  typedef QuadEdgeMeshEulerOperatorFlipEdgeFunction< 
    OutputMeshType, OutputQEType >                                  FlipEdgeFunctionType;
  typedef typename FlipEdgeFunctionType::Pointer                    FlipEdgeFunctionPointer;

  void SetListOfConstrainedEdges( const OutputEdgeCellListType& iList )
    {
    m_ListOfConstrainedEdges = iList;
    }

protected:
  QuadEdgeMeshDelaunayConformingFilter( );
  virtual ~QuadEdgeMeshDelaunayConformingFilter( );

  OutputEdgeCellListType            m_ListOfConstrainedEdges;
  PriorityQueuePointer              m_PriorityQueue;
  QueueMapType                      m_QueueMapper;

  unsigned long                     m_NumberOfEdgeFlips;
  FlipEdgeFunctionPointer           m_FlipEdge;
        

  void GenerateData( );
  void InitializePriorityQueue();
  void Process();

  inline CriterionValueType
    Dyer07Criterion( OutputMeshType* iMesh, OutputQEType* iEdge ) const
    {
    OutputPointIdentifier id1 = iEdge->GetOrigin( );
    OutputPointIdentifier id2 = iEdge->GetDestination( );

    OutputPointIdentifier idA = iEdge->GetLnext( )->GetDestination( );
    OutputPointIdentifier idB = iEdge->GetRnext( )->GetOrigin( );

    OutputPointType pt1 = iMesh->GetPoint( id1 );
    OutputPointType pt2 = iMesh->GetPoint( id2 );
    OutputPointType ptA = iMesh->GetPoint( idA );
    OutputPointType ptB = iMesh->GetPoint( idB );

    OutputVectorType v1A = ptA - pt1;
    OutputVectorType v1B = ptB - pt1;
    OutputVectorType v2A = ptA - pt2;
    OutputVectorType v2B = ptB - pt2;

    OutputCoordRepType sq_norm1A = v1A * v1A;
    OutputCoordRepType sq_norm1B = v1B * v1B;
    OutputCoordRepType sq_norm2A = v2A * v2A;
    OutputCoordRepType sq_norm2B = v2B * v2B;

    CriterionValueType dotA = static_cast< CriterionValueType >( v1A * v2A );
    CriterionValueType dotB = static_cast< CriterionValueType >( v1B * v2B );
    CriterionValueType den  = static_cast< CriterionValueType >( sq_norm1A * sq_norm2A );

    if( den != 0. )
      {
      dotA /= vcl_sqrt( den );
      }

    if( dotA > 1. )
      {
      dotA = 1.;
      }

    if( dotA < -1. )
      {
      dotA = -1.;
      }

    den = static_cast< CriterionValueType >( sq_norm1B * sq_norm2B );

    if( den != 0. )
      {
      dotB /= vcl_sqrt( den );
      }

    if( dotB > 1. )
      {
      dotB = 1.;
      }
      
    if( dotB < -1. )
      {
      dotB = -1.;
      }

    return ( vcl_acos( dotA ) + vcl_acos( dotB ) - vnl_math::pi );
    }

private:

  QuadEdgeMeshDelaunayConformingFilter( const Self& ); // Purposely not implemented
  void operator=( const Self& );  // Purposely not implemented

}; //

} // end namespace itk

#include "itkQuadEdgeMeshDelaunayConformingFilter.txx"

#endif
