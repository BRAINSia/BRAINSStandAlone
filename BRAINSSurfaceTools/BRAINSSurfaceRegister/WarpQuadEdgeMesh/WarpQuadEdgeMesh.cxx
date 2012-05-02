/*=========================================================================
 
 Program:   BRAINS (Brain Research: Analysis of Images, Networks, and Systems)
 Module:    $RCSfile: $
 Language:  C++
 Date:      $Date: 2011/07/09 14:53:40 $
 Version:   $Revision: 1.0 $
 
 Copyright (c) University of Iowa Department of Radiology. All rights reserved.
 See GTRACT-Copyright.txt or http://mri.radiology.uiowa.edu/copyright/GTRACT-Copyright.txt
 for details.
 
 This software is distributed WITHOUT ANY WARRANTY; without even
 the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
 PURPOSE.  See the above copyright notices for more information.
 
 =========================================================================*/

#include "itkQuadEdgeMeshTraits.h"
#include "itkQuadEdgeMeshVTKPolyDataReader.h"
#include "itkQuadEdgeMeshScalarDataVTKPolyDataWriter.h"

#include "itkIdentityTransform.h"
#include "itkLinearInterpolateMeshFunction.h"
#include "itkNearestNeighborInterpolateMeshFunction.h"

#include "itkResampleQuadEdgeMeshFilter.h"
#include "itkAssignScalarValuesQuadEdgeMeshFilter.h"

#include "WarpQuadEdgeMeshCLP.h"

int main( int argc, char * argv [] )
{

  PARSE_ARGS;

  std::cout<<"-----------------------------------------------"<<std::endl;
  std::cout<<"Input Fixed Mesh: "<<std::endl;
  std::cout<<fixedMeshFile<<std::endl;
  std::cout<<"Input Moving Mesh: "<<std::endl;
  std::cout<<movingMeshFile<<std::endl;
  std::cout<<"Input Deformed Fixed Mesh: "<<std::endl;
  std::cout<<deformedMeshFile<<std::endl;
  std::cout<<"Output Mesh: "<<std::endl;
  std::cout<<outputMeshFile<<std::endl;
  std::cout<<"Interpolation Type: "<<interpolateType<<std::endl;
  std::cout<<"-----------------------------------------------"<<std::endl;
    
  typedef float      PixelType;
  const unsigned int Dimension = 3;

  typedef itk::QuadEdgeMesh< PixelType, Dimension >   MeshType;

  typedef MeshType::PointType       PointType;
  typedef PointType::VectorType     VectorType;

  typedef itk::QuadEdgeMeshTraits< VectorType, Dimension, bool, bool > VectorPointSetTraits;
  typedef itk::QuadEdgeMesh< VectorType, Dimension, VectorPointSetTraits > MeshWithVectorsType;

  typedef itk::QuadEdgeMeshVTKPolyDataReader< MeshType >         ReaderType;

  ReaderType::Pointer inputMeshReader = ReaderType::New();
  inputMeshReader->SetFileName( fixedMeshFile.c_str() );
  inputMeshReader->Update( );
    
  ReaderType::Pointer referenceMeshReader = ReaderType::New();
  referenceMeshReader->SetFileName( movingMeshFile.c_str() );
  referenceMeshReader->Update( );

  ReaderType::Pointer deformedMeshReader = ReaderType::New();
  deformedMeshReader->SetFileName( deformedMeshFile.c_str() );
  deformedMeshReader->Update();

  typedef itk::IdentityTransform< double >  TransformType;

  TransformType::Pointer transform = TransformType::New();

  typedef itk::LinearInterpolateMeshFunction< MeshType > LinearInterpolatorType;
  typedef itk::NearestNeighborInterpolateMeshFunction< MeshType > NearestInterpolatorType;

  LinearInterpolatorType::Pointer interpolator_l = LinearInterpolatorType::New();

  NearestInterpolatorType::Pointer interpolator_n = NearestInterpolatorType::New();

  //get scalars from moving mesh (reference) for deformed mesh
  typedef itk::ResampleQuadEdgeMeshFilter< MeshType, MeshType >  ResamplingFilterType;

  ResamplingFilterType::Pointer resampler = ResamplingFilterType::New();

  resampler->SetTransform( transform );
    
  //set the interpolation type
  if (interpolateType == "Nearest") {
      resampler->SetInterpolator( interpolator_n );
  }
  else if (interpolateType == "Linear")
  {
      resampler->SetInterpolator( interpolator_l );
  }
  
  resampler->SetInput (referenceMeshReader->GetOutput());
  resampler->SetReferenceMesh (deformedMeshReader->GetOutput());

  resampler->Update();

  //assign scalars from deformed mesh to fixed mesh
  typedef itk::AssignScalarValuesQuadEdgeMeshFilter< 
                                    MeshType, 
                                    MeshType, 
                                    MeshType >    AssignFilterType;

  AssignFilterType::Pointer   assignFilter  = AssignFilterType::New();

  assignFilter->SetInputMesh(inputMeshReader->GetOutput());
  assignFilter->SetSourceMesh(resampler->GetOutput());

  assignFilter->Update();

  //write the result
  typedef itk::QuadEdgeMeshScalarDataVTKPolyDataWriter< MeshType >  WriterType;
  WriterType::Pointer writer = WriterType::New();
  writer->SetInput( assignFilter->GetOutput());
  writer->SetFileName(outputMeshFile.c_str());
  writer->Update(); 

  return 0;
}

