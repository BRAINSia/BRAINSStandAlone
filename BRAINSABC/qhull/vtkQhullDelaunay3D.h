#ifndef _vtkQhullDelaunay3D_h
#define _vtkQhullDelaunay3D_h

#include "vtkPoints.h"
#include "vtkSmartPointer.h"
#include "vtkUnstructuredGrid.h"

vtkSmartPointer<vtkUnstructuredGrid> vtkQhullDelaunay3D(vtkPoints *inputPoints);

#endif
