// From MathLink Delaunay qhull interface
// Original header:
/*

  qh-math.c -- MathLink(TM) interface to Qhull's Delaunay Triangulation

  Original work Copyright (c) 1998 by Alban P.M. Tsui <a.tsui@ic.ac.uk>
  Modifications Copyright (c) 2000 by P.J. Hinton <paulh@wolfram.com>

  Author: Alban P.M. Tsui
  Date:   Jan 19, 1998
  Tested: Unix, Windows95

  Revised by P.J. Hinton, July 5, 2000
  Ported: Linux (glibc 2.1), Windows 95, MacOS System 8.6

  Use of this source code implies consent to the license in the file
  COPYING that accompanies this source code archive.

*/

#include "vtkQhullDelaunay3D.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

extern "C"
{
#include "qhull.h"
#include "mem.h"
#include "qset.h"
}

#include "vtkCellArray.h"
#include "vtkCellType.h"
#include "vtkIdList.h"
#include "vtkPoints.h"
#include "vtkSmartPointer.h"
#include "vtkUnstructuredGrid.h"

#define BUF_SIZE 2048
// #define QHULL_COMMAND "qhull d QJ Tv "
#define QHULL_COMMAND "qhull d QJ "

vtkSmartPointer<vtkUnstructuredGrid>
vtkQhullDelaunay3D(vtkPoints *inputPoints)
{
  int     curlong, totlong, exitcode;
  char    options[BUF_SIZE];
  coordT *points;

  facetT * facet;
  vertexT *vertex, * *vertexp;

  vtkSmartPointer<vtkUnstructuredGrid> outMesh
    = vtkSmartPointer<vtkUnstructuredGrid>::New();
  outMesh->SetPoints(inputPoints);

  const unsigned int dim = 3;

  unsigned int numPoints = inputPoints->GetNumberOfPoints();

  /* Allocate memory to store elements of the list */

  points = (coordT *)malloc( ( dim + 1 ) * numPoints * sizeof( coordT ) );
  /* Store each coordinate in an array element. */
  for( unsigned int k = 0; k < numPoints; k++ )
    {
    double x[3];
    inputPoints->GetPoint(k, x);

    long pos = k * ( dim + 1 );

#if 1
    double sumS = 0;
    for( unsigned int j = 0; j < dim; j++ )
      {
      points[pos + j] = x[j];
      sumS += x[j] * x[j];
      }
    points[pos + dim] = sumS;
#else
    points[pos + dim] = 0.0;
#endif
    }

  /* Call out to qhull library to compute DeLaunay triangulation. */
  qh_init_A(stdin, stdout, stderr, 0, NULL);
  exitcode = setjmp(qh errexit);

  if( !exitcode )
    {
    // Add extra options here
    strcpy(options, QHULL_COMMAND);

    qh_initflags(options);
    qh_setdelaunay(dim + 1, numPoints, points);
    qh_init_B(points, numPoints, dim + 1, False);
    qh_qhull();
    qh_check_output();

    /*
        long numfacets = 0;

        FORALLfacets
        {
          if (!facet->upperdelaunay)
          {
            numfacets++;
          }
        }
    */

    FORALLfacets
      {
      if( !facet->upperdelaunay )
        {
        vtkIdType    ptIds[4];
        unsigned int k = 0;
        bool         validCell = true;
        FOREACHvertex_(facet->vertices)
          {
          if( k >= 4 )
            {
            validCell = false;
            break;
            }
          vtkIdType id = qh_pointid(vertex->point);
          if( id < 0 || id >= numPoints )
            {
            validCell = false;
            std::cerr << ">->->- WARNING: qhull attempted to insert point id : " <<  id << " with " << numPoints
                      << "points" << std::endl;
            break;
            }
          ptIds[k++] = id;
          }
        if( !validCell )
          {
          continue;
          }
        outMesh->InsertNextCell(VTK_TETRA, 4, ptIds);
        }
      }
    }

  // Free allocated memory

  qh NOerrexit = True;
  qh_freeqhull(False);
  qh_memfreeshort(&curlong, &totlong);
  free(points);

  if( curlong || totlong )
    {
    fprintf(stderr, "qhull internal warning (main): did not \
      free %d bytes of long memory (%d pieces)\n", totlong, curlong);
    }

  outMesh->BuildLinks();

  return outMesh;
}

