#include "vtkQhullDelaunay3D.h"

#include "vtkUnstructuredGridWriter.h"

int main(int argc, char * *argv)
{
  vtkPoints *pts = vtkPoints::New();

  double c = 2.0;
  /*
    for (double x = -c; x <= c; x += 1.0)
      for (double y = -c; y <= c; y += 1.0)
        for (double z = -c; z <= c; z += 1.0)
  */
  for( double x = 0; x <= c; x += 1.0 )
    {
    for( double y = 0; y <= c; y += 1.0 )
      {
      for( double z = 0; z <= c; z += 1.0 )
        {
        double p[3];
        p[0] = x;
        p[1] = y;
        p[2] = z;
        pts->InsertNextPoint(p);
        }
      }
    }

  vtkUnstructuredGrid *mesh = vtkQhullDelaunay3D(pts);

  vtkUnstructuredGridWriter *meshWriter = vtkUnstructuredGridWriter::New();
  meshWriter->SetFileTypeToBinary();
  meshWriter->SetFileName("testqh.vtk");
  meshWriter->SetInput(mesh);
  meshWriter->Update();

  return 0;
}

