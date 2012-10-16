

add_executable(testRandomForest testRandomForest.cxx)
target_link_libraries(testRandomForest ${ITK_LIBRARIES} ${OpenCV_LIBRARIES})
