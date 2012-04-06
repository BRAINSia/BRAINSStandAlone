
/** For Linear Eddy Current Transformation **/

#ifndef _itkLinearEddyCurrentTransform_txx
#define _itkLinearEddyCurrentTransform_txx

#include "itkNumericTraits.h"
#include "itkLinearEddyCurrentTransform.h"
#include "vnl/algo/vnl_matrix_inverse.h"


namespace itk
{

// Constructor with default arguments
template<class TScalarType, unsigned int NInputDimensions,
                            unsigned int NOutputDimensions>
LinearEddyCurrentTransform<TScalarType, NInputDimensions, NOutputDimensions>
::LinearEddyCurrentTransform()
#if (ITK_VERSION_MAJOR < 4)
  : Superclass(OutputSpaceDimension, ParametersDimension)
#else
  : Superclass(ParametersDimension)
#endif
{
  
  m_Matrix.SetIdentity();
  m_MatrixMTime.Modified();
  m_Offset.Fill( 0 );
  m_Center.Fill( 0 );
  m_Translation.Fill( 0 );
  m_Singular = false;
  m_InverseMatrix.SetIdentity();
  m_InverseMatrixMTime = m_MatrixMTime;
  this->m_FixedParameters.SetSize ( NInputDimensions );
  this->m_FixedParameters.Fill ( 0.0 );

  
}


// Constructor with default arguments
template<class TScalarType, unsigned int NInputDimensions,
                            unsigned int NOutputDimensions>
LinearEddyCurrentTransform<TScalarType, NInputDimensions, NOutputDimensions>
::LinearEddyCurrentTransform( unsigned int outputDims, 
                             unsigned int paramDims   )
  : Superclass(outputDims, paramDims)
{
  m_Matrix.SetIdentity();
  m_MatrixMTime.Modified();
  m_Offset.Fill( 0 );
  m_Center.Fill( 0 );
  m_Translation.Fill( 0 );
  m_Singular = false;
  m_InverseMatrix.SetIdentity();
  m_InverseMatrixMTime = m_MatrixMTime;
}




// Constructor with explicit arguments
template<class TScalarType, unsigned int NInputDimensions,
                            unsigned int NOutputDimensions>
LinearEddyCurrentTransform<TScalarType, NInputDimensions, NOutputDimensions>
::LinearEddyCurrentTransform(const MatrixType &matrix,
                            const OutputVectorType &offset)
{
  m_Matrix = matrix;
  m_MatrixMTime.Modified();
  m_Offset = offset;
  m_Center.Fill( 0 );
  m_Translation.Fill(0);
  for(unsigned int i=0; i<NOutputDimensions; i++)
    {
    m_Translation[i] = offset[i];
    }
  this->ComputeMatrixParameters();
}




// Destructor
template<class TScalarType, unsigned int NInputDimensions,
                            unsigned int NOutputDimensions>
LinearEddyCurrentTransform<TScalarType, NInputDimensions, NOutputDimensions>
::~LinearEddyCurrentTransform()
{
  return;
}



// Print self
template<class TScalarType, unsigned int NInputDimensions,
                            unsigned int NOutputDimensions>
void
LinearEddyCurrentTransform<TScalarType, NInputDimensions, NOutputDimensions>
::PrintSelf(std::ostream &os, Indent indent) const
{
  Superclass::PrintSelf(os,indent);

  unsigned int i, j;
  
  os << indent << "Matrix: " << std::endl;
  for (i = 0; i < NInputDimensions; i++) 
    {
    os << indent.GetNextIndent();
    for (j = 0; j < NOutputDimensions; j++)
      {
      os << m_Matrix[i][j] << " ";
      }
    os << std::endl;
    }

  os << indent << "Offset: " << m_Offset << std::endl;
  os << indent << "Center: " << m_Center << std::endl;
  os << indent << "Translation: " << m_Translation << std::endl;

  os << indent << "Inverse: " << std::endl;
  for (i = 0; i < NInputDimensions; i++) 
    {
    os << indent.GetNextIndent();
    for (j = 0; j < NOutputDimensions; j++)
      {
      os << this->GetInverseMatrix()[i][j] << " ";
      }
    os << std::endl;
    }
  os << indent << "Singular: " << m_Singular << std::endl;
}

// Constructor with explicit arguments
template<class TScalarType, unsigned int NInputDimensions,
                            unsigned int NOutputDimensions>
void
LinearEddyCurrentTransform<TScalarType, NInputDimensions, NOutputDimensions>
::SetIdentity( void )
{
  m_Matrix.SetIdentity();
  m_MatrixMTime.Modified();
  m_Offset.Fill( 0.0 );
  m_Translation.Fill( 0.0 );
  m_Center.Fill( 0.0 );
  m_Singular = false;
  m_InverseMatrix.SetIdentity();
  m_InverseMatrixMTime = m_MatrixMTime;
  this->Modified();  
}


// Compose with another affine transformation
template<class TScalarType, unsigned int NInputDimensions,
                            unsigned int NOutputDimensions>
void
LinearEddyCurrentTransform<TScalarType, NInputDimensions, NOutputDimensions>
::Compose(const Self * other, bool pre)
{
  if (pre) 
    {
    m_Offset = m_Matrix * other->m_Offset + m_Offset;
    m_Matrix = m_Matrix * other->m_Matrix;
    }
  else 
    {
    m_Offset = other->m_Matrix * m_Offset + other->m_Offset;
    m_Matrix = other->m_Matrix * m_Matrix;
    }

  this->ComputeTranslation();
  this->ComputeMatrixParameters();

  m_MatrixMTime.Modified();
  this->Modified();

  return;
}



// Transform a point
template<class TScalarType, unsigned int NInputDimensions,
                            unsigned int NOutputDimensions>
typename LinearEddyCurrentTransform<TScalarType,
                               NInputDimensions,
                               NOutputDimensions>::OutputPointType
LinearEddyCurrentTransform<TScalarType, NInputDimensions, NOutputDimensions>
::TransformPoint(const InputPointType &point) const 
{
  return m_Matrix * point + m_Offset;
}


// Transform a vector
template<class TScalarType, unsigned int NInputDimensions,
                            unsigned int NOutputDimensions>
typename LinearEddyCurrentTransform<TScalarType,
                               NInputDimensions,
                               NOutputDimensions>::OutputVectorType
LinearEddyCurrentTransform<TScalarType, NInputDimensions, NOutputDimensions>
::TransformVector(const InputVectorType &vect) const 
{
  return m_Matrix * vect;
}


// Transform a vnl_vector_fixed
template<class TScalarType, unsigned int NInputDimensions,
                            unsigned int NOutputDimensions>
typename LinearEddyCurrentTransform<TScalarType,
                               NInputDimensions,
                               NOutputDimensions>::OutputVnlVectorType
LinearEddyCurrentTransform<TScalarType, NInputDimensions, NOutputDimensions>
::TransformVector(const InputVnlVectorType &vect) const 
{
  return m_Matrix * vect;
}


// Transform a CovariantVector
template<class TScalarType, unsigned int NInputDimensions,
                            unsigned int NOutputDimensions>
typename LinearEddyCurrentTransform<TScalarType,
                               NInputDimensions,
                               NOutputDimensions>::OutputCovariantVectorType
LinearEddyCurrentTransform<TScalarType, NInputDimensions, NOutputDimensions>
::TransformCovariantVector(const InputCovariantVectorType &vec) const 
{
  OutputCovariantVectorType  result;    // Converted vector

  for (unsigned int i = 0; i < NOutputDimensions; i++) 
    {
    result[i] = NumericTraits<ScalarType>::Zero;
    for (unsigned int j = 0; j < NInputDimensions; j++) 
      {
      result[i] += this->GetInverseMatrix()[j][i]*vec[j]; // Inverse transposed
      }
    }
  return result;
}

// Recompute the inverse matrix (internal)
template<class TScalarType, unsigned int NInputDimensions,
                            unsigned int NOutputDimensions>
const typename LinearEddyCurrentTransform<TScalarType,
                               NInputDimensions,
                               NOutputDimensions>::InverseMatrixType &
LinearEddyCurrentTransform<TScalarType, NInputDimensions, NOutputDimensions>
::GetInverseMatrix( void ) const
{
  // If the transform has been modified we recompute the inverse
  if(m_InverseMatrixMTime != m_MatrixMTime)
    {
    m_Singular = false;
    try 
      {
      m_InverseMatrix  = m_Matrix.GetInverse();
      }
    catch(...) 
      {
      m_Singular = true;
      }
     m_InverseMatrixMTime = m_MatrixMTime;
    }

  return m_InverseMatrix;
}

// return an inverse transformation
template<class TScalarType, unsigned int NInputDimensions,
                            unsigned int NOutputDimensions>
bool
LinearEddyCurrentTransform<TScalarType, NInputDimensions, NOutputDimensions>
::GetInverse( Self * inverse) const
{
  if(!inverse)
    {
    return false;
    }

  this->GetInverseMatrix();
  if(m_Singular)
    {
    return false;
    }

  inverse->m_Matrix         = this->GetInverseMatrix();
  inverse->m_InverseMatrix  = m_Matrix;
  inverse->m_Offset         = -(this->GetInverseMatrix() * m_Offset);
  inverse->ComputeTranslation();
  inverse->ComputeMatrixParameters();

  return true;
}


// Get fixed parameters
template<class TScalarType, unsigned int NInputDimensions,
                            unsigned int NOutputDimensions>
void
LinearEddyCurrentTransform<TScalarType, NInputDimensions, NOutputDimensions>
  ::SetFixedParameters( const ParametersType & fp )
{
  this->m_FixedParameters = fp;
  InputPointType c;
  for ( unsigned int i = 0; i < NInputDimensions; i++ )
    {
    c[i] = this->m_FixedParameters[i];
    }
  this->SetCenter ( c );
}

/** Get the Fixed Parameters. */
template<class TScalarType, unsigned int NInputDimensions,
                            unsigned int NOutputDimensions>
const typename LinearEddyCurrentTransform<TScalarType,
                                     NInputDimensions,
                                     NOutputDimensions>::ParametersType &
LinearEddyCurrentTransform<TScalarType, NInputDimensions, NOutputDimensions>
  ::GetFixedParameters(void) const
{
  this->m_FixedParameters.SetSize ( NInputDimensions );
  for ( unsigned int i = 0; i < NInputDimensions; i++ )
    {
    this->m_FixedParameters[i] = this->m_Center[i];
    }
  return this->m_FixedParameters;
}



// Get parameters
template<class TScalarType, unsigned int NInputDimensions,
                            unsigned int NOutputDimensions>
const typename LinearEddyCurrentTransform<TScalarType,
                                     NInputDimensions,
                                     NOutputDimensions>::ParametersType &
LinearEddyCurrentTransform<TScalarType, NInputDimensions, NOutputDimensions>
::GetParameters( void ) const
{
 
  this->m_Parameters[0] = m_Matrix[1][0];  //for X axis shear c1
  this->m_Parameters[1] = m_Matrix[1][1];  //for Y axis scale c2
  this->m_Parameters[2] = m_Matrix[1][2];  //for Z axis shear c3
  this->m_Parameters[3] = m_Translation[1];   //This is for global translation on Y axis c0

  return this->m_Parameters;
}


// Set parameters
template<class TScalarType, unsigned int NInputDimensions,
                            unsigned int NOutputDimensions>
void
LinearEddyCurrentTransform<TScalarType, NInputDimensions, NOutputDimensions>
::SetParameters( const ParametersType & parameters )
{

  //unsigned int par = 0;

  this->m_Parameters = parameters;

  for(unsigned int row=0; row<NOutputDimensions; row++) 
    {
    for(unsigned int col=0; col<NInputDimensions; col++) 
      {
      m_Matrix[row][col] = 0.0;
      }
    m_Matrix[row][row] = 1.0;
    }

 

  m_Matrix[1][0] = this->m_Parameters[0];  //for c1
  m_Matrix[1][1] = this->m_Parameters[1];  //for c2
  m_Matrix[1][2] = this->m_Parameters[2];  //for c3

  // Transfer the constant part
  for(unsigned int i=0; i<NOutputDimensions; i++) 
    {
    m_Translation[i] = 0.0;
    }
  m_Translation[1] = this->m_Parameters[3];    //c0
   
   

  m_MatrixMTime.Modified(); 

  this->ComputeMatrix();  // Not necessary since parameters explicitly define
                          //    the matrix
  this->ComputeOffset();

  // Modified is always called since we just have a pointer to the
  // parameters and cannot know if the parameters have changed.
  this->Modified();

}


// Compute the Jacobian in one position 
template<class TScalarType, unsigned int NInputDimensions,
                            unsigned int NOutputDimensions>
const typename LinearEddyCurrentTransform<TScalarType, NInputDimensions, NOutputDimensions>::JacobianType & 
LinearEddyCurrentTransform<TScalarType, NInputDimensions, NOutputDimensions>
::GetJacobian( const InputPointType & p ) const
{
  // The Jacobian of the affine transform is composed of
  // subblocks of diagonal matrices, each one of them having
  // a constant value in the diagonal.

#if (ITK_VERSION_MAJOR > 3)
#define m_Jacobian m_SharedLocalJacobian
#endif
  this->m_Jacobian.Fill( 0.0 );

  const InputVectorType v = p - this->GetCenter();

  //Linear correction
  this->m_Jacobian( 1, 0 ) = v[0];
  this->m_Jacobian( 1, 1 ) = v[1];
  this->m_Jacobian( 1, 2 ) = v[2];
  this->m_Jacobian( 1, 3 ) = 1.0;
  return this->m_Jacobian;

#if (ITK_VERSION_MAJOR > 3)
#undef  m_Jacobian
#endif

}

// Computes offset based on center, matrix, and translation variables
template<class TScalarType, unsigned int NInputDimensions,
                            unsigned int NOutputDimensions>
void
LinearEddyCurrentTransform<TScalarType, NInputDimensions, NOutputDimensions>
::ComputeOffset( void ) 
{
  const MatrixType & matrix = this->GetMatrix();
  
  OffsetType offset;
  for(unsigned int i=0; i<NOutputDimensions; i++)
    {
    offset[i] = m_Translation[i] + m_Center[i];
    for(unsigned int j=0; j<NInputDimensions; j++)
      {
      offset[i] -= matrix[i][j] * m_Center[j];
      }
    }

  m_Offset = offset ;
}

// Computes translation based on offset, matrix, and center
template<class TScalarType, unsigned int NInputDimensions,
                            unsigned int NOutputDimensions>
void
LinearEddyCurrentTransform<TScalarType, NInputDimensions, NOutputDimensions>
::ComputeTranslation( void ) 
{
  const MatrixType & matrix = this->GetMatrix();
  
  OffsetType translation;
  for(unsigned int i=0; i<NOutputDimensions; i++)
    {
    translation[i] = m_Offset[i] - m_Center[i];
    for(unsigned int j=0; j<NInputDimensions; j++)
      {
      translation[i] += matrix[i][j] * m_Center[j];
      }
    }

  m_Translation = translation ;
}


// Computes matrix - base class does nothing.  In derived classes is
//    used to convert, for example, versor into a matrix
template<class TScalarType, unsigned int NInputDimensions,
                            unsigned int NOutputDimensions>
void
LinearEddyCurrentTransform<TScalarType, NInputDimensions, NOutputDimensions>
::ComputeMatrix( void ) 
{
  // Since parameters explicitly define the matrix in this base class, this
  // function does nothing.  Normally used to compute a matrix when
  // its parameterization (e.g., the class' versor) is modified.
}


// Computes parameters - base class does nothing.  In derived classes is
//    used to convert, for example, matrix into a versor
template<class TScalarType, unsigned int NInputDimensions,
                            unsigned int NOutputDimensions>
void
LinearEddyCurrentTransform<TScalarType, NInputDimensions, NOutputDimensions>
::ComputeMatrixParameters( void ) 
{
  // Since parameters explicitly define the matrix in this base class, this
  // function does nothing.  Normally used to update the parameterization
  // of the matrix (e.g., the class' versor) when the matrix is explicitly
  // set.
}

} // namespace

#endif

