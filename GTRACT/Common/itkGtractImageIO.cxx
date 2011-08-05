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

#ifndef __itkGtractImageIO_cxx
#define __itkGtractImageIO_cxx

#include "itkGtractImageIO.h"

#include <iostream>

namespace itk
{
GtractImageIO
::GtractImageIO()
{
}

void GtractImageIO::SetDicomDirectory( char *dicomDir)
{
  m_DicomDirectory = dicomDir;
}

void GtractImageIO::SetDicomDirectory( std::string dicomDir)
{
  m_DicomDirectory = dicomDir;
}

void GtractImageIO::SetFileName( char *fileName)
{
  m_FileName = fileName;
}

void GtractImageIO::SetFileName( std::string fileName)
{
  m_FileName = fileName;
}

void GtractImageIO::SetDicomSeriesUID( char *UID)
{
  m_DicomSeriesUID = UID;
}

void GtractImageIO::SetDicomSeriesUID( std::string UID)
{
  m_DicomSeriesUID = UID;
}

void GtractImageIO::Load3dShortImage()
{
  typedef itk::ImageFileReader<Short3dImageType> FileReaderType;
  FileReaderType::Pointer reader = FileReaderType::New();
  std::cout << "Loading image " << m_FileName << " ...." << std::endl;
  reader->SetFileName( m_FileName.c_str() );
  reader->Update();

  m_Short3dImage = reader->GetOutput();
}

void GtractImageIO::Load4dShortImage()
{
  typedef itk::ImageFileReader<Short4dImageType> FileReaderType;
  FileReaderType::Pointer reader = FileReaderType::New();
  std::cout << "Loading image " << m_FileName << " ...." << std::endl;
  reader->SetFileName( m_FileName.c_str() );
  reader->Update();

  m_Short4dImage = reader->GetOutput();
}

void GtractImageIO::Load3dFloatImage()
{
  typedef itk::ImageFileReader<Float3dImageType> FileReaderType;
  FileReaderType::Pointer reader = FileReaderType::New();
  std::cout << "Loading image " << m_FileName << " ...." << std::endl;
  reader->SetFileName( m_FileName.c_str() );
  reader->Update();

  m_Float3dImage = reader->GetOutput();
}

void GtractImageIO::Load3dRgbImage()
{
  typedef itk::ImageFileReader<Rgb3dImageType> FileReaderType;
  FileReaderType::Pointer reader = FileReaderType::New();
  std::cout << "Loading image " << m_FileName << " ...." << std::endl;
  reader->SetFileName( m_FileName.c_str() );
  reader->Update();

  m_Rgb3dImage = reader->GetOutput();
}

void GtractImageIO::LoadTensorImage()
{
  typedef itk::ImageFileReader<TensorImageType> FileReaderType;
  FileReaderType::Pointer reader = FileReaderType::New();
  std::cout << "Loading image " << m_FileName << " ...." << std::endl;
  reader->SetFileName( m_FileName.c_str() );
  reader->Update();

  m_TensorImage = reader->GetOutput();
}

void GtractImageIO::Save3dShortImage()
{
  typedef itk::ImageFileWriter<Short3dImageType> FileWriterType;
  FileWriterType::Pointer writer = FileWriterType::New();
  writer->UseCompressionOn();
  std::cout << "Saving image " << m_FileName << " ...." << std::endl;
  writer->SetInput(m_Short3dImage);
  writer->SetFileName( m_FileName.c_str() );
  writer->Update();
  std::cout << "Done!" << std::endl;
}

void GtractImageIO::Save4dShortImage()
{
  typedef itk::ImageFileWriter<Short4dImageType> FileWriterType;
  FileWriterType::Pointer writer = FileWriterType::New();
  writer->UseCompressionOn();
  std::cout << "Saving image " << m_FileName << " ...." << std::endl;
  writer->SetInput(m_Short4dImage);
  writer->SetFileName( m_FileName.c_str() );
  writer->Update();
  std::cout << "Done!" << std::endl;
}

void GtractImageIO::Save3dFloatImage()
{
  typedef itk::ImageFileWriter<Float3dImageType> FileWriterType;
  FileWriterType::Pointer writer = FileWriterType::New();
  writer->UseCompressionOn();
  std::cout << "Saving image " << m_FileName << " ...." << std::endl;
  writer->SetInput(m_Float3dImage);
  writer->SetFileName( m_FileName.c_str() );
  writer->Update();
  std::cout << "Done!" << std::endl;
}

void GtractImageIO::Save3dRgbImage()
{
  typedef itk::ImageFileWriter<Rgb3dImageType> FileWriterType;
  FileWriterType::Pointer writer = FileWriterType::New();
  writer->UseCompressionOn();
  std::cout << "Saving image " << m_FileName << " ...." << std::endl;
  writer->SetInput(m_Rgb3dImage);
  writer->SetFileName( m_FileName.c_str() );
  writer->Update();
  std::cout << "Done!" << std::endl;
}

void GtractImageIO::SaveTensorImage()
{
  typedef itk::ImageFileWriter<TensorImageType> FileWriterType;
  FileWriterType::Pointer writer = FileWriterType::New();
  writer->UseCompressionOn();
  std::cout << "Saving image " << m_FileName << " ...." << std::endl;
  writer->SetInput(m_TensorImage);
  writer->SetFileName( m_FileName.c_str() );
  writer->Update();
  std::cout << "Done!" << std::endl;
}

void GtractImageIO::Load3dDICOMSeries()
{
  typedef itk::ImageSeriesReader<Short3dImageType> ReaderType;
  ReaderType::Pointer       reader = ReaderType::New();
  itk::GDCMImageIO::Pointer dicomIO = itk::GDCMImageIO::New();

  /* Generate a list of Series UIDs */
  itk::GDCMSeriesFileNames::Pointer FileNameGenerator;
  FileNameGenerator = itk::GDCMSeriesFileNames::New();
  FileNameGenerator->SetUseSeriesDetails( false );
  FileNameGenerator->SetDirectory( m_DicomDirectory.c_str() );

  reader->SetFileNames( FileNameGenerator->GetFileNames( m_DicomSeriesUID.c_str() ) );
  reader->SetImageIO( dicomIO );

  std::cout << "Loading dicom images...." << std::endl;
  reader->Update();
  std::cout << "Done!" << std::endl;

  m_Short3dImage = reader->GetOutput();
}

void GtractImageIO::Load4dDICOMSeries()
{
  typedef itk::ImageSeriesReader<Short4dImageType> ReaderType;
  ReaderType::Pointer       reader = ReaderType::New();
  itk::GDCMImageIO::Pointer dicomIO = itk::GDCMImageIO::New();

  /* Generate a list of Series UIDs */
  itk::GDCMSeriesFileNames::Pointer FileNameGenerator;
  FileNameGenerator = itk::GDCMSeriesFileNames::New();
  FileNameGenerator->SetUseSeriesDetails( true );
  FileNameGenerator->SetDirectory( m_DicomDirectory.c_str() );

  reader->SetFileNames( FileNameGenerator->GetFileNames( m_DicomSeriesUID.c_str() ) );
  reader->SetImageIO( dicomIO );

  std::cout << "Loading dicom images...." << std::endl;
  reader->Update();
  std::cout << "Done!" << std::endl;

  m_Short4dImage = reader->GetOutput();
}

} // end namespace itk
#endif
