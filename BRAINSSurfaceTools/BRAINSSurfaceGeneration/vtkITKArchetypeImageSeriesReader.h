/*=========================================================================

  Copyright Brigham and Women's Hospital (BWH) All Rights Reserved.

  See Doc/copyright/copyright.txt
  or http://www.slicer.org/copyright/copyright.txt for details.

  Program:   vtkITK
  Module:    $HeadURL: http://www.na-mic.org/svn/Slicer3/trunk/Libs/vtkITK/vtkITKArchetypeImageSeriesReader.h $
  Date:      $Date: 2007-11-27 14:42:06 -0600 (Tue, 27 Nov 2007) $
  Version:   $Revision: 4956 $

==========================================================================*/

// .NAME vtkITKArchetypeImageSeriesReader - Read a series of files
// that have a common naming convention
// .SECTION Description
// ArchetypeImageSeriesReader creates a volume from a series of images
// stored in files. The series are represented by one filename. This
// filename, the archetype, is any one of the files in the series.
//
// \note
// This work is part of the National Alliance for Medical Image Computing 
// (NAMIC), funded by the National Institutes of Health through the NIH Roadmap
// for Medical Research, Grant U54 EB005149.

#ifndef __vtkITKArchetypeImageSeriesReader_h
#define __vtkITKArchetypeImageSeriesReader_h

#include "vtkImageSource.h"
#include "vtkMatrix4x4.h"
#include "itkSpatialOrientation.h"
#include <vector>
#include <string>

//#include "vtkITK.h"

class  vtkITKArchetypeImageSeriesReader : public vtkImageSource
{
public:
  static vtkITKArchetypeImageSeriesReader *New();
  vtkTypeRevisionMacro(vtkITKArchetypeImageSeriesReader,vtkImageSource);
  void PrintSelf(ostream& os, vtkIndent indent);   

//BTX
  typedef itk::SpatialOrientation::ValidCoordinateOrientationFlags CoordinateOrientationCode;
//ETX

  // Description:
  // Specify the archetype filename for the series.
  vtkSetStringMacro(Archetype);
  vtkGetStringMacro(Archetype);

  // Description:
  // See how many file names were generated during ExecuteInformation
  int GetNumberOfFileNames()
    {
    return this->FileNames.size();
    };

  // Description:
  // Set/Get the default spacing of the data in the file. This will be
  // used if the reader provided spacing is 1.0. (Default is 1.0)
  vtkSetVector3Macro(DefaultDataSpacing,double);
  vtkGetVector3Macro(DefaultDataSpacing,double);
  
  // Description:
  // Set/Get the default origin of the data (location of first pixel
  // in the file). This will be used if the reader provided origin is
  // 0.0. (Default is 0.0)
  vtkSetVector3Macro(DefaultDataOrigin,double);
  vtkGetVector3Macro(DefaultDataOrigin,double);

  // Description:
  // When reading files which start at an unusual index, this can be added
  // to the slice number when generating the file name (default = 0)
  vtkSetMacro(FileNameSliceOffset,int);
  vtkGetMacro(FileNameSliceOffset,int);

  // Description:
  // When reading files which have regular, but non contiguous slices
  // (eg filename.1,filename.3,filename.5)
  // a spacing can be specified to skip missing files (default = 1)
  vtkSetMacro(FileNameSliceSpacing,int);
  vtkGetMacro(FileNameSliceSpacing,int);

  // Description:
  // The maximum number of files to include in the series. If this is
  // zero, then all files will be included. (Default is 0)
  vtkSetMacro(FileNameSliceCount,int);
  vtkGetMacro(FileNameSliceCount,int);

  // Description: is the given file name a NRRD file?
  virtual int CanReadFile(const char* filename);

  // Description:
  // Set the orientation of the output image
  void SetDesiredCoordinateOrientationToAxial ()
    {
    this->DesiredCoordinateOrientation =
     itk::SpatialOrientation::ITK_COORDINATE_ORIENTATION_RAI;
//     itk::SpatialOrientation::ITK_COORDINATE_ORIENTATION_RPS;
    this->UseNativeCoordinateOrientation = 0;
    this->Modified();
    }
  void SetDesiredCoordinateOrientationToCoronal ()
    {
    this->DesiredCoordinateOrientation =
      itk::SpatialOrientation::ITK_COORDINATE_ORIENTATION_RSA;
//      itk::SpatialOrientation::ITK_COORDINATE_ORIENTATION_RIP;
    this->UseNativeCoordinateOrientation = 0;
    this->Modified();
    }
  void SetDesiredCoordinateOrientationToSagittal ()
    {
    this->DesiredCoordinateOrientation =
      itk::SpatialOrientation::ITK_COORDINATE_ORIENTATION_ASL;
//      itk::SpatialOrientation::ITK_COORDINATE_ORIENTATION_AIR;
    this->UseNativeCoordinateOrientation = 0;
    this->Modified();
    }
  void SetDesiredCoordinateOrientationToNative ()
    {
    this->UseNativeCoordinateOrientation = 1;
    this->Modified();
    }

  // Description:
  // Set the data type of pixels in the file.  
  // If you want the output scalar type to have a different value, set it
  // after this method is called.
  virtual void SetOutputScalarTypeToDouble()
  {
    UseNativeScalarType = 0;
    this->SetOutputScalarType(VTK_DOUBLE);
  }
  virtual void SetOutputScalarTypeToFloat()
  {
    UseNativeScalarType = 0;
    this->SetOutputScalarType(VTK_FLOAT);
  }
  virtual void SetOutputScalarTypeToLong()
  {
    UseNativeScalarType = 0;
    this->SetOutputScalarType(VTK_LONG);
  }
  virtual void SetOutputScalarTypeToUnsignedLong()
  {
    UseNativeScalarType = 0;
    this->SetOutputScalarType(VTK_UNSIGNED_LONG);
  }
  virtual void SetOutputScalarTypeToInt()
  {
    UseNativeScalarType = 0;
    this->SetOutputScalarType(VTK_INT);
  }
  virtual void SetOutputScalarTypeToUnsignedInt()
  {
    UseNativeScalarType = 0;
    this->SetOutputScalarType(VTK_UNSIGNED_INT);
  }
  virtual void SetOutputScalarTypeToShort()
  {
    UseNativeScalarType = 0;
    this->SetOutputScalarType(VTK_SHORT);
  }
  virtual void SetOutputScalarTypeToUnsignedShort()
  {
    UseNativeScalarType = 0;
    this->SetOutputScalarType(VTK_UNSIGNED_SHORT);
  }
  virtual void SetOutputScalarTypeToChar()
  {
    UseNativeScalarType = 0;
    this->SetOutputScalarType(VTK_CHAR);
  }
  virtual void SetOutputScalarTypeToUnsignedChar()
  {
    UseNativeScalarType = 0;
    this->SetOutputScalarType(VTK_UNSIGNED_CHAR);
  }
  virtual void SetOutputScalarTypeToNative()
  {
    UseNativeScalarType = 1;
    this->Modified();
  }
  
  // Description:
  // Use image origin from the file
  void SetUseNativeOriginOn() 
  {
    UseNativeOrigin = true;
  }

  // Description:
  // Use image center as origin
  void SetUseNativeOriginOff() 
  {
    UseNativeOrigin = false;
  }

  // Description:
  // Get the file format.  Pixels are this type in the file.
  vtkSetMacro(OutputScalarType, int);
  vtkGetMacro(OutputScalarType, int);

  // Description:
  // Get number of scalars
  vtkSetMacro(NumberOfComponents, int);
  vtkGetMacro(NumberOfComponents, int);

  // Description:
  // Returns an IJK to RAS transformation matrix
  vtkMatrix4x4* GetRasToIjkMatrix();

  // Description:
  // ITK internally does not register all of the IO types that get built
  // (possibly due to lingering bugs?) but many slicer users have
  // GE5 (Signa - magic number: IMGF) files that they need to work
  // with so we register the factory explictly here
  //
  void RegisterExtraBuiltInFactories();

protected:
  vtkITKArchetypeImageSeriesReader();
  ~vtkITKArchetypeImageSeriesReader();

  char *Archetype;
  int DataExtent[6];

  int OutputScalarType;
  int NumberOfComponents;

  double DefaultDataSpacing[3];
  double DefaultDataOrigin[3];

  int FileNameSliceOffset;
  int FileNameSliceSpacing;
  int FileNameSliceCount;
  
  vtkMatrix4x4* RasToIjkMatrix;

  char UseNativeCoordinateOrientation;
  char UseNativeScalarType;
  bool UseNativeOrigin;

//BTX
  std::vector<std::string> FileNames;
  CoordinateOrientationCode DesiredCoordinateOrientation;
//ETX
  virtual void ExecuteInformation();
  // defined in the subclasses
  virtual void ExecuteData(vtkDataObject *data);

private:
  vtkITKArchetypeImageSeriesReader(const vtkITKArchetypeImageSeriesReader&);  // Not implemented.
  void operator=(const vtkITKArchetypeImageSeriesReader&);  // Not implemented.
};

#endif
