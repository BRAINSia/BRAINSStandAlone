project(qhull_lib)

find_package(VTK)
if(VTK_FOUND)
  include(${USE_VTK_FILE})
else(VTK_FOUND)
  message(FATAL_ERROR "VTK not found. Please set VTK_DIR.")
endif(VTK_FOUND)

include_directories(
  ${VTK_INCLUDE_DIRS}
#  ${CMAKE_CURRENT_SOURCE_DIR}/../basicimg
  ${CMAKE_CURRENT_SOURCE_DIR}/../common
)

add_executable(testqh
  testqh.cxx
  vtkQhullDelaunay3D.cxx
  user.c
  global.c
  stat.c
  io.c
  geom2.c
  poly2.c
  merge.c
  qhull.c
  geom.c
  poly.c
  qset.c
  mem.c
)


target_link_libraries(testqh ${VTK_LIBRARIES})
