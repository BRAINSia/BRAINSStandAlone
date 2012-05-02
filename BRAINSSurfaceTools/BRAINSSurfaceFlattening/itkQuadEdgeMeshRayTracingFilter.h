#ifndef __itkQuadEdgeMeshRayTracingFilter_h
#define __itkQuadEdgeMeshRayTracingFilter_h

#include <itkQuadEdgeMeshToQuadEdgeMeshFilter.h>
#include <itkQuadEdgeMeshParamMatrixCoefficients.h>

namespace itk
{
/**
 * \class QuadEdgeMeshRayTracingFilter
 * \brief This filter first computes the center of mass C of the input mesh.
 * Then it projects each vertex on a sphere centered at C.
*/
template< class TInputMesh, class TOutputMesh >
class QuadEdgeMeshRayTracingFilter :
  public QuadEdgeMeshToQuadEdgeMeshFilter< TInputMesh, TOutputMesh >
{
public:
  typedef QuadEdgeMeshRayTracingFilter Self;
  typedef SmartPointer< Self > Pointer;
  typedef SmartPointer< const Self > ConstPointer;
  typedef QuadEdgeMeshToQuadEdgeMeshFilter< TInputMesh, TOutputMesh > Superclass;

  /** Run-time type information (and related methods).   */
  itkTypeMacro( QuadEdgeMeshRayTracingFilter, QuadEdgeMeshToQuadEdgeMeshFilter );
  /** New macro for creation of through a Smart Pointer   */
  itkNewMacro( Self );

  /** Input types. */
  typedef TInputMesh                              InputMeshType;
  typedef typename InputMeshType::Pointer         InputMeshPointer;
  typedef typename InputMeshType::ConstPointer    InputMeshConstPointer;
  typedef typename InputMeshType::CoordRepType    InputCoordRepType;
  typedef typename InputMeshType::PointType       InputPointType;
  typedef typename InputPointType::VectorType     InputPointVectorType;
  typedef typename InputMeshType::PointIdentifier InputPointIdentifier;
  typedef typename InputMeshType::QEType          InputQEType;
  typedef typename InputMeshType::VectorType      InputVectorType;
  typedef typename InputMeshType::EdgeListType    InputEdgeListType;
  typedef typename InputMeshType::PixelType       InputPixelType;
  typedef typename InputMeshType::Traits          InputTraits;

  typedef typename InputMeshType::PointsContainer InputPointsContainer;
  typedef typename InputMeshType::PointsContainerConstIterator
    InputPointsContainerConstIterator;

  typedef typename InputMeshType::CellsContainerConstIterator
    InputCellsContainerConstIterator;
  typedef typename InputMeshType::EdgeCellType    InputEdgeCellType;
  typedef typename InputMeshType::PolygonCellType InputPolygonCellType;
  typedef typename InputMeshType::PointIdList     InputPointIdList;

  /** Output types. */
  typedef TOutputMesh                               OutputMeshType;
  typedef typename OutputMeshType::Pointer          OutputMeshPointer;
  typedef typename OutputMeshType::ConstPointer     OutputMeshConstPointer;
  typedef typename OutputMeshType::CoordRepType     OutputCoordRepType;
  typedef typename OutputMeshType::PointType        OutputPointType;
  typedef typename OutputMeshType::PointIdentifier  OutputPointIdentifier;
  typedef typename OutputMeshType::QEType           OutputQEType;
  typedef typename OutputMeshType::VectorType       OutputVectorType;
  typedef typename OutputQEType::IteratorGeom       OutputQEIterator;
  typedef typename OutputMeshType::PointsContainerPointer
    OutputPointsContainerPointer;
  typedef typename OutputMeshType::PointsContainerIterator
    OutputPointsContainerIterator;

  itkStaticConstMacro( PointDimension, unsigned int,
    OutputMeshType::PointDimension );

  typedef MatrixCoefficients< InputMeshType >       CoefficientsComputation;

  void SetCoefficientsMethod( CoefficientsComputation* iMethod )
    { (void) iMethod; }

  itkSetMacro( Radius, OutputCoordRepType );

protected:
  QuadEdgeMeshRayTracingFilter() : Superclass(), m_Radius( 1. ) {}
  ~QuadEdgeMeshRayTracingFilter() {}

  OutputPointType m_Center;
  OutputCoordRepType m_Radius;

  void GenerateData()
  {
    this->CopyInputMeshToOutputMesh( );

    OutputMeshPointer output = this->GetOutput();
    OutputPointsContainerPointer points = output->GetPoints();
    OutputPointsContainerIterator p_it = points->Begin();

    OutputCoordRepType norm2;
    OutputPointType u;
    unsigned int dim;

    for( p_it = points->Begin(); p_it != points->End(); ++p_it )
      {
      norm2 = 0.;
      u.SetEdge( p_it->Value().GetEdge() );

      for( dim = 0; dim < PointDimension; ++dim )
        {
        u[dim] = p_it->Value() [dim] - m_Center[dim];
        norm2 += u[dim] * u[dim];
        }
      norm2 = m_Radius / vcl_sqrt( norm2 );
      for( dim = 0; dim < PointDimension; ++dim )
        u[dim] *= norm2;
      points->SetElement( p_it->Index(), u );
      }
    }

  /** \brief Compute the Center of mass of the input mesh. */
  void ComputeCenterOfMass( )
  {
    m_Center.Fill( 0. );

    OutputMeshPointer output = this->GetOutput();
    OutputPointsContainerPointer points = output->GetPoints();
    OutputPointsContainerIterator p_it = points->Begin();

    unsigned int dim;
    unsigned long k = 0;

    for( ; p_it != points->End(); ++p_it, ++k )
      {
      for( dim = 0; dim < PointDimension; ++dim )
        {
        m_Center[dim] += p_it->Value()[dim];
        }
      }

    OutputCoordRepType inv = 1. / static_cast< OutputCoordRepType > (k);

    for( dim = 0; dim < PointDimension; ++dim )
      {
      m_Center[dim] *= inv;
      }
  }

private:
  QuadEdgeMeshRayTracingFilter( const Self& );
  void operator = ( const Self& );
};
}
#endif
